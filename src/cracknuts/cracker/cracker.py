import abc
from dataclasses import dataclass
import socket
import struct
import threading
import typing
from abc import ABC

import numpy as np

import cracknuts.utils.hex_util as hex_util
from cracknuts import logger
from cracknuts.cracker import protocol


class Cracker(typing.Protocol):
    def get_default_config(self) -> typing.Optional["Config"]: ...

    def set_addr(self, ip, port) -> None: ...

    def set_uri(self, uri: str) -> None: ...

    def get_uri(self): ...

    def connect(self): ...

    def disconnect(self): ...

    def reconnect(self): ...

    def get_connection_status(self) -> bool: ...

    def send_and_receive(self, message) -> None | bytes: ...

    def send_with_command(self, command: int | bytes, payload: str | bytes = None): ...

    def echo(self, payload: str) -> str: ...

    def echo_hex(self, payload: str) -> str: ...

    def get_id(self) -> str: ...

    def get_name(self) -> str: ...

    def scrat_analog_channel_enable(self, enable: dict[int, bool]): ...

    def scrat_analog_coupling(self, coupling: dict[int, int]): ...

    def scrat_analog_voltage(self, channel: int, voltage: int): ...

    def scrat_analog_bias_voltage(self, channel: int, voltage: int): ...

    def scrat_digital_channel_enable(self, enable: dict[int, bool]): ...

    def scrat_digital_voltage(self, voltage: int): ...

    def scrat_trigger_mode(self, source: int, stop: int): ...

    def scrat_analog_trigger_source(self, channel: int): ...

    def scrat_digital_trigger_source(self, channel: int): ...

    def scrat_analog_trigger_voltage(self, voltage: int): ...

    def scrat_sample_delay(self, delay: int): ...

    def scrat_sample_len(self, length: int): ...

    def scrat_arm(self): ...

    def scrat_force(self): ...

    def scrat_is_triggered(self): ...

    def scrat_get_analog_wave(self, channel: int, offset: int, sample_count: int) -> np.ndarray: ...

    def scrat_get_digital_wave(self, channel: int, offset: int, sample_count: int): ...

    def scrat_analog_gain(self, gain: int): ...

    def scrat_sample_clock(self, clock: int): ...

    def scrat_sample_phase(self, phase: int): ...

    def cracker_nut_enable(self, enable: int): ...

    def cracker_nut_voltage(self, voltage: int): ...

    def cracker_nut_clock(self, clock: int): ...

    def cracker_nut_interface(self, interface: dict[int, bool]): ...

    def cracker_nut_timeout(self, timeout: int): ...

    def cracker_serial_baud(self, baud: int): ...

    def cracker_serial_width(self, width: int): ...

    def cracker_serial_stop(self, stop: int): ...

    def cracker_serial_odd_eve(self, odd_eve: int): ...

    def cracker_serial_data(self, expect_len: int, data: bytes): ...

    def cracker_spi_cpol(self, cpol: int): ...

    def cracker_spi_cpha(self, cpha: int): ...

    def cracker_spi_data_len(self, cpha: int): ...

    def cracker_spi_freq(self, freq: int): ...

    def cracker_spi_timeout(self, timeout: int): ...

    def cracker_spi_data(self, expect_len: int, data: bytes): ...

    def cracker_i2c_freq(self, freq: int): ...

    def cracker_i2c_timeout(self, timeout: int): ...

    def cracker_i2c_data(self, expect_len: int, data: bytes): ...

    def cracker_can_freq(self, freq: int): ...

    def cracker_can_timeout(self, timeout: int): ...

    def cracker_can_data(self, expect_len: int, data: bytes): ...


