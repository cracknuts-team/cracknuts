import socket
import struct
import sys
import time

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
        self._handler_dict = {}
        self._server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self._server_socket.bind(("", protocol.DEFAULT_PORT))
        self._server_socket.listen()
        self._logger.debug("MockCracker initialized")
        self._start_server()

    def _start_server(self):
        while True:
            time.sleep(0.01)
            try:
                conn, addr = self._server_socket.accept()
                self._logger.debug(f"Get client request from {addr}.")

                while True:
                    time.sleep(0.01)
                    try:
                        header_data = conn.recv(protocol.RESP_HEADER_SIZE)
                        if not header_data:
                            continue
                        magic, version, direction, command, rfu, length = struct.unpack(
                            protocol.REQ_HEADER_FORMAT, header_data
                        )
                        self._logger.debug(
                            f"Received header: Magic={magic}, Version={version}, Direction={direction}, "
                            f"Command={command}, Length={length}"
                        )

                        payload_data = conn.recv(length)

                        self._logger.debug(f"Received payload length: {len(payload_data)}")
                        self._logger.debug(f"Received payload\n: {hex_util.get_bytes_matrix(payload_data)}")

                        self._handler_dict.get(command, None)(self, payload=payload_data)
                    except OSError as e:
                        self._logger.error(e.args)
                        conn.sendall(f"Error: {e.args[0]}".encode())
                        continue
                    except struct.error as e:
                        self._logger.error(e)
                        conn.sendall(f"Format error: {e.args[0]}\n".encode())
                        continue
                    except KeyboardInterrupt:
                        sys.exit(0)
            except KeyboardInterrupt:
                print(111111)
                sys.exit(0)

    @_handler(cracker.Commands.GET_ID, has_payload=False)
    def get_id(self, payload: bytes) -> bytes:
        return b"mock_001"
