import abc
import socket
import struct
import threading
import typing
from abc import ABC
from dataclasses import dataclass

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

    def send_and_receive(self, message) -> tuple[int, bytes]: ...

    def send_with_command(self, command: int, rfu: int = 0, payload: str | bytes = None) -> tuple[int, bytes]: ...

    def echo(self, payload: str) -> str: ...

    def echo_hex(self, payload: str) -> str: ...

    def get_id(self) -> str | None: ...

    def get_name(self) -> str | None: ...

    def get_version(self) -> str | None: ...

    def osc_set_analog_channel_enable(self, enable: dict[int, bool]): ...

    def osc_set_analog_coupling(self, coupling: dict[int, int]): ...

    def osc_set_analog_voltage(self, channel: int, voltage: int): ...

    def osc_set_analog_bias_voltage(self, channel: int, voltage: int): ...

    def osc_set_digital_channel_enable(self, enable: dict[int, bool]): ...

    def osc_set_digital_voltage(self, voltage: int): ...

    def osc_set_trigger_mode(self, source: int, stop: int): ...

    def osc_set_analog_trigger_source(self, channel: int): ...

    def osc_set_digital_trigger_source(self, channel: int): ...

    def osc_set_analog_trigger_voltage(self, voltage: int): ...

    def osc_set_sample_delay(self, delay: int): ...

    def osc_set_sample_len(self, length: int): ...

    def osc_single(self): ...

    def osc_force(self): ...

    def osc_is_triggered(self): ...

    def osc_get_analog_wave(self, channel: int, offset: int, sample_count: int) -> tuple[int, np.ndarray]: ...

    def osc_get_digital_wave(self, channel: int, offset: int, sample_count: int): ...

    def osc_set_analog_gain(self, channel: int, gain: int): ...

    def osc_set_analog_gain_raw(self, channel: int, gain: int): ...

    def osc_set_sample_clock(self, clock: int): ...

    def osc_set_sample_phase(self, phase: int): ...

    def nut_enable(self, enable: int): ...

    def nut_voltage(self, voltage: int): ...

    def nut_voltage_raw(self, voltage: int): ...

    def nut_clock(self, clock: int): ...

    def nut_interface(self, interface: dict[int, bool]): ...

    def nut_timeout(self, timeout: int): ...

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
    GET_VERSION = 0x0003

    OSC_ANALOG_CHANNEL_ENABLE = 0x0100
    OSC_ANALOG_COUPLING = 0x0101
    OSC_ANALOG_VOLTAGE = 0x0102
    OSC_ANALOG_BIAS_VOLTAGE = 0x0103
    OSC_ANALOG_GAIN = 0x0104
    OSC_ANALOG_GAIN_RAW = 0x0107

    OSC_SAMPLE_CLOCK = 0x0105
    OSC_SAMPLE_PHASE = 0x0106

    OSC_DIGITAL_CHANNEL_ENABLE = 0x0110
    OSC_DIGITAL_VOLTAGE = 0x0111

    OSC_TRIGGER_MODE = 0x0120

    OSC_ANALOG_TRIGGER_SOURCE = 0x0121
    OSC_DIGITAL_TRIGGER_SOURCE = 0x0122

    OSC_ANALOG_TRIGGER_VOLTAGE = 0x0123

    OSC_SAMPLE_DELAY = 0x0124

    OSC_SAMPLE_LENGTH = 0x0125
    OSC_SAMPLE_RATE = 0x0128

    OSC_SINGLE = 0x0126

    OSC_IS_TRIGGERED = 0x0127
    OSC_FORCE = 0x0129

    OSC_GET_ANALOG_WAVES = 0x0130
    OSC_GET_DIGITAL_WAVES = 0x0130

    NUT_ENABLE = 0x0200
    NUT_VOLTAGE = 0x0201
    NUT_VOLTAGE_RAW = 0x0203
    NUT_CLOCK = 0x0202
    NUT_INTERFACE = 0x0210
    NUT_TIMEOUT = 0x0224

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


