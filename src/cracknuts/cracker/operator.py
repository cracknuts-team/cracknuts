# Copyright 2024 CrackNuts. All rights reserved.

import logging
import socket
import struct
import threading

from cracknuts import logger
from cracknuts.cracker import protocol
from cracknuts.utils import hex_util

from collections import OrderedDict


class Command:
    START_SERVER = 0x0001
    STOP_SERVER = 0x0002
    GET_STATUS = 0x0003
    UPDATE_SERVER = 0x0004
    UPDATE_BITSTREAM = 0x0005

    GET_MODEL = 0x0009
    GET_SN = 0x000A

    GET_VERSION = 0x000B
    GET_SERVER_VERSION = 0x000C
    SET_LED = 0x000D

    GET_IP = 0x0007
    SET_IP = 0x0006


class LedServer(threading.Thread):
    def __init__(self, operator, width=19, height=4, delay=2, gap=2):
        super().__init__(daemon=True)

        self.operator = operator
        self.width = width
        self.height = height
        self.delay = delay
        self.gap = gap

        # key -> {title:str, items:OrderedDict[item_key,str]}
        self._groups = OrderedDict()

        self._lock = threading.Lock()
        self._running = True

        self._update_event = threading.Event()

    def set_groups(self, items):
        """
        items = [(key, title, content)]
        content 可以是 str 或 list[str]
        """
        with self._lock:
            self._groups.clear()

            for key, title, content in items:
                if isinstance(content, str):
                    content = content.splitlines()

                item_dict = OrderedDict()
                for i, line in enumerate(content):
                    item_dict[str(i)] = line

                self._groups[key] = {"title": title, "items": item_dict}

        self._update_event.set()

    def update_group(self, title, content, key=None):
        if key is None:
            key = title.strip().lower()

        if isinstance(content, str):
            content = content.splitlines()

        item_dict = OrderedDict()
        for i, line in enumerate(content):
            item_dict[str(i)] = line

        with self._lock:
            self._groups[key] = {"title": title, "items": item_dict}

        self._update_event.set()

    def update_item(self, title: str, item, key=None, item_key=None):
        if key is None:
            key = title.strip().lower()

        if isinstance(item, list):
            item = " ".join(item)

        if item_key is None:
            item_key = title.strip().lower()

        with self._lock:
            if key not in self._groups:
                self._groups[key] = {"title": title, "items": OrderedDict()}

            group = self._groups[key]
            group["title"] = title
            group["items"][item_key] = item

        self._update_event.set()

    def remove_group(self, key):
        with self._lock:
            if key in self._groups:
                del self._groups[key]

        self._update_event.set()

    def stop(self):
        self._running = False
        self._update_event.set()

    def _wrap_lines(self, content):
        lines = []

        for line in content.splitlines():
            if not line:
                lines.append("")
                continue

            for i in range(0, len(line), self.width):
                lines.append(line[i : i + self.width])

        return lines

    def _build_buffer(self):
        buffer = []

        for group in self._groups.values():
            title = group["title"]
            items = group["items"]

            for text in items.values():
                lines = self._wrap_lines(text)
                lines = [line.ljust(self.width) for line in lines]

                for line in lines:
                    buffer.append((title, line))

            for _ in range(self.gap):
                buffer.append((None, " " * self.width))

        return buffer

    def run(self):
        offset = 0

        while self._running:
            with self._lock:
                buffer = self._build_buffer()

            if not buffer:
                self._update_event.wait(self.delay)
                self._update_event.clear()
                continue

            total = len(buffer)

            # 修改后的滚动判断逻辑
            need_scroll = total - 2 > self.height

            frame_lines = []
            current_title = None

            for i in range(self.height):
                if need_scroll:
                    idx = (offset + i) % total
                else:
                    idx = i if i < total else None

                if idx is None:
                    title, line = None, " " * self.width
                else:
                    title, line = buffer[idx]

                if current_title is None and title is not None:
                    current_title = title

                frame_lines.append(line)

            if current_title is None:
                current_title = ""

            self.operator.update_led_content(title=" " + current_title + " ", content="\n".join(frame_lines))

            triggered = self._update_event.wait(self.delay)
            self._update_event.clear()

            if triggered:
                offset = 0
                continue

            if need_scroll:
                offset = (offset + 1) % total


