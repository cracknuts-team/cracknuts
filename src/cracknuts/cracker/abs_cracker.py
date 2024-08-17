import socket
import struct
import typing
from abc import ABC
from abc import abstractmethod

import numpy as np

from cracknuts import logger
from cracknuts.cracker import protocol
import cracknuts.utils.hex_util as hex_util


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

    SCRAT_DIGITAL_CHANNEL_ENABLE = 0x0110
    SCRAT_DIGITAL_VOLTAGE = 0x0111

    SCRAT_TRIGGER_MODE = 0x0120

    SCRAT_ANALOG_TRIGGER_SOURCE = 0x0121
    SCRAT_DIGITAL_TRIGGER_SOURCE = 0x0122

    SCRAT_ANALOG_TRIGGER_VOLTAGE = 0x0123

    SCRAT_TRIGGER_DELAY = 0x0124

    SCRAT_SAMPLE_LENGTH = 0x0125
    SCRAT_SAMPLE_RATE = 0x0128

    SCRAT_ARM = 0x0126

    SCRAT_IS_TRIGGERED = 0x0127

    SCRAT_GET_ANALOG_WAVES = 0x0130
    SCRAT_GET_DIGITAL_WAVES = 0x0130

    CRACKER_NUT_ENABLE = 0x0200
    CRACKER_NUT_VOLTAGE = 0x0201
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

    PROTOCOL_PREFIX = 'cnp'
    PROTOCOL_DEFAULT_PORT = 9761