class Commands:
    """
    Protocol commands.
    """

    GET_ID = 0x0001
    GET_NAME = 0x0002

    SCRAT_ANALOG_CHANNEL_ENABLE = 0x0100
    SCRAT_ANALOG_COUPLING = 0x0101
    SCRAT_ANALOG_VOLTAGE = 0x0102
    SCRAT_ANALOG_BIAS_VOLTAGE = 0x0103
    SCRAT_ANALOG_GAIN = 0x0104

    SCRAT_SAMPLE_CLOCK = 0x0105
    SCRAT_SAMPLE_PHASE = 0x0106

    SCRAT_DIGITAL_CHANNEL_ENABLE = 0x0110
    SCRAT_DIGITAL_VOLTAGE = 0x0111

    SCRAT_TRIGGER_MODE = 0x0120

    SCRAT_ANALOG_TRIGGER_SOURCE = 0x0121
    SCRAT_DIGITAL_TRIGGER_SOURCE = 0x0122

    SCRAT_ANALOG_TRIGGER_VOLTAGE = 0x0123

    SCRAT_SAMPLE_DELAY = 0x0124

    SCRAT_SAMPLE_LENGTH = 0x0125
    SCRAT_SAMPLE_RATE = 0x0128

    SCRAT_ARM = 0x0126

    SCRAT_IS_TRIGGERED = 0x0127
    SCRAT_FORCE = 0x0129

    SCRAT_GET_ANALOG_WAVES = 0x0130
    SCRAT_GET_DIGITAL_WAVES = 0x0130

    CRACKER_NUT_ENABLE = 0x0200
    CRACKER_NUT_VOLTAGE = 0x0201
    CRACKER_NUT_CLOCK = 0x0202
    CRACKER_NUT_INTERFACE = 0x0210
    CRACKER_NUT_TIMEOUT = 0x0224

    CRACKER_SERIAL_BAUD = 0x0220
    CRACKER_SERIAL_WIDTH = 0x0221
    CRACKER_SERIAL_STOP = 0x0222
    CRACKER_SERIAL_ODD_EVE = 0x0223
    CRACKER_SERIAL_DATA = 0x022A

    CRACKER_SPI_CPOL = 0x0230
    CRACKER_SPI_CPHA = 0x0231
    CRACKER_SPI_DATA_LEN = 0x0232
    CRACKER_SPI_FREQ = 0x0233
    CRACKER_SPI_TIMEOUT = 0x0234
    CRACKER_SPI_DATA = 0x023A

    CRACKER_I2C_FREQ = 0x0240
    CRACKER_I2C_TIMEOUT = 0x0244
    CRACKER_I2C_DATA = 0x024A

    CRACKER_CAN_FREQ = 0x0250
    CRACKER_CAN_TIMEOUT = 0x0254
    CRACKER_CA_DATA = 0x025A

    PROTOCOL_PREFIX = "cnp"
    PROTOCOL_DEFAULT_PORT = 9761


@dataclass
class Config:
    def __init__(
        self,
        cracker_nut_enable: bool = None,
        cracker_nut_voltage: int = None,
        cracker_nut_clock: int = None,
        scrat_analog_channel_enable: dict[int, bool] = None,
        cracker_scrat_sample_len: int = None,
        cracker_scrat_sample_delay: int = None,
        cracker_scrat_sample_phase: int = None,
        cracker_scrat_sample_clock: int = None,
    ):
        self._binder: dict[str, callable] = {}
        self.cracker_nut_enable: bool = cracker_nut_enable
        self.cracker_nut_voltage: int = cracker_nut_voltage
        self.cracker_nut_clock: int = cracker_nut_clock
        self.cracker_scrat_sample_len = cracker_scrat_sample_len
        self.cracker_scrat_sample_delay = cracker_scrat_sample_delay
        self.cracker_scrat_sample_phase = cracker_scrat_sample_phase
        self.cracker_scrat_sample_clock = cracker_scrat_sample_clock
        self.scrat_analog_channel_enable: dict[int, bool] = scrat_analog_channel_enable

    def __setattr__(self, key, value):
        self.__dict__[key] = value
        if "_binder" in self.__dict__ and (binder := self._binder.get(key)) is not None:
            binder(value)

    def bind(self, key: str, callback: callable):
        """
        Bind a callback which will be call when the key field is updated.
        :param key: a filed name of class `Config`
        :param callback:
        :return:
        """
        self._binder[key] = callback