@dataclass
class Config:
    def __init__(
        self,
        nut_enable: bool = None,
        nut_voltage: int = None,
        nut_clock: int = None,
        osc_analog_channel_enable: dict[int, bool] = None,
        osc_sample_len: int = None,
        osc_sample_delay: int = None,
        osc_sample_phase: int = None,
        osc_sample_clock: int = None,
    ):
        self._binder: dict[str, callable] = {}
        self.nut_enable: bool = nut_enable
        self.nut_voltage: int = nut_voltage
        self.nut_clock: int = nut_clock
        self.osc_sample_len = osc_sample_len
        self.osc_sample_delay = osc_sample_delay
        self.osc_sample_phase = osc_sample_phase
        self.osc_sample_clock = osc_sample_clock
        self.osc_analog_channel_enable: dict[int, bool] = osc_analog_channel_enable

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

    def __init__(self, address: tuple | str | None = None):
        """
        :param address: Cracker device address (ip, port) or "cnp://xxx:xx"
        """
        self._command_lock = threading.Lock()
        self._logger = logger.get_logger(self)
        if isinstance(address, tuple):
            self._server_address = address
        elif isinstance(address, str):
            self.set_uri(address)
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
            host, port = uri, protocol.DEFAULT_PORT

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
            if self._connection_status:
                self._logger.debug("Already connected, reuse.")
                return
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

    def send_and_receive(self, message) -> tuple[int, bytes | None]:
        """
        Send message to socket
        :param message:
        :return:
        """
        try:
            self._command_lock.acquire()
            if not self.get_connection_status():
                self._logger.error("Cracker is not connected.")
                return protocol.STATUS_ERROR, None
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
                    "Receive payload from {self._server_address}: \n{hex_util.get_bytes_matrix(resp_payload)}"
                )
            else:
                self._logger.debug(
                    "Receive payload from {self._server_address}: \n{hex_util.get_bytes_matrix(resp_payload)}"
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

    def send_with_command(self, command: int, rfu: int = 0, payload: str | bytes = None) -> tuple[int, bytes]:
        if isinstance(payload, str):
            payload = bytes.fromhex(payload)
        return self.send_and_receive(protocol.build_send_message(command, rfu, payload))

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
    def get_id(self) -> str | None: ...

    @abc.abstractmethod
    def get_name(self) -> str | None: ...

    def get_version(self) -> str | None:
        return super().get_version()

    @abc.abstractmethod
    def osc_set_analog_channel_enable(self, enable: dict[int, bool]): ...

    @abc.abstractmethod
    def osc_set_analog_coupling(self, coupling: dict[int, int]): ...

    @abc.abstractmethod
    def osc_set_analog_voltage(self, channel: int, voltage: int): ...

    @abc.abstractmethod
    def osc_set_analog_bias_voltage(self, channel: int, voltage: int): ...

    @abc.abstractmethod
    def osc_set_digital_channel_enable(self, enable: dict[int, bool]): ...

    @abc.abstractmethod
    def osc_set_digital_voltage(self, voltage: int): ...

    @abc.abstractmethod
    def osc_set_trigger_mode(self, source: int, stop: int): ...

    @abc.abstractmethod
    def osc_set_analog_trigger_source(self, channel: int): ...

    @abc.abstractmethod
    def osc_set_digital_trigger_source(self, channel: int): ...

    @abc.abstractmethod
    def osc_set_analog_trigger_voltage(self, voltage: int): ...

    @abc.abstractmethod
    def osc_set_sample_delay(self, delay: int): ...

    @abc.abstractmethod
    def osc_set_sample_len(self, length: int): ...

    @abc.abstractmethod
    def osc_single(self): ...

    @abc.abstractmethod
    def osc_force(self): ...

    @abc.abstractmethod
    def osc_is_triggered(self): ...

    @abc.abstractmethod
    def osc_get_analog_wave(self, channel: int, offset: int, sample_count: int) -> tuple[int, np.ndarray]: ...

    @abc.abstractmethod
    def osc_get_digital_wave(self, channel: int, offset: int, sample_count: int): ...

    @abc.abstractmethod
    def osc_set_analog_gain(self, channel: int, gain: int): ...

    @abc.abstractmethod
    def osc_set_analog_gain_raw(self, channel: int, gain: int): ...

    @abc.abstractmethod
    def osc_set_sample_clock(self, clock: int): ...

    @abc.abstractmethod
    def osc_set_sample_phase(self, phase: int): ...

    @abc.abstractmethod
    def nut_enable(self, enable: int): ...

    @abc.abstractmethod
    def nut_voltage(self, voltage: int): ...

    @abc.abstractmethod
    def nut_voltage_raw(self, voltage: int): ...

    @abc.abstractmethod
    def nut_clock(self, clock: int): ...

    @abc.abstractmethod
    def nut_interface(self, interface: dict[int, bool]): ...

    @abc.abstractmethod
    def nut_timeout(self, timeout: int): ...

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