class Operator:
    """
    Config `Cracker` device daemo process
    """

    NON_PROTOCOL_ERROR = -1
    SOCKET_TIMEOUT_ERROR = -2

    def __init__(self, host: str, port: int = protocol.DEFAULT_OPERATOR_PORT):
        self._logger = logger.get_logger(self)
        self._socket: socket.socket | None = None
        self._server_address = (host, port)
        self._command_lock = threading.Lock()
        self._connection_status = False
        self._ignore_socket_timeout_error = False  # This is used to ignore connection errors after changing the IP.
        self._led_server = LedServer(self)

    def connect(self, connect_timeout: float = 5.0) -> bool:
        """
        Connect to Cracker daemon service.
        """
        if self._socket and self._connection_status:
            self._logger.debug("The operator is already connected and will reuse this session.")
            return True
        else:
            try:
                if not self._socket:
                    self._socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                self._socket.settimeout(connect_timeout)
                self._socket.connect(self._server_address)
                self._logger.info(f"Connected to cracker operator server: {self._server_address}")
                self._connection_status = True
                self._led_server.start()
                self._led_server.update_group("IP", content=self._server_address[0])
                return True
            except OSError as e:
                if not (type(e) is TimeoutError and self._ignore_socket_timeout_error):
                    self._logger.error(f"Connection failed: {e}, and connect_timeout is {connect_timeout}")
                self._connection_status = False
                self._socket = None
                return False

    def disconnect(self):
        try:
            self._led_server.stop()
            if self._socket:
                self._socket.shutdown(socket.SHUT_RDWR)
            self._logger.info(f"Disconnect from {self._server_address}")
        except OSError as e:
            self._logger.error("Disconnection failed: %s", e)
        finally:
            self._socket.close()
            self._socket = None
            self._connection_status = False

    def get_hardware_model(self):
        status, res = self.send_and_receive(protocol.build_send_message(Command.GET_MODEL))
        if status != protocol.STATUS_OK:
            return None
        else:
            if all(b == 0xFF for b in res):
                return "unknown"
            else:
                try:
                    return res.strip(b"\x00").decode("ascii")
                except UnicodeDecodeError:
                    self._logger.error(
                        f"Get hardware_model error: decode error, " f"the original bytes are: {res.hex().upper()}"
                    )
                    return "unknown"

    def get_sn(self):
        status, res = self.send_and_receive(protocol.build_send_message(Command.GET_SN))
        if status != protocol.STATUS_OK:
            return None
        else:
            if all(b == 0xFF for b in res):
                return "unknown"
            else:
                try:
                    return res.strip(b"\x00").decode("ascii")
                except UnicodeDecodeError:
                    self._logger.error(f"Get SN error: decode error, the original bytes are: {res.hex().upper()}")
                    return "unknown"

    def get_version(self):
        status, res = self.send_with_command(Command.GET_VERSION)
        if status != protocol.STATUS_OK:
            return None
        else:
            return res.strip(b"\x00").decode("ascii")

    def get_server_version(self):
        status, res = self.send_with_command(Command.GET_SERVER_VERSION)
        if status != protocol.STATUS_OK:
            return None
        else:
            return res.strip(b"\x00").decode("ascii")

    def get_ip(self):
        status, res = self.send_and_receive(protocol.build_send_message(Command.GET_IP))
        if status != protocol.STATUS_OK:
            return None
        else:
            ip = socket.inet_ntoa(res[0:4])
            mask = socket.inet_ntoa(res[4:8])
            gateway = socket.inet_ntoa(res[8:12])
            return ip, mask, gateway

    def set_ip(self, ip, mask, gateway, ignore_reconnect_check: bool = False) -> bool:
        ip_byte = socket.inet_aton(ip)
        mask_byte = socket.inet_aton(mask)
        gate_byte = socket.inet_aton(gateway)
        self._ignore_socket_timeout_error = True
        if self._socket is None or not self._connection_status:
            self.connect()
        if self._socket is not None:
            self._socket.settimeout(1)
        else:
            return False
        status, res = self.send_and_receive(
            protocol.build_send_message(Command.SET_IP, payload=ip_byte + mask_byte + gate_byte)
        )
        if status != self.SOCKET_TIMEOUT_ERROR:
            self._logger.error(f"Set ip failed: {res}")
            return False
        self._server_address = (ip, protocol.DEFAULT_OPERATOR_PORT)
        self.disconnect()
        if not ignore_reconnect_check:
            try_connect_count = 10
            while try_connect_count > 0:
                if self.connect(connect_timeout=30):
                    break
            self._ignore_socket_timeout_error = False
            return self._connection_status
        else:
            return True

    def start_server(self):
        status, res = self.send_and_receive(protocol.build_send_message(Command.START_SERVER))
        self._logger.debug(f"Receive status: {status} and res: {res}")
        if status != protocol.STATUS_OK:
            self._logger.error(f"Failed to start server: {res}")
            return False
        return True

    def stop_server(self):
        status, res = self.send_and_receive(protocol.build_send_message(Command.STOP_SERVER))
        if status != protocol.STATUS_OK:
            self._logger.error(f"Failed to stop server: {res}")
            return False
        return True

    def get_status(self):
        status, res = self.send_and_receive(protocol.build_send_message(Command.GET_STATUS))
        if status != protocol.STATUS_OK:
            return False
        else:
            return struct.unpack(">B", res)[0] == 1

    def update_server(self, file_bytes):
        status, res = self.send_and_receive(protocol.build_send_message(Command.UPDATE_SERVER, payload=file_bytes))
        if status != protocol.STATUS_OK:
            self._logger.error(f"Failed to update server: {res}")
            return False
        return True

    def update_bitstream(self, file_bytes):
        status, res = self.send_and_receive(protocol.build_send_message(Command.UPDATE_BITSTREAM, payload=file_bytes))
        if status != protocol.STATUS_OK:
            self._logger.error(f"Failed to update bitstream: {res}")
            return False
        return True

    def update_led_content(self, title: str, content: str):
        payload = struct.pack(">B", len(title)) + title.encode() + content.encode()
        status, res = self.send_and_receive(protocol.build_send_message(Command.SET_LED, payload=payload))
        if status != protocol.STATUS_OK:
            self._logger.error(f"Failed to set led: {res}")
            return False
        return True

    def send_and_receive(self, message) -> tuple[int, bytes | None | str]:
        """
        Send message to socket
        :param message:
        :return:
        """
        if self._socket is None or not self._connection_status:
            self.connect()
            # self._logger.error("Operator not connected")
            # return protocol.STATUS_ERROR, None
        try:
            self._command_lock.acquire()
            if self._logger.isEnabledFor(logging.DEBUG):
                self._logger.debug(f"Send message to {self._server_address}: \n{hex_util.get_bytes_matrix(message)}")
            self._socket.sendall(message)
            resp_header = self._socket.recv(protocol.RES_HEADER_SIZE)
            if self._logger.isEnabledFor(logging.DEBUG):
                self._logger.debug(
                    "Get response header from %s: \n%s",
                    self._server_address,
                    hex_util.get_bytes_matrix(resp_header),
                )
            magic, version, direction, status, length = struct.unpack(protocol.RES_HEADER_FORMAT, resp_header)
            self._logger.debug(
                f"Receive header from {self._server_address}: {magic}, {version}, {direction}, {status:02X}, {length}"
            )
            if status >= protocol.STATUS_ERROR:
                self._logger.error(f"Receive status error: {status:02X}")
            if length == 0:
                return status, None
            resp_payload = self._recv(length)
            if status >= protocol.STATUS_ERROR:
                self._logger.error(
                    f"Receive payload from {self._server_address}: \n{hex_util.get_bytes_matrix(resp_payload)}"
                )
            else:
                if self._logger.isEnabledFor(logging.DEBUG):
                    self._logger.debug(
                        f"Receive payload from {self._server_address}: \n{hex_util.get_bytes_matrix(resp_payload)}"
                    )
            return status, resp_payload
        except OSError as e:
            if self._ignore_socket_timeout_error:
                if type(e) is TimeoutError:
                    return self.SOCKET_TIMEOUT_ERROR, str(e.args)
                else:
                    self._logger.error(f"Send message failed: {e}, and msg: {message}", e, message)
                    return self.NON_PROTOCOL_ERROR, str(e.args)
            else:
                self._logger.error(f"Send message failed: {e}, and msg: {message}", e, message)
                return self.NON_PROTOCOL_ERROR, str(e.args)
        finally:
            self._command_lock.release()

    def _recv(self, length):
        resp_payload = b""
        while (received_len := len(resp_payload)) < length:
            for_receive_len = length - received_len
            resp_payload += self._socket.recv(for_receive_len)

        return resp_payload

    def send_with_command(
        self, command: int, rfu: int = 0, payload: str | bytes | None = None
    ) -> tuple[int, bytes | None]:
        if isinstance(payload, str):
            payload = bytes.fromhex(payload)
        return self.send_and_receive(protocol.build_send_message(command, rfu, payload))

    def get_led_server(self):
        return self._led_server