class AbsCracker(ABC):
    """Cracker
    Cracker
    """

    def __init__(self, server_address=None):
        """
        :param server_address: Cracker device address (ip, port)
        """
        self._logger = logger.get_logger(self)
        self._server_address = server_address
        self._socket: socket.socket | None = None
        self._connection_status = False
        self._channel_enable: dict = {0: False, 1: False, 2: False, 3: False, 4: False, 5: False, 6: False, 7: False}

    def set_addr(self, ip, port) -> None:
        self._server_address = ip, port

    def set_uri(self, uri: str) -> None:
        if not uri.startswith('cnp://') and uri.count(':') < 2:
            uri = 'cnp://' + uri

        uri = uri.replace('cnp://', '', 1)
        if ':' in uri:
            host, port = uri.split(':')
        else:
            host, port = uri, Commands.PROTOCOL_DEFAULT_PORT

        self._server_address = host, int(port)

    def get_uri(self):
        if self._server_address is None:
            return None
        else:
            return f'cnp://{self._server_address[0]}:{self._server_address[1]}'

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
            self._logger.info('Connected to cracker: {}'.format(self._server_address))
        except socket.error as e:
            self._logger.error('Connection failed: %s', e)
            self._connection_status = False
        return self

    def disconnect(self):
        """
        Disconnect Cracker device.
        :return: Cracker self.
        """
        try:
            if self._socket:
                self._socket.close()
            self._socket = None
            self._logger.info(f'Disconnect from {self._server_address}')
        except socket.error as e:
            self._logger.error('Disconnection failed: %s', e)
        finally:
            self._connection_status = False
        return self

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
            if not self.get_connection_status():
                self.connect()
            self._logger.debug("Send message to %s: \n%s", self._server_address,
                               hex_util.get_bytes_matrix(message))
            self._socket.sendall(message)
            resp_header = self._socket.recv(protocol.RESP_HEADER_SIZE)
            self._logger.debug("Get response header from %s: \n%s", self._server_address,
                               hex_util.get_bytes_matrix(resp_header))
            magic, version, direction, status, length = struct.unpack(
                protocol.RESP_HEADER_FORMAT, resp_header
            )
            self._logger.debug(
                "Receive header from %s: %s",
                self._server_address,
                (magic, version, direction, status, length),
            )

            if length == 0:
                return None
            resp_payload = self._socket.recv(length)
            self._logger.debug(
                "Receive payload from %s: \n%s", self._server_address, hex_util.get_bytes_matrix(resp_payload)
            )
            return resp_payload
        except socket.error as e:
            self._logger.error('Send message failed: %s', e)
            return None

    def send_with_command(self, command: int | bytes, payload: str | bytes = None):
        if isinstance(payload, str):
            payload = bytes.fromhex(payload)
        return self.send_and_receive(protocol.build_send_message(command, payload))

    def echo(self, payload: str) -> str:
        """
        length <= 1024
        """
        self._socket.sendall(payload.encode('ascii'))
        res = self._socket.recv(1024).decode('ascii')
        self._logger.debug(f'Get response: {res}')
        return res

    def echo_hex(self, payload: str) -> str:
        """
        length <= 1024
        """
        payload = bytes.fromhex(payload)
        self._socket.sendall(payload)
        res = self._socket.recv(1024).hex()
        self._logger.debug(f'Get response: {res}')
        return res

    @abstractmethod
    def get_id(self) -> str:
        ...

    @abstractmethod
    def get_name(self) -> str:
        ...

    @abstractmethod
    def scrat_analog_channel_enable(self, enable: typing.Dict[int, bool]):
        ...

    @abstractmethod
    def scrat_analog_coupling(self, coupling: typing.Dict[int, int]):
        ...

    @abstractmethod
    def scrat_analog_voltage(self, channel: int, voltage: int):
        ...

    @abstractmethod
    def scrat_analog_bias_voltage(self, channel: int, voltage: int):
        ...

    @abstractmethod
    def scrat_digital_channel_enable(self, enable: typing.Dict[int, bool]):
        ...

    @abstractmethod
    def scrat_digital_voltage(self, voltage: int):
        ...

    @abstractmethod
    def scrat_trigger_mode(self, source: int, stop: int):
        ...

    @abstractmethod
    def scrat_analog_trigger_source(self, channel: int):
        ...

    @abstractmethod
    def scrat_digital_trigger_source(self, channel: int):
        ...

    @abstractmethod
    def scrat_analog_trigger_voltage(self, voltage: int):
        ...

    @abstractmethod
    def scrat_trigger_delay(self, delay: int):
        ...

    @abstractmethod
    def scrat_sample_len(self, length: int):
        ...

    @abstractmethod
    def scrat_arm(self):
        ...

    @abstractmethod
    def scrat_is_triggered(self):
        ...

    @abstractmethod
    def scrat_get_analog_wave(self, channel: int, offset: int, sample_count: int) -> np.ndarray:
        ...

    @abstractmethod
    def scrat_get_digital_wave(self, channel: int, offset: int, sample_count: int):
        ...

    @abstractmethod
    def scrat_analog_gain(self, gain: int):
        ...

    @abstractmethod
    def cracker_nut_enable(self, enable: int):
        ...

    @abstractmethod
    def cracker_nut_voltage(self, voltage: int):
        ...

    @abstractmethod
    def cracker_nut_interface(self, interface: typing.Dict[int, bool]):
        ...

    @abstractmethod
    def cracker_nut_timeout(self, timeout: int):
        ...

    @abstractmethod
    def cracker_serial_baud(self, baud: int):
        ...

    @abstractmethod
    def cracker_serial_width(self, width: int):
        ...

    @abstractmethod
    def cracker_serial_stop(self, stop: int):
        ...

    @abstractmethod
    def cracker_serial_odd_eve(self, odd_eve: int):
        ...

    @abstractmethod
    def cracker_serial_data(self, expect_len: int, data: bytes):
        ...

    @abstractmethod
    def cracker_spi_cpol(self, cpol: int):
        ...

    @abstractmethod
    def cracker_spi_cpha(self, cpha: int):
        ...

    @abstractmethod
    def cracker_spi_data_len(self, cpha: int):
        ...

    @abstractmethod
    def cracker_spi_freq(self, freq: int):
        ...

    @abstractmethod
    def cracker_spi_timeout(self, timeout: int):
        ...

    @abstractmethod
    def cracker_spi_data(self, expect_len: int, data: bytes):
        ...

    @abstractmethod
    def cracker_i2c_freq(self, freq: int):
        ...

    @abstractmethod
    def cracker_i2c_timeout(self, timeout: int):
        ...

    @abstractmethod
    def cracker_i2c_data(self, expect_len: int, data: bytes):
        ...

    @abstractmethod
    def cracker_can_freq(self, freq: int):
        ...

    @abstractmethod
    def cracker_can_timeout(self, timeout: int):
        ...

    @abstractmethod
    def cracker_can_data(self, expect_len: int, data: bytes):
        ...
