# Copyright 2024 CrackNuts. All rights reserved.

import io
import os
import shlex
import threading
from collections.abc import Callable, Generator

import paramiko

from cracknuts import logger


__SSH_PRIVATE_KEY = """-----BEGIN OPENSSH PRIVATE KEY-----
b3BlbnNzaC1rZXktdjEAAAAABG5vbmUAAAAEbm9uZQAAAAAAAAABAAAAMwAAAAtzc2gtZW
QyNTUxOQAAACAE6LmHiknXfqM5ee5FSVr091gRm9nv55p46K1EKWwyDQAAAKDq5Kma6uSp
mgAAAAtzc2gtZWQyNTUxOQAAACAE6LmHiknXfqM5ee5FSVr091gRm9nv55p46K1EKWwyDQ
AAAEDYTZLDl1AqFeJCYr5UQkGgLxE/ACHUBC6oQLSDZzaIyQTouYeKSdd+ozl57kVJWvT3
WBGb2e/nmnjorUQpbDINAAAAGWNyYWNrZXJBZG1pbkBjcmFja251dHMuaW8BAgME
-----END OPENSSH PRIVATE KEY-----"""


class SSHClient:
    """
    SSH 客户端封装类

    支持：
    - ip / port / username / private_key 配置
    - private_key 可以是文件路径，也可以是 PEM 格式的字符串
    - exec() 执行命令并实时流式输出结果
    """

    def __init__(
        self,
        ip: str,
        username: str,
        private_key: str | None = None,
        password: str | None = None,
        port: int = 22,
        timeout: float = 10.0,
        encoding: str = "utf-8",
    ):
        """
        初始化 SSH 客户端（不立即连接）

        :param ip:          目标主机 IP 或主机名
        :param username:    SSH 用户名
        :param private_key: 私钥文件路径，或 -----BEGIN OPENSSH PRIVATE KEY----- 格式的字符串（与 password 二选一）
        :param password:    SSH 密码（与 private_key 二选一）
        :param port:        SSH 端口，默认 22
        :param timeout:     连接超时时间（秒），默认 10
        :param encoding:    命令输出编码，默认 utf-8
        """
        self.ip = ip
        self.port = port
        self.username = username
        self.private_key = private_key
        self.password = password
        self.timeout = timeout
        self.encoding = encoding
        self._client: paramiko.SSHClient | None = None
        self._logger = logger.get_logger(self)

        if private_key is None and password is None:
            raise ValueError("Either private_key or password must be provided.")
        if private_key is not None and password is not None:
            raise ValueError("Only one of private_key or password can be specified.")

    # ------------------------------------------------------------------
    # 私钥加载
    # ------------------------------------------------------------------

    def _load_private_key(self) -> paramiko.PKey:
        """
        自动识别私钥来源（文件路径 or 字符串），并加载为 PKey 对象。
        支持 OpenSSH / RSA / DSS / ECDSA / Ed25519 格式。
        """
        key_str = self.private_key.strip()

        # 判断是否为文件路径（不含换行且文件存在）
        import os

        if "\n" not in key_str and os.path.isfile(key_str):
            with open(key_str) as f:
                key_str = f.read().strip()

        key_file = io.StringIO(key_str)

        # 按顺序尝试各种密钥类型
        key_classes = [
            paramiko.Ed25519Key,
            paramiko.ECDSAKey,
            paramiko.RSAKey,
        ]

        last_exc = None
        for key_class in key_classes:
            key_file.seek(0)
            try:
                return key_class.from_private_key(key_file)
            except Exception as e:
                last_exc = e
                continue

        self._logger.error(f"Unrecognized private key format. Last error: {last_exc}")
        return None

    # ------------------------------------------------------------------
    # 连接 / 断开
    # ------------------------------------------------------------------

    def connect(self) -> "SSHClient":
        """
        建立 SSH 连接，返回 self 以支持链式调用。
        """
        client = paramiko.SSHClient()
        client.set_missing_host_key_policy(paramiko.AutoAddPolicy())

        if self.private_key is not None:
            pkey = self._load_private_key()
            if pkey is None:
                return self
            client.connect(
                hostname=self.ip,
                port=self.port,
                username=self.username,
                pkey=pkey,
                password=None,
                timeout=self.timeout,
                look_for_keys=False,
                allow_agent=False,
            )
        else:
            client.connect(
                hostname=self.ip,
                port=self.port,
                username=self.username,
                password=self.password,
                timeout=self.timeout,
                look_for_keys=False,
                allow_agent=False,
            )

        self._client = client
        return self

    def disconnect(self):
        """断开 SSH 连接"""
        if self._client:
            self._client.close()
            self._client = None

    def is_connected(self) -> bool:
        """检查连接是否仍然活跃"""
        if self._client is None:
            return False
        transport = self._client.get_transport()
        return transport is not None and transport.is_active()

    # ------------------------------------------------------------------
    # 上下文管理器
    # ------------------------------------------------------------------

    def __enter__(self) -> "SSHClient":
        return self.connect()

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.disconnect()

    # ------------------------------------------------------------------
    # 执行命令
    # ------------------------------------------------------------------

    def exec(
        self,
        command: str,
        timeout: float | None = None,
        on_stdout: Callable[[str], None] | None = None,
        on_stderr: Callable[[str], None] | None = None,
        print_output: bool = True,
    ) -> dict | None:
        """
        在远程主机上执行命令，实时流式输出结果。

        :param command:     要执行的 Shell 命令
        :param timeout:     命令执行超时（秒），None 表示不限制
        :param on_stdout:   stdout 每行回调函数（可选）
        :param on_stderr:   stderr 每行回调函数（可选）
        :param print_output: 是否自动打印到控制台，默认 True
        :return: {
                    "stdout": str,   # 完整标准输出
                    "stderr": str,   # 完整错误输出
                    "exit_code": int # 退出码
                 }| None（如果 print_output=True 则不返回输出内容）
        """
        if not self.is_connected():
            self._logger.error("SSH is not connected. Call connect() or use the context manager first.")
            return None

        stdout_lines = []
        stderr_lines = []

        # 打开独立 channel（比 exec_command 更可控）
        transport = self._client.get_transport()
        channel = transport.open_session()
        if timeout is not None:
            channel.settimeout(timeout)
        channel.exec_command(command)

        # 实时读取 stdout / stderr
        def _read_stream(stream, collector: list, label: str, callback):
            """在独立线程中逐行读取流"""
            for raw_line in stream:
                try:
                    line = raw_line.decode(self.encoding, errors="replace")
                except AttributeError:
                    line = raw_line  # 已经是 str（paramiko 某些版本）
                collector.append(line)
                if print_output:
                    print(line, end="", flush=True)
                if callback:
                    callback(line)

        stdout_thread = threading.Thread(
            target=_read_stream,
            args=(channel.makefile("r"), stdout_lines, "STDOUT", on_stdout),
            daemon=True,
        )
        stderr_thread = threading.Thread(
            target=_read_stream,
            args=(channel.makefile_stderr("r"), stderr_lines, "STDERR", on_stderr),
            daemon=True,
        )

        stdout_thread.start()
        stderr_thread.start()

        stdout_thread.join(timeout=timeout)
        stderr_thread.join(timeout=timeout)

        exit_code = channel.recv_exit_status()
        channel.close()

        if not print_output:
            return {
                "stdout": "".join(stdout_lines),
                "stderr": "".join(stderr_lines),
                "exit_code": exit_code,
            }
        else:
            return None

    def exec_iter(self, command: str) -> Generator[str, None, None]:
        """
        生成器版本：逐行 yield stdout 输出（不含 stderr）。

        示例：
            for line in client.exec_iter("tail -f /var/log/syslog"):
                print(line, end="")
        """
        if not self.is_connected():
            self._logger.error("SSH is not connected. Call connect() first.")
            return

        transport = self._client.get_transport()
        channel = transport.open_session()
        channel.exec_command(command)

        stdout = channel.makefile("r")
        for raw_line in stdout:
            try:
                yield raw_line.decode(self.encoding, errors="replace")
            except AttributeError:
                yield raw_line

        channel.close()

    def upload(
        self,
        local_path: str,
        remote_path: str,
    ) -> None:
        """
        Upload a local file to the remote host via SFTP.

        :param local_path: Local path of the file to upload.
        :type local_path: str
        :param remote_path: Destination path on the remote host.
        :type remote_path: str
        :raises RuntimeError: If the SSH connection is not established.
        :raises FileNotFoundError: If ``local_path`` does not exist or is not a file.
        """
        if not self.is_connected():
            self._logger.error("SSH is not connected. Call connect() or use the context manager first.")
            return
        if not os.path.isfile(local_path):
            self._logger.error(f"Local file not found: {local_path}")
            return

        sftp = self._client.open_sftp()
        try:
            sftp.put(local_path, remote_path)
        finally:
            sftp.close()

    def upload_and_exec(
        self,
        local_path: str,
        remote_path: str,
        timeout: float | None = None,
        on_stdout: Callable[[str], None] | None = None,
        on_stderr: Callable[[str], None] | None = None,
        print_output: bool = True,
        make_executable: bool = True,
        exec_command: str | None = None,
    ) -> dict:
        """
        上传本地文件到远程主机并执行。

        :param local_path:      本地文件路径
        :param remote_path:     远程目标路径
        :param timeout:         命令执行超时（秒），None 表示不限制
        :param on_stdout:       stdout 每行回调函数（可选）
        :param on_stderr:       stderr 每行回调函数（可选）
        :param print_output:    是否自动打印输出
        :param make_executable: 是否添加执行权限 `chmod +x`
        :param exec_command:    自定义执行命令，None 时使用 `remote_path`
        """
        if not self.is_connected():
            self._logger.error("SSH is not connected. Call connect() or use the context manager first.")
            return None
        if not os.path.isfile(local_path):
            self._logger.error(f"Local file not found: {local_path}")
            return None

        self.upload(local_path, remote_path)

        if make_executable:
            self.exec(f"chmod +x {shlex.quote(remote_path)}", print_output=False)

        command = exec_command if exec_command is not None else shlex.quote(remote_path)
        return self.exec(
            command,
            timeout=timeout,
            on_stdout=on_stdout,
            on_stderr=on_stderr,
            print_output=print_output,
        )


