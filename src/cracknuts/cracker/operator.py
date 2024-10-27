import socket
import struct
import threading

from cracknuts import logger
from cracknuts.cracker import protocol
from cracknuts.utils import hex_util


class Commands:
    START_SERVER = 0x0001
    STOP_SERVER = 0x0002
    GET_STATUS = 0x0003
    UPDATE_SERVER = 0x0004
    UPDATE_BITSTREAM = 0x0005


class Operator:
    def __init__(self, host, port):
        self._logger = logger.get_logger(self)
        self._socket: socket.socket | None = None
        self._server_address = (host, port)
        self._command_lock = threading.Lock()

    def connect(self):
        """
        Connect to Cracker device.
        :return: Cracker self.
        """
        try:
            if not self._socket:
                self._socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                self._socket.settimeout(5)
            self._socket.connect(self._server_address)
            self._logger.info(f"Connected to cracker operator server: {self._server_address}")
        except OSError as e:
            self._logger.error("Connection failed: %s", e)

    def start_server(self):
        status, res = self.send_and_receive(protocol.build_send_message(Commands.START_SERVER))
        self._logger.debug(f"Receive status: {status} and res: {res}")
        if status != protocol.STATUS_OK:
            self._logger.error(f"Failed to start server: {res}")
            return False
        return True

    def stop_server(self):
        status, res = self.send_and_receive(protocol.build_send_message(Commands.STOP_SERVER))
        if status != protocol.STATUS_OK:
            self._logger.error(f"Failed to stop server: {res}")
            return False
        return True

    def get_status(self):
        status, res = self.send_and_receive(protocol.build_send_message(Commands.GET_STATUS))
        if status != protocol.STATUS_OK:
            return False
        else:
            return struct.unpack(">B", res)[0] == 1

    def update_server(self, file_bytes):
        status, res = self.send_and_receive(protocol.build_send_message(Commands.UPDATE_SERVER, payload=file_bytes))
        if status != protocol.STATUS_OK:
            self._logger.error(f"Failed to update server: {res}")
            return False
        return True

    def update_bitstream(self, file_bytes):
        status, res = self.send_and_receive(protocol.build_send_message(Commands.UPDATE_BITSTREAM, payload=file_bytes))
        if status != protocol.STATUS_OK:
            self._logger.error(f"Failed to update bitstream: {res}")
            return False
        return True

    def send_and_receive(self, message) -> tuple[int, bytes | None]:
        """
        Send message to socket
        :param message:
        :return:
        """
        if self._socket is None:
            self._logger.error("Cracker not connected")
            return protocol.STATUS_ERROR, None
        try:
            self._command_lock.acquire()
            self._logger.debug(f"Send message to {self._server_address}: \n{hex_util.get_bytes_matrix(message)}")
            self._socket.sendall(message)
            resp_header = self._socket.recv(protocol.RES_HEADER_SIZE)
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
                self._logger.debug(
                    f"Receive payload from {self._server_address}: \n{hex_util.get_bytes_matrix(resp_payload)}"
                )
            return status, resp_payload
        except OSError as e:
            self._logger.error("Send message failed: %s, and msg: %s", e, message)
            return protocol.STATUS_ERROR, None
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
