import logging
import time

import numpy as np
import socket
import struct
import sys
import threading

from cracknuts import logger
from cracknuts.cracker import protocol, cracker
from cracknuts.utils import hex_util

_handler_dict = {}


def _handler(command: int, has_payload: bool = True):
    def decorator(func):
        def wrapper(*args, **kwargs):
            if not has_payload:
                del kwargs["payload"]
            return func(*args, **kwargs)

        _handler_dict[command] = wrapper
        return wrapper

    return decorator


class MockCracker:
    def __init__(self):
        self._logger = logger.get_logger(MockCracker)
        self._server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self._server_socket.settimeout(1)
        self._server_socket.bind(("", protocol.DEFAULT_PORT))
        self._server_socket.listen()
        self._logger.debug("MockCracker initialized")

    def start(self):
        try:
            self._start_accept()
        except KeyboardInterrupt:
            sys.exit(0)

    def _start_accept(self):
        while True:
            try:
                conn, addr = self._server_socket.accept()
                conn.settimeout(5)
                self._logger.debug(f"Get client request from {addr}.")
                threading.Thread(target=self._handle, args=(conn,), daemon=True).start()
                # self._handle(conn)
            except TimeoutError:
                continue
            except KeyboardInterrupt:
                self._logger.debug("exist by keyboard interrupt.")
                sys.exit(0)

    def _handle(self, conn):
        while True:
            try:
                header_data = conn.recv(protocol.REQ_HEADER_SIZE)
                if not header_data:
                    self._logger.debug("disconnected...")
                    break

                self._logger.debug(f"Received header:\n{hex_util.get_bytes_matrix(header_data)}")

                try:
                    magic, version, direction, command, rfu, length = struct.unpack(
                        protocol.REQ_HEADER_FORMAT, header_data
                    )
                except struct.error as e:
                    err_msg = f"Message format error: {e.args[0]}\n"
                    self._logger.error(err_msg)
                    err_res = self._error(f"Header format error: {hex_util.get_hex(header_data)}")
                    self._logger.debug(f"Send error:\n{hex_util.get_bytes_matrix(err_res)}")
                    conn.sendall(err_res)
                    continue

                self._logger.debug(
                    f"Received header: Magic={magic}, Version={version}, Direction={direction}, "
                    f"Command={command}, Length={length}"
                )

                payload_data = conn.recv(length)
                if len(payload_data) > 0:
                    self._logger.debug(f"Received payload:\n{hex_util.get_bytes_matrix(payload_data)}")
                if command not in _handler_dict:
                    self._logger.warning(f'Get command not supported: 0x{format(command, '04x')}')
                    self._logger.error(_handler_dict)
                    unsupported_res = self._unsupported(command)
                    self._logger.debug(f"Send unsupported:\n{hex_util.get_bytes_matrix(unsupported_res)}")
                    conn.sendall(unsupported_res)
                    continue
                res_payload = _handler_dict.get(command, None)(self, payload=payload_data)
                res = protocol.build_response_message(protocol.STATUS_OK, res_payload)
                self._logger.debug(f"Sending:\n{hex_util.get_bytes_matrix(res)}")
                conn.sendall(res)
            except TimeoutError:
                continue
            except ConnectionResetError:
                break
            except Exception as e:
                self._logger.error(e)
                raise e

    @staticmethod
    def _error(error: str) -> bytes:
        return protocol.build_response_message(protocol.STATUS_ERROR, error.encode())

    @staticmethod
    def _unsupported(command):
        return protocol.build_response_message(
            protocol.STATUS_UNSUPPORTED, f'Command [0x{format(command, '04x')}] not supported'.encode()
        )

    @_handler(cracker.Commands.GET_ID, has_payload=False)
    def get_id(self) -> bytes:
        return b"mock_001"

    @_handler(cracker.Commands.GET_NAME, has_payload=False)
    def get_name(self) -> bytes:
        return b"MOCK 001"

    @_handler(cracker.Commands.GET_VERSION, has_payload=False)
    def get_version(self) -> bytes:
        return b"0.1.0(adc:0.1.0,hardware:0.1.0)"

    @_handler(cracker.Commands.SCRAT_GET_ANALOG_WAVES)
    def scrat_get_analog_wave(self, payload: bytes) -> bytes:
        time.sleep(0.05)  # Simulate device I/O operations.
        channel, offset, sample_count = struct.unpack(">BII", payload)
        return struct.pack(f">{sample_count}h", *np.random.randint(-100, 100, size=sample_count).tolist())

    @_handler(cracker.Commands.SCRAT_IS_TRIGGERED)
    def scrat_is_trigger(self, payload: bytes) -> bytes:
        time.sleep(0.05)  # Simulate device I/O operations.
        return struct.pack(">?", True)


if __name__ == "__main__":
    mock_cracker = MockCracker()
    logger.set_level(logging.DEBUG, mock_cracker)
    mock_cracker.start()
