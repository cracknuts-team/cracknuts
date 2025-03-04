# Copyright 2024 CrackNuts. All rights reserved.

import logging
import os
import socket
import struct
import sys
import threading
import time

import numpy as np

from cracknuts import logger
from cracknuts.cracker import protocol
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
    def __init__(self, host: str = "127.0.0.1", port: int = protocol.DEFAULT_PORT, logging_level=logging.INFO):
        self._running = False
        self._logger = logger.get_logger(MockCracker, logging_level)
        self._server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self._server_socket.settimeout(1)
        self._server_socket.bind((host, port))
        self._server_socket.listen()
        self._logger.debug("MockCracker initialized")
        self._command_payload_cache = {}

    def start(self):
        try:
            self._running = True
            self._start_accept()
        except KeyboardInterrupt:
            self._logger.debug("exist by keyboard interrupt.")
            sys.exit(0)

    def stop(self):
        self._running = False

    def _start_accept(self):
        while self._running:
            try:
                conn, addr = self._server_socket.accept()
                conn.settimeout(5)
                self._logger.debug(f"Get client request from {addr}.")
                threading.Thread(target=self._handle, args=(conn,), daemon=True).start()
                # self._handle(conn)
            except TimeoutError:
                continue

    def _handle(self, conn):
        while self._running:
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

                self._logger.info(f"Received command: 0x{command:02X}")
                self._logger.debug(
                    f"Received header: Magic={magic}, Version={version}, Direction={direction}, "
                    f"Command={command}, Length={length}"
                )

                payload_data = conn.recv(length)
                self._command_payload_cache[command] = payload_data

                if len(payload_data) > 0:
                    if self._logger.isEnabledFor(logging.INFO):
                        self._logger.info(f"Received payload: {hex_util.get_hex(payload_data)}")
                    if self._logger.isEnabledFor(logging.DEBUG):
                        self._logger.debug(f"Received payload:\n{hex_util.get_bytes_matrix(payload_data)}")
                if command not in _handler_dict:
                    self._logger.warning(f'Get command not supported: 0x{format(command, '04x')}')
                    unsupported_res = self._unsupported(command)
                    self._logger.debug(f"Send unsupported:\n{hex_util.get_bytes_matrix(unsupported_res)}")
                    conn.sendall(unsupported_res)
                    continue
                func_res = _handler_dict.get(command, None)(self, payload=payload_data)
                if type(func_res) is tuple:
                    status, res_payload = func_res
                else:
                    status, res_payload = protocol.STATUS_OK, func_res
                res = protocol.build_response_message(status, res_payload)
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
            protocol.STATUS_OK, f'Command [0x{format(command, '04x')}] not supported'.encode()
        )

    @_handler(protocol.Command.GET_ID, has_payload=False)
    def get_id(self) -> bytes:
        return b"mock_001"

    @_handler(protocol.Command.GET_NAME, has_payload=False)
    def get_name(self) -> bytes:
        return b"MOCK 001"

    @_handler(protocol.Command.GET_VERSION, has_payload=False)
    def get_version(self) -> bytes:
        return b"0.1.0(adc:0.1.0,hardware:0.1.0)"

    @_handler(protocol.Command.OSC_GET_ANALOG_WAVES)
    def osc_get_analog_wave(self, payload: bytes) -> bytes:
        channel, offset, sample_count = struct.unpack(">BII", payload)
        if channel == 1:
            mn, mx = -26, -1
        elif channel == 2:
            mn, mx = 0, 25
        else:
            mn, mx = -1, 1
        # mn, mx = -50, 50
        return struct.pack(f"<{sample_count}h", *np.random.randint(mn, mx, size=sample_count).tolist())

    @_handler(protocol.Command.OSC_IS_TRIGGERED)
    def osc_is_trigger(self, payload: bytes) -> tuple[int, bytes | None]:
        time.sleep(0.05)  # Simulate device I/O operations.
        return protocol.STATUS_OK, int.to_bytes(4, 4, "big")

    @_handler(protocol.Command.OSC_FORCE, has_payload=False)
    def osc_force(self) -> bytes: ...  # type: ignore

    @_handler(protocol.Command.OSC_SINGLE, has_payload=False)
    def osc_arm(self) -> bytes: ...  # type: ignore

    @_handler(protocol.Command.NUT_VOLTAGE, has_payload=False)
    def nut_voltage(self) -> bytes: ...  # type: ignore

    @_handler(protocol.Command.OSC_ANALOG_CHANNEL_ENABLE, has_payload=False)
    def osc_analog_channel_enable(self) -> bytes: ...  # type: ignore

    @_handler(protocol.Command.NUT_CLOCK, has_payload=False)
    def nut_clock(self) -> bytes: ...  # type: ignore

    @_handler(protocol.Command.OSC_SAMPLE_LENGTH, has_payload=False)
    def osc_sample_len(self) -> bytes: ...

    @_handler(protocol.Command.NUT_ENABLE, has_payload=False)
    def nut_enable(self) -> bytes: ...

    @_handler(protocol.Command.OSC_ANALOG_GAIN, has_payload=False)
    def osc_analog_gain(self) -> bytes: ...

    @_handler(protocol.Command.OSC_SAMPLE_DELAY, has_payload=False)
    def osc_sample_delay(self) -> bytes: ...

    @_handler(protocol.Command.OSC_SAMPLE_RATE, has_payload=False)
    def osc_sample_rate(self) -> bytes: ...

    @_handler(protocol.Command.OSC_CLOCK_SAMPLE_PHASE, has_payload=False)
    def osc_clock_sample_phase(self) -> bytes: ...

    @_handler(protocol.Command.OSC_ANALOG_TRIGGER_SOURCE, has_payload=False)
    def osc_analog_trigger_source(self) -> bytes: ...

    @_handler(protocol.Command.OSC_TRIGGER_MODE, has_payload=False)
    def osc_trigger_mode(self) -> bytes: ...

    @_handler(protocol.Command.OSC_TRIGGER_EDGE, has_payload=False)
    def osc_trigger_edge(self) -> bytes: ...

    @_handler(protocol.Command.OSC_TRIGGER_EDGE_LEVEL, has_payload=False)
    def osc_trigger_edge_level(self) -> bytes: ...

    @_handler(protocol.Command.CRACKER_SERIAL_DATA)
    def cracker_serial_data(self, payload: bytes) -> bytes:
        return os.urandom(10)

    @_handler(protocol.Command.NUT_CLOCK_ENABLE)
    def nut_clock_enable(self, payload: bytes) -> bytes:
        return b""

    @_handler(0xFFFF)
    def get_command_payload_cache(self, payload: bytes) -> bytes:
        command = struct.unpack(">I", payload)[0]
        return self._command_payload_cache.get(command)