class AbsCnpCracker(ABC, Cracker):
    """Cracker
    Cracker
    """

    def __init__(self, server_address=None):
        """
        :param server_address: Cracker device address (ip, port)
        """
        self._command_lock = threading.Lock()
        self._logger = logger.get_logger(self)
        self._server_address = server_address
        self._socket: socket.socket | None = None
        self._connection_status = False
        self._channel_enable: dict = {
            0: False,
            1: False,
        }

    @abc.abstractmethod
    def get_default_config(self) -> Config | None: ...

    def set_addr(self, ip, port) -> None:
        self._server_address = ip, port

    def set_uri(self, uri: str) -> None:
        if not uri.startswith("cnp://") and uri.count(":") < 2:
            uri = "cnp://" + uri

        uri = uri.replace("cnp://", "", 1)
        if ":" in uri:
            host, port = uri.split(":")
        else:
            host, port = uri, Commands.PROTOCOL_DEFAULT_PORT

        self._server_address = host, int(port)

    def get_uri(self):
        if self._server_address is None:
            return None
        else:
            return f"cnp://{self._server_address[0]}:{self._server_address[1]}"

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
            self._connection_status = True
            self._logger.info(f"Connected to cracker: {self._server_address}")
        except OSError as e:
            self._logger.error("Connection failed: %s", e)
            self._connection_status = False

    def disconnect(self):
        """
        Disconnect Cracker device.
        :return: Cracker self.
        """
        try:
            if self._socket:
                self._socket.close()
            self._socket = None
            self._logger.info(f"Disconnect from {self._server_address}")
        except OSError as e:
            self._logger.error("Disconnection failed: %s", e)
        finally:
            self._connection_status = False

    def reconnect(self):
        """
        Reconnect to Cracker device.
        :return: Cracker self.
        """
        self.disconnect()
        self.connect()

    def get_connection_status(self) -> bool:
        """
        Get connection status.
        :return: True or False
        """
        return self._connection_status

    def send_and_receive(self, message) -> None | bytes:
        """
        Send message to socket
        :param message:
        :return:
        """
        try:
            self._command_lock.acquire()
            if not self.get_connection_status():
                self.connect()
            self._logger.debug(
                "Send message to %s: \n%s",
                self._server_address,
                hex_util.get_bytes_matrix(message),
            )
            self._socket.sendall(message)
            resp_header = self._socket.recv(protocol.RESP_HEADER_SIZE)
            self._logger.debug(
                "Get response header from %s: \n%s",
                self._server_address,
                hex_util.get_bytes_matrix(resp_header),
            )
            magic, version, direction, status, length = struct.unpack(protocol.RESP_HEADER_FORMAT, resp_header)
            self._logger.debug(
                "Receive header from %s: %s",
                self._server_address,
                (magic, version, direction, status, length),
            )

            if length == 0:
                return None
            # resp_payload = self._socket.recv(length)
            resp_payload = self.recv(length)
            self._logger.debug(
                "Receive payload from %s: \n%s",
                self._server_address,
                hex_util.get_bytes_matrix(resp_payload),
            )
            return resp_payload
        except OSError as e:
            self._logger.error("Send message failed: %s, and msg: %s", e, message)
            return None
        finally:
            self._command_lock.release()

    # def recv(self, length):
    #     c = length // 1024
    #     r = length % 1024
    #     resp_payload = b''
    #     for _ in range(c):
    #         resp_payload += self._socket.recv(length)
    #
    #     resp_payload += self._socket.recv(r)
    #
    #     return resp_payload

    def recv(self, length):

        resp_payload = b''
        while (received_len :=len(resp_payload)) < length:
            for_receive_len = length - received_len
            resp_payload += self._socket.recv(for_receive_len)

        return resp_payload


    def send_with_command(self, command: int | bytes, payload: str | bytes = None):
        if isinstance(payload, str):
            payload = bytes.fromhex(payload)
        return self.send_and_receive(protocol.build_send_message(command, payload))

    def echo(self, payload: str) -> str:
        """
        length <= 1024
        """
        self._socket.sendall(payload.encode("ascii"))
        res = self._socket.recv(1024).decode("ascii")
        self._logger.debug(f"Get response: {res}")
        return res

    def echo_hex(self, payload: str) -> str:
        """
        length <= 1024
        """
        payload = bytes.fromhex(payload)
        self._socket.sendall(payload)
        res = self._socket.recv(1024).hex()
        self._logger.debug(f"Get response: {res}")
        return res

    @abc.abstractmethod
    def get_id(self) -> str: ...

    @abc.abstractmethod
    def get_name(self) -> str: ...

    @abc.abstractmethod
    def scrat_analog_channel_enable(self, enable: dict[int, bool]): ...

    @abc.abstractmethod
    def scrat_analog_coupling(self, coupling: dict[int, int]): ...

    @abc.abstractmethod
    def scrat_analog_voltage(self, channel: int, voltage: int): ...

    @abc.abstractmethod
    def scrat_analog_bias_voltage(self, channel: int, voltage: int): ...

    @abc.abstractmethod
    def scrat_digital_channel_enable(self, enable: dict[int, bool]): ...

    @abc.abstractmethod
    def scrat_digital_voltage(self, voltage: int): ...

    @abc.abstractmethod
    def scrat_trigger_mode(self, source: int, stop: int): ...

    @abc.abstractmethod
    def scrat_analog_trigger_source(self, channel: int): ...

    @abc.abstractmethod
    def scrat_digital_trigger_source(self, channel: int): ...

    @abc.abstractmethod
    def scrat_analog_trigger_voltage(self, voltage: int): ...

    @abc.abstractmethod
    def scrat_sample_delay(self, delay: int): ...

    @abc.abstractmethod
    def scrat_sample_len(self, length: int): ...

    @abc.abstractmethod
    def scrat_arm(self): ...

    @abc.abstractmethod
    def scrat_force(self): ...

    @abc.abstractmethod
    def scrat_is_triggered(self): ...

    @abc.abstractmethod
    def scrat_get_analog_wave(self, channel: int, offset: int, sample_count: int) -> np.ndarray: ...

    @abc.abstractmethod
    def scrat_get_digital_wave(self, channel: int, offset: int, sample_count: int): ...

    @abc.abstractmethod
    def scrat_analog_gain(self, gain: int): ...

    @abc.abstractmethod
    def scrat_sample_clock(self, clock: int): ...

    @abc.abstractmethod
    def scrat_sample_phase(self, phase: int): ...

    @abc.abstractmethod
    def cracker_nut_enable(self, enable: int): ...

    @abc.abstractmethod
    def cracker_nut_voltage(self, voltage: int): ...

    @abc.abstractmethod
    def cracker_nut_clock(self, clock: int): ...

    @abc.abstractmethod
    def cracker_nut_interface(self, interface: dict[int, bool]): ...

    @abc.abstractmethod
    def cracker_nut_timeout(self, timeout: int): ...

    @abc.abstractmethod
    def cracker_serial_baud(self, baud: int): ...

    @abc.abstractmethod
    def cracker_serial_width(self, width: int): ...

    @abc.abstractmethod
    def cracker_serial_stop(self, stop: int): ...

    @abc.abstractmethod
    def cracker_serial_odd_eve(self, odd_eve: int): ...

    @abc.abstractmethod
    def cracker_serial_data(self, expect_len: int, data: bytes): ...

    @abc.abstractmethod
    def cracker_spi_cpol(self, cpol: int): ...

    @abc.abstractmethod
    def cracker_spi_cpha(self, cpha: int): ...

    @abc.abstractmethod
    def cracker_spi_data_len(self, cpha: int): ...

    @abc.abstractmethod
    def cracker_spi_freq(self, freq: int): ...

    @abc.abstractmethod
    def cracker_spi_timeout(self, timeout: int): ...

    @abc.abstractmethod
    def cracker_spi_data(self, expect_len: int, data: bytes): ...

    @abc.abstractmethod
    def cracker_i2c_freq(self, freq: int): ...

    @abc.abstractmethod
    def cracker_i2c_timeout(self, timeout: int): ...

    @abc.abstractmethod
    def cracker_i2c_data(self, expect_len: int, data: bytes): ...

    @abc.abstractmethod
    def cracker_can_freq(self, freq: int): ...

    @abc.abstractmethod
    def cracker_can_timeout(self, timeout: int): ...

    @abc.abstractmethod
    def cracker_can_data(self, expect_len: int, data: bytes): ...
