# Copyright 2024 CrackNuts. All rights reserved.

import io
import os
import shlex
import threading
from collections.abc import Callable, Generator

import paramiko

from cracknuts import logger


class SSHClient:
    """SSH client wrapper for remote command execution and file transfer.

    Supports:

    - Configuration via ``ip``, ``port``, ``username``, and ``private_key``.
    - Private key as a file path or PEM-encoded string.
    - Streaming output during command execution via :meth:`exec`.
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
        """Initialise the SSH client without connecting.

        :param ip: Target host IP address or hostname.
        :param username: SSH username.
        :param private_key: Path to a private key file, or a PEM-encoded key string.
            Mutually exclusive with ``password``.
        :param password: SSH password. Mutually exclusive with ``private_key``.
        :param port: SSH port. Defaults to ``22``.
        :param timeout: Connection timeout in seconds. Defaults to ``10.0``.
        :param encoding: Command output encoding. Defaults to ``"utf-8"``.
        :raises ValueError: If neither or both ``private_key`` and ``password`` are provided.
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

    def _load_private_key(self) -> paramiko.PKey:
        """Load the private key from a file path or PEM string.

        Automatically detects whether the key is stored in a file or provided
        as a string, then parses it into a :class:`paramiko.PKey` object.
        Supports OpenSSH, RSA, ECDSA, and Ed25519 key formats.

        :return: Loaded private key object, or ``None`` if the format is unrecognized.
        :rtype: paramiko.PKey
        """
        key_str = self.private_key.strip()

        # Check if it's a file path (no newlines and file exists)
        import os

        if "\n" not in key_str and os.path.isfile(key_str):
            with open(key_str) as f:
                key_str = f.read().strip()

        key_file = io.StringIO(key_str)

        # Try key types in order
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

    def connect(self) -> "SSHClient":
        """Establish an SSH connection.

        :return: The current instance for method chaining.
        :rtype: SSHClient
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

    def disconnect(self) -> None:
        """Close the SSH connection and release resources."""
        if self._client:
            self._client.close()
            self._client = None

    def is_connected(self) -> bool:
        """Check if the SSH connection is still active.

        :return: ``True`` if connected, ``False`` otherwise.
        :rtype: bool
        """
        if self._client is None:
            return False
        transport = self._client.get_transport()
        return transport is not None and transport.is_active()

    def __enter__(self) -> "SSHClient":
        return self.connect()

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.disconnect()

    def exec(
        self,
        command: str,
        timeout: float | None = None,
        on_stdout: Callable[[str], None] | None = None,
        on_stderr: Callable[[str], None] | None = None,
        print_output: bool = True,
    ) -> dict | None:
        """Execute a command on the remote host with streaming output.

        :param command: Shell command to execute.
        :param timeout: Command execution timeout in seconds. ``None`` for no timeout.
        :param on_stdout: Optional callback invoked for each line of stdout.
        :param on_stderr: Optional callback invoked for each line of stderr.
        :param print_output: If ``True``, automatically print output to the console.
            Defaults to ``True``.
        :return: A dictionary with keys ``stdout``, ``stderr``, and ``exit_code`` if
            ``print_output`` is ``False``; otherwise ``None``.
        :rtype: dict | None
        """
        if not self.is_connected():
            self._logger.error("SSH is not connected. Call connect() or use the context manager first.")
            return None

        stdout_lines = []
        stderr_lines = []

        # Open a dedicated channel for finer-grained control than `exec_command`.
        transport = self._client.get_transport()
        channel = transport.open_session()
        if timeout is not None:
            channel.settimeout(timeout)
        channel.exec_command(command)

        # Stream stdout / stderr in real time
        def _read_stream(stream, collector: list, label: str, callback):
            """Read stream line by line in a separate thread."""
            for raw_line in stream:
                try:
                    line = raw_line.decode(self.encoding, errors="replace")
                except AttributeError:
                    line = raw_line  # Already a str (some paramiko versions)
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
        """Generator-based version: yield stdout lines one by one (stderr excluded).

        Example::

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
        """Upload a local file to the remote host and execute it.

        :param local_path: Path to the local file.
        :param remote_path: Destination path on the remote host.
        :param timeout: Command execution timeout in seconds. None for no timeout.
        :param on_stdout: Optional callback invoked for each line of stdout.
        :param on_stderr: Optional callback invoked for each line of stderr.
        :param print_output: If True, automatically print output to the console.
            Defaults to True.
        :param make_executable: If True, add execute permission via chmod +x.
            Defaults to True.
        :param exec_command: Custom command to execute. None uses remote_path directly.
        :return: A dictionary with keys stdout, stderr, and exit_code if
            print_output is False; otherwise None.
        :rtype: dict | None
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


class _SSHCracker(SSHClient):
    """
    Internal SSH client specialised for CrackNuts devices.

    Subclasses :class:`SSHClient` with a pre-configured username and embedded
    private key, removing the need for callers to supply credentials.
    Not part of the public API.
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
        Initialise the client without connecting.

        :param ip:       Target host IP address or hostname.
        :param port:     SSH port. Defaults to 22.
        :param timeout:  Connection timeout in seconds. Defaults to 10.
        :param encoding: Command output encoding. Defaults to ``"utf-8"``.
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