class SSHCracker(SSHClient):
    """
    SSHCracker 是 SSHClient 的子类，专门用于 CrackNuts 设备的 SSH 连接和命令执行。
    他默认配置了用户名和私钥，简化了连接过程。
    """

    _PRIVATE_KEY = """-----BEGIN OPENSSH PRIVATE KEY-----
b3BlbnNzaC1rZXktdjEAAAAABG5vbmUAAAAEbm9uZQAAAAAAAAABAAAAMwAAAAtzc2gtZW
QyNTUxOQAAACAE6LmHiknXfqM5ee5FSVr091gRm9nv55p46K1EKWwyDQAAAKDq5Kma6uSp
mgAAAAtzc2gtZWQyNTUxOQAAACAE6LmHiknXfqM5ee5FSVr091gRm9nv55p46K1EKWwyDQ
AAAEDYTZLDl1AqFeJCYr5UQkGgLxE/ACHUBC6oQLSDZzaIyQTouYeKSdd+ozl57kVJWvT3
WBGb2e/nmnjorUQpbDINAAAAGWNyYWNrZXJBZG1pbkBjcmFja251dHMuaW8BAgME
-----END OPENSSH PRIVATE KEY-----"""

    _MTD_DEVICE = "/dev/mtd3"
    _SERVER_REMOTE_PATH = "/tmp/server"
    _BITSTREAM_REMOTE_PATH = "/tmp/bitstream.bit.bin"

    def __init__(
        self,
        ip: str,
        port: int = 22,
        timeout: float = 10.0,
        encoding: str = "utf-8",
    ):
        """
        初始化 SSHCracker（不立即连接）

        :param ip:          目标主机 IP 或主机名
        :param port:        SSH 端口，默认 22
        :param timeout:     连接超时时间（秒），默认 10
        :param encoding:    命令输出编码，默认 utf-8
        """
        super().__init__(
            ip=ip,
            username="root",
            private_key=self._PRIVATE_KEY,
            port=port,
            timeout=timeout,
            encoding=encoding,
        )

    def _ensure_connected(self) -> None:
        if not self.is_connected():
            self.connect()

    def get_hardware_model(self) -> str | None:
        """
        Read the hardware model string from the device via mtd_debug.

        :return: Hardware model string, ``"unknown"`` if the value is empty, or ``None`` on failure.
        :rtype: str | None
        """
        self._ensure_connected()
        result = self.exec(
            f"mtd_debug read {self._MTD_DEVICE} 0x20 32 /tmp/hw_model > /dev/null 2>&1 && strings /tmp/hw_model",
            print_output=False,
        )
        if result and result["exit_code"] == 0:
            return result["stdout"].strip() or "unknown"
        return None

    def get_sn(self) -> str | None:
        """
        Read the device serial number from the device via mtd_debug.

        :return: Serial number string, ``"unknown"`` if the value is empty, or ``None`` on failure.
        :rtype: str | None
        """
        self._ensure_connected()
        result = self.exec(
            f"mtd_debug read {self._MTD_DEVICE} 0x40 32 /tmp/sn > /dev/null 2>&1 && strings /tmp/sn",
            print_output=False,
        )
        if result and result["exit_code"] == 0:
            return result["stdout"].strip() or "unknown"
        return None

    def get_server_status(self) -> bool:
        """
        Check whether the server process is currently running.

        :return: ``True`` if the server process is found, ``False`` otherwise.
        :rtype: bool
        """
        try:
            self._ensure_connected()
        except Exception:
            return False
        result = self.exec("pgrep -x server", print_output=False)
        return result is not None and result["exit_code"] == 0

    def start_server(self) -> bool:
        """
        Start the server process as a detached daemon via setsid.

        Uses ``setsid`` to create a new session so the process is fully
        detached from the SSH channel and survives after the channel closes.
        Waits 1 second on the Python side, then verifies the process is
        running via :meth:`get_server_status`.

        :return: ``True`` if the server process is confirmed running, ``False`` otherwise.
        :rtype: bool
        """
        import time
        self._ensure_connected()
        result = self.exec(
            f"setsid {self._SERVER_REMOTE_PATH} > /tmp/server.log 2>&1 &",
            print_output=False,
        )
        if result is None or result["exit_code"] != 0:
            return False
        time.sleep(1)
        return self.get_server_status()

    def stop_server(self) -> bool:
        """
        Stop the server process and confirm it has exited.

        Sends SIGTERM and waits up to 5 seconds for a graceful shutdown.
        If the process is still alive, SIGKILL is sent to force termination.

        :return: ``True`` if the process is confirmed stopped, ``False`` otherwise.
        :rtype: bool
        """
        self._ensure_connected()
        import time
        s = time.time()
        result = self.exec(
            "killall -w -t 5 server 2>/dev/null; killall -9 server 2>/dev/null; sleep 0.5; ! pgrep -x server",
            print_output=False,
        )
        return result is not None and result["exit_code"] == 0

    def update_server(self, local_path: str) -> bool:
        """
        Upload the server binary to the device and start it.

        Stops any running server instance first, uploads the file via SFTP
        to :attr:`_SERVER_REMOTE_PATH`, then calls :meth:`start_server`.

        :param local_path: Local path to the server binary file.
        :type local_path: str
        :return: ``True`` if the server started successfully, ``False`` otherwise.
        :rtype: bool
        """
        self._ensure_connected()
        self.stop_server()
        self.upload(local_path, self._SERVER_REMOTE_PATH)
        self.exec(f"chmod +x {self._SERVER_REMOTE_PATH}", print_output=False)
        return self.start_server()

    def update_bitstream(self, local_path: str) -> bool:
        """
        Upload the bitstream file to the device and program it into the FPGA.

        Uploads the file via SFTP to :attr:`_BITSTREAM_REMOTE_PATH`, then
        executes ``fpgautil -b <path>`` to program the FPGA.

        :param local_path: Local path to the bitstream file.
        :type local_path: str
        :return: ``True`` if fpgautil exited successfully, ``False`` otherwise.
        :rtype: bool
        """
        self._ensure_connected()
        import time
        s = time.time()
        self.upload(local_path, self._BITSTREAM_REMOTE_PATH)
        result = self.exec(
            f"fpgautil -b {self._BITSTREAM_REMOTE_PATH}",
            print_output=False,
        )
        return result is not None and result["exit_code"] == 0

    def get_server_version(self) -> str | None:
        """
        Retrieve the server version string by running ``/tmp/server --version``.

        :return: Version string from stdout, or ``None`` on failure.
        :rtype: str | None
        """
        self._ensure_connected()
        result = self.exec(f"{self._SERVER_REMOTE_PATH} --version", print_output=False)
        if result and result["exit_code"] == 0:
            return result["stdout"].strip()
        return None
