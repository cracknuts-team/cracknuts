# Copyright 2024 CrackNuts. All rights reserved.

import io
import os
import shlex
import threading
from collections.abc import Callable, Generator

import paramiko


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
        if private_key is None and password is None:
            raise ValueError("必须提供 private_key 或 password 之一")
        if private_key is not None and password is not None:
            raise ValueError("private_key 和 password 只能选择其中一种认证方式")

        self.ip = ip
        self.port = port
        self.username = username
        self.private_key = private_key
        self.password = password
        self.timeout = timeout
        self.encoding = encoding

        self._client: paramiko.SSHClient | None = None

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

        raise ValueError(f"无法识别私钥格式，请检查私钥内容。最后错误: {last_exc}")

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
            raise RuntimeError("SSH 未连接，请先调用 connect() 或使用 with 语句")

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
            raise RuntimeError("SSH 未连接，请先调用 connect()")

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
        通过 SFTP 上传本地文件到远程主机。

        :param local_path:  本地文件路径
        :param remote_path: 远程目标路径
        """
        if not self.is_connected():
            raise RuntimeError("SSH 未连接，请先调用 connect() 或使用 with 语句")
        if not os.path.isfile(local_path):
            raise FileNotFoundError(f"本地文件不存在: {local_path}")

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
            raise RuntimeError("SSH 未连接，请先调用 connect() 或使用 with 语句")
        if not os.path.isfile(local_path):
            raise FileNotFoundError(f"本地文件不存在: {local_path}")

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
