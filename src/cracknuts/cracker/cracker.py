# Copyright 2024 CrackNuts. All rights reserved.

import abc
import json
import logging
import os
import re
import socket
import struct
import threading
import typing
from abc import ABC

import numpy as np
from packaging.version import Version

import cracknuts
import cracknuts.utils.hex_util as hex_util
from cracknuts import logger
from cracknuts.cracker import protocol
from cracknuts.cracker.operator import Operator


class CommonCommands:
    """
    Protocol commands.
    """

    GET_ID = 0x0001
    GET_NAME = 0x0002
    GET_VERSION = 0x0003

    CRACKER_READ_REGISTER = 0x0004
    CRACKER_WRITE_REGISTER = 0x0005

    OSC_ANALOG_CHANNEL_ENABLE = 0x0100
    OSC_ANALOG_COUPLING = 0x0101
    OSC_ANALOG_VOLTAGE = 0x0102
    OSC_ANALOG_BIAS_VOLTAGE = 0x0103
    OSC_ANALOG_GAIN = 0x0104
    OSC_ANALOG_GAIN_RAW = 0x0105
    OSC_CLOCK_BASE_FREQ_MUL_DIV = 0x0106
    OSC_CLOCK_SAMPLE_DIVISOR = 0x0107
    OSC_CLOCK_SAMPLE_PHASE = 0x0108
    OSC_CLOCK_NUT_DIVISOR = 0x0109
    OSC_CLOCK_UPDATE = 0x10A
    OSC_CLOCK_SIMPLE = 0x10B

    OSC_DIGITAL_CHANNEL_ENABLE = 0x0110
    OSC_DIGITAL_VOLTAGE = 0x0111

    OSC_TRIGGER_MODE = 0x0151

    OSC_ANALOG_TRIGGER_SOURCE = 0x0150
    OSC_DIGITAL_TRIGGER_SOURCE = 0x0122

    OSC_TRIGGER_EDGE = 0x152
    OSC_TRIGGER_EDGE_LEVEL = 0x153

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

    SPI_TRANSCEIVE = 0x023C

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
    CRACKER_I2C_TRANSCEIVE = 0x024A

    CRACKER_CAN_FREQ = 0x0250
    CRACKER_CAN_TIMEOUT = 0x0254
    CRACKER_CA_DATA = 0x025A


class CommonConfig:
    def __init__(self):
        """
        For specific devices, users need to set default values and extend configuration items by inheriting this class.
        """

        self._binder: dict[str, typing.Callable] = {}

        self.osc_analog_channel_enable: dict[int, bool] = {}
        self.osc_analog_coupling: dict[int, int] = {}
        self.osc_analog_voltage: dict[int, int] = {}
        self.osc_analog_bias_voltage: dict[int, int] = {}
        self.osc_digital_voltage: int | None = None
        self.osc_trigger_mode: int | None = None
        self.osc_analog_trigger_source: int | None = None
        self.osc_digital_trigger_source: int | None = None
        self.osc_analog_trigger_edge: int | None = None
        self.osc_analog_trigger_edge_level: int | None = None
        self.osc_sample_delay: int | None = None
        self.osc_sample_len: int | None = None
        self.osc_sample_rate: int | None = None
        self.osc_analog_gain: dict[int, int] = {}
        self.osc_analog_gain_raw: dict[int, int] = {}
        self.osc_clock_base_freq_mul_div: tuple[int, int, int] | None = None
        self.osc_clock_sample_divisor: tuple[int, int] | None = None
        self.osc_clock_simple: tuple[int, int, int] | None = None
        self.osc_clock_phase: int | None = None
        self.osc_clock_divisor: int | None = None
        self.osc_sample_phase: int | None = None

        self.nut_enable: bool | None = None
        self.nut_voltage: int | None = None
        self.nut_voltage_raw: int | None = None
        self.nut_clock: int | None = None
        self.nut_interface: int | None = None
        self.nut_timeout: int | None = None

    def __setattr__(self, key, value):
        self.__dict__[key] = value
        if "_binder" in self.__dict__ and (binder := self._binder.get(key)) is not None:
            binder(value)

    def bind(self, key: str, callback: typing.Callable):
        """
        Bind a callback which will be call when the key field is updated.
        :param key: a filed name of class `Config`
        :param callback:
        :return:
        """
        self._binder[key] = callback

    def __str__(self):
        return f"Config({", ".join([f"{k}: {v}" for k, v in self.__dict__.items() if not k.startswith("_")])})"

    def __repr__(self):
        return self.__str__()

    def dump_to_json(self) -> str:
        """
        Dump the configuration to a JSON string.

        """
        return json.dumps({k: v for k, v in self.__dict__.items() if k != "_binder"})

    def load_from_json(self, json_str: str) -> "CommonConfig":
        """
        Load configuration from a JSON string. If a value in the JSON string is null, it will be skipped,
        and the default configuration will be used.

        """
        for k, v in json.loads(json_str).items():
            if k in (
                "osc_analog_channel_enable",
                "osc_analog_coupling",
                "osc_analog_voltage",
                "osc_analog_bias_voltage",
                "osc_analog_gain",
                "osc_analog_gain_raw",
            ):
                v = {int(_k): _v for _k, _v in v.items()}
            if v is not None:
                self.__dict__[k] = v
        return self


T = typing.TypeVar("T", bound=CommonConfig)


class BaseCracker(ABC, typing.Generic[T]):
    """Cnp protocol supported Cracker"""

    def __init__(
        self,
        address: tuple | str | None = None,
        bin_server_path: str | None = None,
        bin_bitstream_path: str | None = None,
        operator_port: int = None,
    ):
        """
        :param address: Cracker device address (ip, port) or "cnp://xxx:xx"
        """
        self._command_lock = threading.Lock()
        self._logger = logger.get_logger(self)
        self._socket: socket.socket | None = None
        self._connection_status = False
        self._bin_server_path = bin_server_path
        self._bin_bitstream_path = bin_bitstream_path
        self._operator_port = operator_port
        self._server_address = None
        self.set_address(address)
        self._config = self.get_default_config()

    def set_address(self, address: tuple[str, int] | str):
        if isinstance(address, tuple):
            self._server_address = address
        elif isinstance(address, str):
            self.set_uri(address)

    def get_address(self):
        return self._server_address

    def set_ip_port(self, ip, port) -> None:
        self._server_address = ip, port

    def set_uri(self, uri: str) -> None:
        if not uri.startswith("cnp://") and uri.count(":") < 2:
            uri = "cnp://" + uri

        uri = uri.replace("cnp://", "", 1)
        if ":" in uri:
            host, port = uri.split(":")
        else:
            host, port = uri, protocol.DEFAULT_PORT  # type: ignore

        self._server_address = host, int(port)

    def get_uri(self):
        if self._server_address is None:
            return None
        else:
            port = self._server_address[1]
            if port == protocol.DEFAULT_PORT:
                port = None
            return f"cnp://{self._server_address[0]}{"" if port is None else f":{port}"}"

    def connect(
        self,
        update_bin: bool = True,
        force_update_bin: bool = False,
        bin_server_path: str | None = None,
        bin_bitstream_path: str | None = None,
    ):
        """
        Connect to Cracker device.
        """
        if bin_server_path is None:
            bin_server_path = self._bin_server_path
        if bin_bitstream_path is None:
            bin_bitstream_path = self._bin_bitstream_path

        if update_bin and not self._update_cracker_bin(
            force_update_bin, bin_server_path, bin_bitstream_path, self._operator_port
        ):
            return

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

    def _update_cracker_bin(
        self,
        force_update: bool = False,
        bin_server_path: str | None = None,
        bin_bitstream_path: str | None = None,
        operator_port: int = None,
        server_version: str = None,
        bitstream_version: str = None,
    ) -> bool:
        if operator_port is None:
            operator_port = protocol.DEFAULT_OPERATOR_PORT
        operator = Operator(self._server_address[0], operator_port)

        if not operator.connect():
            return False

        if not force_update and operator.get_status():
            operator.disconnect()
            return True

        hardware_model = operator.get_hardware_model()

        bin_path = os.path.join(cracknuts.__file__, "bin")
        user_home_bin_path = os.path.join(os.path.expanduser("~"), ".cracknuts", "bin")
        current_bin_path = os.path.join(os.getcwd(), ".bin")

        if bin_server_path is None or bin_bitstream_path is None:
            server_bin_dict, bitstream_bin_dict = self._find_bin_files(bin_path, user_home_bin_path, current_bin_path)
            self._logger.debug(
                f"Find bin server_bin_dict: {server_bin_dict} and bitstream_bin_dict: {bitstream_bin_dict}"
            )
            if bin_server_path is None:
                bin_server_path = self._get_version_file_path(server_bin_dict, hardware_model, server_version)
            if bin_bitstream_path is None:
                bin_bitstream_path = self._get_version_file_path(bitstream_bin_dict, hardware_model, bitstream_version)

        if bin_server_path is None or not os.path.exists(bin_server_path):
            self._logger.error(
                f"Server binary file not found for hardware: {hardware_model} and server_version: {server_version}."
            )
            return False

        if bin_bitstream_path is None or not os.path.exists(bin_bitstream_path):
            self._logger.error(
                f"Bitstream file not found for hardware: {hardware_model} and bitstream_version: {bitstream_version}"
            )
            return False

        self._logger.debug(f"Get bit_server file at {bin_server_path}.")
        self._logger.debug(f"Get bin_bitstream file at {bin_bitstream_path}.")
        bin_server = open(bin_server_path, "rb").read()
        bin_bitstream = open(bin_bitstream_path, "rb").read()

        try:
            return (
                operator.update_server(bin_server)
                and operator.update_bitstream(bin_bitstream)
                and operator.get_status()
            )
        except OSError as e:
            self._logger.error("Do update cracker bin failed: %s", e)
            return False
        finally:
            operator.disconnect()

    def _get_version_file_path(
        self, bin_dict: dict[str, dict[str, str]], hardware_model: str, version: str
    ) -> str | None:
        dict_by_hardware = bin_dict.get(hardware_model, None)
        if dict_by_hardware is None:
            self._logger.error(f"bin file dict is none: {hardware_model}.")
            return None
        if version is None:
            sorted_version = sorted(dict_by_hardware.keys(), key=Version)
            version = sorted_version[-1]
        return dict_by_hardware.get(version, None)

    @staticmethod
    def _find_bin_files(*bin_paths: str) -> tuple[dict[str, dict[str, str]], dict[str, dict[str, str]]]:
        server_path_pattern = r"server-(?P<hardware>.+?)-(?P<firmware>.+?)"
        bitstream_path_pattern = r"bitstream-(?P<hardware>.+?)-(?P<firmware>.+?).bit.bin"

        server_bin_dict = {}
        bitstream_bin_dict = {}

        for bin_path in bin_paths:
            if os.path.exists(bin_path):
                for filename in os.listdir(bin_path):
                    server_match = re.search(server_path_pattern, filename)
                    if server_match:
                        server_hardware_version = server_match.group("hardware")
                        server_firmware_version = server_match.group("firmware")
                        server_hardware_dict = server_bin_dict.get(server_hardware_version, {})
                        server_hardware_dict[server_firmware_version] = os.path.join(bin_path, filename)
                        server_bin_dict[server_hardware_version] = server_hardware_dict
                    bitstream_match = re.search(bitstream_path_pattern, filename)
                    if bitstream_match:
                        bitstream_hardware_version = bitstream_match.group("hardware")
                        bitstream_firmware_version = bitstream_match.group("firmware")
                        bitstream_hardware_dict = bitstream_bin_dict.get(bitstream_hardware_version, {})
                        bitstream_hardware_dict[bitstream_firmware_version] = os.path.join(bin_path, filename)
                        bitstream_bin_dict[bitstream_hardware_version] = bitstream_hardware_dict

        return server_bin_dict, bitstream_bin_dict

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
        if self._socket is None:
            self._logger.error("Cracker not connected")
            return protocol.STATUS_ERROR, None
        try:
            self._command_lock.acquire()
            if not self.get_connection_status():
                self._logger.error("Cracker is not connected.")
                return protocol.STATUS_ERROR, None
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
            if self._logger.isEnabledFor(logging.DEBUG):
                self._logger.debug(
                    f"Receive header from {self._server_address}: "
                    f"{magic}, {version}, {direction}, {status:02X}, {length}"
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

    @abc.abstractmethod
    def get_default_config(self) -> T: ...

    def get_current_config(self) -> T:
        """
        Get current configuration of `Cracker`.
        Note: Currently, the configuration returned is recorded on the host computer,
        not the ACTUAL configuration of the device. In the future, it should be
        synchronized from the device to the host computer.

        :return: Current configuration of `Cracker`.
        :rtype: CommonConfig
        """
        return self._config

    def sync_config_to_cracker(self):
        """
        Sync config to cracker.

        To prevent configuration inconsistencies between the host and the device,
        so all configuration information needs to be written to the device.
        User should call this function before get data from device.

        NOTE: This function is currently ignored and will be resumed after all Cracker functions are completed.
        """
        ...

    def dump_config(self, path=None) -> str | None:
        """
        Dump the current config to a JSON file if a path is specified, or to a JSON string if no path is specified.

        :param path: the path to the JSON file
        :return: the content of JSON string or None if no path is specified.
        """
        config_json = self._config.dump_to_json()
        if path is None:
            return config_json
        else:
            with open(path, "w") as f:
                f.write(config_json)

    def load_config_from_file(self, path) -> None:
        """
        Load config from a JSON file.

        :param path: the path to the JSON file
        """
        with open(path) as f:
            self.load_config_from_str(f.readlines())

    def load_config_from_str(self, json_str) -> None:
        """
        Load config from a JSON string.

        :param json_str: the JSON string
        """
        self._config.load_from_json(json_str)


class CommonCracker(BaseCracker[T], ABC):
    def get_id(self) -> str | None:
        status, res = self.send_with_command(CommonCommands.GET_ID)
        if status != protocol.STATUS_OK:
            self._logger.error(f"Receive status code error [{status}]")
        return res.decode("ascii") if res is not None else None

    def get_name(self) -> str | None:
        status, res = self.send_with_command(CommonCommands.GET_NAME)
        if status != protocol.STATUS_OK:
            self._logger.error(f"Receive status code error [{status}]")
        return res.decode("ascii") if res is not None else None

    def get_version(self) -> str | None:
        status, res = self.send_with_command(CommonCommands.GET_VERSION)
        if status != protocol.STATUS_OK:
            self._logger.error(f"Receive status code error [{status}]")
        return res.decode("ascii") if res is not None else None

    def cracker_read_register(self, base_address: int, offset: int) -> bytes | None:
        payload = struct.pack(">II", base_address, offset)
        self._logger.debug(f"cracker_read_register payload: {payload.hex()}")
        status, res = self.send_with_command(CommonCommands.CRACKER_READ_REGISTER, payload=payload)
        if status != protocol.STATUS_OK:
            self._logger.error(f"Receive status code error [{status}]")
            return None
        else:
            return res

    def cracker_write_register(self, base_address: int, offset: int, data: bytes | int | str) -> bytes | None:
        if isinstance(data, str):
            if data.startswith("0x") or data.startswith("0X"):
                data = data[2:]
            data = bytes.fromhex(data)
        if isinstance(data, int):
            data = struct.pack(">I", data)
        payload = struct.pack(">II", base_address, offset) + data
        self._logger.debug(f"cracker_write_register payload: {payload.hex()}")
        status, res = self.send_with_command(CommonCommands.CRACKER_WRITE_REGISTER, payload=payload)
        if status != protocol.STATUS_OK:
            self._logger.error(f"Receive status code error [{status}]")
            return None
        else:
            return res

    def osc_set_analog_channel_enable(self, channel: int, enable: bool):
        final_enable = self._config.osc_analog_channel_enable | {channel: enable}
        mask = 0
        if final_enable.get(0):
            mask |= 1
        if final_enable.get(1):
            mask |= 1 << 1
        if final_enable.get(2):
            mask |= 1 << 2
        if final_enable.get(3):
            mask |= 1 << 3
        if final_enable.get(4):
            mask |= 1 << 4
        if final_enable.get(5):
            mask |= 1 << 5
        if final_enable.get(6):
            mask |= 1 << 6
        if final_enable.get(7):
            mask |= 1 << 7
        if final_enable.get(8):
            mask |= 1 << 8
        payload = struct.pack(">I", mask)
        self._logger.debug(f"Scrat analog_channel_enable payload: {payload.hex()}")
        status, res = self.send_with_command(CommonCommands.OSC_ANALOG_CHANNEL_ENABLE, payload=payload)
        if status != protocol.STATUS_OK:
            self._logger.error(f"Receive status code error [{status}]")
        else:
            self._config.osc_analog_channel_enable = final_enable

    def osc_set_analog_coupling(self, channel: int, coupling: int):
        final_coupling = self._config.osc_analog_coupling | {channel: coupling}
        enable = 0
        if final_coupling.get(0):
            enable |= 1
        if final_coupling.get(1):
            enable |= 1 << 1
        if final_coupling.get(2):
            enable |= 1 << 2
        if final_coupling.get(3):
            enable |= 1 << 3
        if final_coupling.get(4):
            enable |= 1 << 4
        if final_coupling.get(5):
            enable |= 1 << 5
        if final_coupling.get(6):
            enable |= 1 << 6
        if final_coupling.get(7):
            enable |= 1 << 7
        if final_coupling.get(8):
            enable |= 1 << 8

        payload = struct.pack(">I", enable)
        self._logger.debug(f"scrat_analog_coupling payload: {payload.hex()}")

        status, res = self.send_with_command(CommonCommands.OSC_ANALOG_COUPLING, payload=payload)
        if status != protocol.STATUS_OK:
            self._logger.error(f"Receive status code error [{status}]")
        else:
            self._config.osc_analog_coupling = final_coupling

    def osc_set_analog_voltage(self, channel: int, voltage: int):
        payload = struct.pack(">BI", channel, voltage)
        self._logger.debug(f"scrat_analog_coupling payload: {payload.hex()}")
        status, res = self.send_with_command(CommonCommands.OSC_ANALOG_VOLTAGE, payload=payload)
        if status != protocol.STATUS_OK:
            self._logger.error(f"Receive status code error [{status}]")
        else:
            self._config.osc_analog_voltage[channel] = voltage

    def osc_set_analog_bias_voltage(self, channel: int, voltage: int):
        payload = struct.pack(">BI", channel, voltage)
        self._logger.debug(f"scrat_analog_bias_voltage payload: {payload.hex()}")
        status, res = self.send_with_command(CommonCommands.OSC_ANALOG_BIAS_VOLTAGE, payload=payload)
        if status != protocol.STATUS_OK:
            self._logger.error(f"Receive status code error [{status}]")
        else:
            self._config.osc_analog_bias_voltage[channel] = voltage

    def osc_set_digital_channel_enable(self, channel: int, enable: bool):
        final_enable = self._config.osc_digital_channel_enable | {channel: enable}
        mask = 0
        if final_enable.get(0):
            mask |= 1
        if final_enable.get(1):
            mask |= 1 << 1
        if final_enable.get(2):
            mask |= 1 << 2
        if final_enable.get(3):
            mask |= 1 << 3
        if final_enable.get(4):
            mask |= 1 << 4
        if final_enable.get(5):
            mask |= 1 << 5
        if final_enable.get(6):
            mask |= 1 << 6
        if final_enable.get(7):
            mask |= 1 << 7
        if final_enable.get(8):
            mask |= 1 << 8
        payload = struct.pack(">I", mask)
        self._logger.debug(f"scrat_digital_channel_enable payload: {payload.hex()}")
        status, res = self.send_with_command(CommonCommands.OSC_DIGITAL_CHANNEL_ENABLE, payload=payload)
        if status != protocol.STATUS_OK:
            self._logger.error(f"Receive status code error [{status}]")
        else:
            self._config.osc_digital_channel_enable = final_enable

    def osc_set_digital_voltage(self, voltage: int):
        payload = struct.pack(">I", voltage)
        self._logger.debug(f"scrat_digital_voltage payload: {payload.hex()}")
        status, res = self.send_with_command(CommonCommands.OSC_DIGITAL_VOLTAGE, payload=payload)
        if status != protocol.STATUS_OK:
            self._logger.error(f"Receive status code error [{status}]")
        else:
            self._config.osc_digital_voltage = voltage

    def osc_set_trigger_mode(self, mode: int):
        payload = struct.pack(">B", mode)
        self._logger.debug(f"scrat_trigger_mode payload: {payload.hex()}")
        status, res = self.send_with_command(CommonCommands.OSC_TRIGGER_MODE, payload=payload)
        if status != protocol.STATUS_OK:
            self._logger.error(f"Receive status code error [{status}]")
        else:
            self._config.osc_trigger_mode = mode

    def osc_set_analog_trigger_source(self, source: int):
        payload = struct.pack(">B", source)
        self._logger.debug(f"scrat_analog_trigger_source payload: {payload.hex()}")
        status, res = self.send_with_command(CommonCommands.OSC_ANALOG_TRIGGER_SOURCE, payload=payload)
        if status != protocol.STATUS_OK:
            self._logger.error(f"Receive status code error [{status}]")
        else:
            self._config.osc_analog_trigger_source = source

    def osc_set_digital_trigger_source(self, channel: int):
        payload = struct.pack(">B", channel)
        self._logger.debug(f"scrat_digital_trigger_source payload: {payload.hex()}")
        status, res = self.send_with_command(CommonCommands.OSC_DIGITAL_TRIGGER_SOURCE, payload=payload)
        if status != protocol.STATUS_OK:
            self._logger.error(f"Receive status code error [{status}]")
        else:
            self._config.osc_digital_trigger_source = channel

    def osc_set_trigger_edge(self, edge: int | str):
        if isinstance(edge, str):
            if edge == "up":
                edge = 0
            elif edge == "down":
                edge = 1
            elif edge == "either":
                edge = 2
            else:
                raise ValueError(f"Unknown edge type: {edge}")
        elif isinstance(edge, int):
            if edge not in (0, 1, 2):
                raise ValueError(f"Unknown edge type: {edge}")
        payload = struct.pack(">B", edge)
        self._logger.debug(f"scrat_analog_trigger_edge payload: {payload.hex()}")
        status, res = self.send_with_command(CommonCommands.OSC_TRIGGER_EDGE, payload=payload)
        if status != protocol.STATUS_OK:
            self._logger.error(f"Receive status code error [{status}]")
        else:
            self._config.osc_analog_trigger_edge = edge

    def osc_set_trigger_edge_level(self, edge_level: int):
        payload = struct.pack(">H", edge_level)
        self._logger.debug(f"scrat_analog_trigger_edge_level payload: {payload.hex()}")
        status, res = self.send_with_command(CommonCommands.OSC_TRIGGER_EDGE_LEVEL, payload=payload)
        if status != protocol.STATUS_OK:
            self._logger.error(f"Receive status code error [{status}]")
        else:
            self._config.osc_analog_trigger_edge_level = edge_level

    def osc_set_analog_trigger_voltage(self, voltage: int):
        payload = struct.pack(">I", voltage)
        self._logger.debug(f"scrat_analog_trigger_voltage payload: {payload.hex()}")
        status, res = self.send_with_command(CommonCommands.OSC_ANALOG_TRIGGER_VOLTAGE, payload=payload)
        if status != protocol.STATUS_OK:
            self._logger.error(f"Receive status code error [{status}]")
        else:
            self._config.osc_analog_trigger_voltage = voltage

    def osc_set_sample_delay(self, delay: int):
        payload = struct.pack(">i", delay)
        self._logger.debug(f"osc_sample_delay payload: {payload.hex()}")
        status, res = self.send_with_command(CommonCommands.OSC_SAMPLE_DELAY, payload=payload)
        if status != protocol.STATUS_OK:
            self._logger.error(f"Receive status code error [{status}]")
        else:
            self._config.osc_sample_delay = delay

    def osc_set_sample_len(self, length: int):
        payload = struct.pack(">I", length)
        self._logger.debug(f"osc_set_sample_len payload: {payload.hex()}")
        status, res = self.send_with_command(CommonCommands.OSC_SAMPLE_LENGTH, payload=payload)
        if status != protocol.STATUS_OK:
            self._logger.error(f"Receive status code error [{status}]")
        else:
            self._config.osc_sample_len = length

    def osc_set_sample_rate(self, rate: int):
        """
        Set osc sample rate
        :param rate: The sample rate in kHz
        """
        payload = struct.pack(">I", rate)
        self._logger.debug(f"osc_set_sample_rate payload: {payload.hex()}")
        status, res = self.send_with_command(CommonCommands.OSC_SAMPLE_RATE, payload=payload)
        if status != protocol.STATUS_OK:
            self._logger.error(f"Receive status code error [{status}]")
        else:
            self._config.osc_sample_rate = rate

    def osc_single(self):
        payload = None
        self._logger.debug("scrat_sample_len payload: %s", payload)
        status, res = self.send_with_command(CommonCommands.OSC_SINGLE, payload=payload)
        if status != protocol.STATUS_OK:
            self._logger.error(f"Receive status code error [{status}]")

    def osc_is_triggered(self):
        payload = None
        self._logger.debug(f"scrat_is_triggered payload: {payload}")
        status, res = self.send_with_command(CommonCommands.OSC_IS_TRIGGERED, payload=payload)
        if status != protocol.STATUS_OK:
            self._logger.error(f"Receive status code error [{status}]")
            return False
        else:
            res_code = int.from_bytes(res, "big")
            return res_code == 4

    def osc_get_analog_wave(self, channel: int, offset: int, sample_count: int) -> np.ndarray:
        payload = struct.pack(">BII", channel, offset, sample_count)
        self._logger.debug(f"scrat_get_analog_wave payload: {payload.hex()}")
        status, wave_bytes = self.send_with_command(CommonCommands.OSC_GET_ANALOG_WAVES, payload=payload)
        if status != protocol.STATUS_OK:
            self._logger.error(f"Receive status code error [{status}]")
            return np.array([])
        else:
            if wave_bytes is None:
                return np.array([])
            else:
                wave = struct.unpack(f"{sample_count}h", wave_bytes)
                return np.array(wave, dtype=np.int16)

    def osc_get_digital_wave(self, channel: int, offset: int, sample_count: int):
        payload = struct.pack(">BII", channel, offset, sample_count)
        self._logger.debug(f"scrat_get_digital_wave payload: {payload.hex()}")
        status, wave_bytes = self.send_with_command(CommonCommands.OSC_GET_ANALOG_WAVES, payload=payload)
        if status != protocol.STATUS_OK:
            self._logger.error(f"Receive status code error [{status}]")
            return np.array([])
        else:
            if wave_bytes is None:
                return np.array([])
            else:
                wave = struct.unpack(f"{sample_count}h", wave_bytes)
                return np.array(wave, dtype=np.int16)

    def osc_set_analog_gain(self, channel: int, gain: int):
        payload = struct.pack(">BB", channel, gain)
        self._logger.debug(f"scrat_analog_gain payload: {payload.hex()}")
        status, res = self.send_with_command(CommonCommands.OSC_ANALOG_GAIN, payload=payload)
        if status != protocol.STATUS_OK:
            self._logger.error(f"Receive status code error [{status}]")
        else:
            self._config.osc_analog_gain[channel] = gain

    def osc_set_analog_gain_raw(self, channel: int, gain: int):
        payload = struct.pack(">BB", channel, gain)
        self._logger.debug(f"scrat_analog_gain payload: {payload.hex()}")
        status, res = self.send_with_command(CommonCommands.OSC_ANALOG_GAIN_RAW, payload=payload)
        if status != protocol.STATUS_OK:
            self._logger.error(f"Receive status code error [{status}]")
        else:
            self._config.osc_analog_gain_raw[channel] = gain

    def osc_force(self):
        payload = None
        self._logger.debug(f"scrat_force payload: {payload}")
        status, res = self.send_with_command(CommonCommands.OSC_FORCE, payload=payload)
        if status != protocol.STATUS_OK:
            self._logger.error(f"Receive status code error [{status}]")

    def osc_set_clock_base_freq_mul_div(self, mult_int: int, mult_fra: int, div: int):
        payload = struct.pack(">BHB", mult_int, mult_fra, div)
        self._logger.debug(f"osc_set_clock_base_freq_mul_div payload: {payload.hex()}")
        status, res = self.send_with_command(CommonCommands.OSC_CLOCK_BASE_FREQ_MUL_DIV, payload=payload)
        if status != protocol.STATUS_OK:
            self._logger.error(f"Receive status code error [{status}]")
        else:
            self._config.osc_clock_base_freq_mul_div = mult_int, mult_fra, div

    def osc_set_sample_divisor(self, div_int: int, div_frac: int):
        payload = struct.pack(">BH", div_int, div_frac)
        self._logger.debug(f"osc_set_sample_divisor payload: {payload.hex()}")
        status, res = self.send_with_command(CommonCommands.OSC_CLOCK_SAMPLE_DIVISOR, payload=payload)
        if status != protocol.STATUS_OK:
            self._logger.error(f"Receive status code error [{status}]")
        else:
            self._config.osc_clock_sample_divisor = div_int, div_frac

    def osc_set_clock_update(self):
        self._logger.debug(f"osc_set_clock_update payload: {None}")
        status, res = self.send_with_command(CommonCommands.OSC_CLOCK_UPDATE, payload=None)
        if status != protocol.STATUS_OK:
            self._logger.error(f"Receive status code error [{status}]")

    def osc_set_clock_simple(self, nut_clk: int, mult: int, phase: int):
        if not 1 <= nut_clk <= 32:
            raise ValueError("nut_clk must be between 1 and 32")
        if nut_clk * mult > 32:
            raise ValueError("nut_clk * mult must be less than 32")
        payload = struct.pack(">BBI", nut_clk, mult, phase * 1000)
        self._logger.debug(f"osc_set_clock_simple payload: {payload.hex()}")
        status, res = self.send_with_command(CommonCommands.OSC_CLOCK_SIMPLE, payload=payload)
        if status != protocol.STATUS_OK:
            self._logger.error(f"Receive status code error [{status}]")
        else:
            self._config.osc_clock_simple = nut_clk, mult, phase

    def osc_set_sample_phase(self, phase: int):
        payload = struct.pack(">I", phase)
        self._logger.debug(f"osc_set_sample_phase payload: {payload.hex()}")
        status, res = self.send_with_command(CommonCommands.OSC_CLOCK_SAMPLE_PHASE, payload=payload)
        if status != protocol.STATUS_OK:
            self._logger.error(f"Receive status code error [{status}]")
        else:
            self._config.osc_sample_phase = phase

    def nut_set_enable(self, enable: int | bool):
        if isinstance(enable, bool):
            enable = 1 if enable else 0
        payload = struct.pack(">B", enable)
        self._logger.debug(f"cracker_nut_enable payload: {payload.hex()}")
        status, res = self.send_with_command(CommonCommands.NUT_ENABLE, payload=payload)
        if status != protocol.STATUS_OK:
            self._logger.error(f"Receive status code error [{status}]")
        else:
            self._config.nut_enable = enable

    def nut_set_voltage(self, voltage: int):
        payload = struct.pack(">I", voltage)
        self._logger.debug(f"cracker_nut_voltage payload: {payload.hex()}")
        status, res = self.send_with_command(CommonCommands.NUT_VOLTAGE, payload=payload)
        if status != protocol.STATUS_OK:
            self._logger.error(f"Receive status code error [{status}]")
        else:
            self._config.nut_voltage = voltage

    def nut_set_voltage_raw(self, voltage: int):
        payload = struct.pack(">B", voltage)
        self._logger.debug(f"cracker_nut_voltage payload: {payload.hex()}")
        status, res = self.send_with_command(CommonCommands.NUT_VOLTAGE_RAW, payload=payload)
        if status != protocol.STATUS_OK:
            self._logger.error(f"Receive status code error [{status}]")
        else:
            self._config.nut_voltage_raw = voltage

    def nut_set_clock(self, clock: int):
        """
        Set nut clock.
        :param clock: The clock of the nut in kHz
        :type clock: int
        """
        payload = struct.pack(">I", clock)
        self._logger.debug(f"cracker_nut_clock payload: {payload.hex()}")
        status, res = self.send_with_command(CommonCommands.NUT_CLOCK, payload=payload)
        if status != protocol.STATUS_OK:
            self._logger.error(f"Receive status code error [{status}]")
        else:
            self._config.nut_clock = clock

    def nut_set_interface(self, interface: int):
        payload = struct.pack(">I", interface)
        self._logger.debug(f"cracker_nut_interface payload: {payload.hex()}")
        status, res = self.send_with_command(CommonCommands.NUT_INTERFACE, payload=payload)
        if status != protocol.STATUS_OK:
            self._logger.error(f"Receive status code error [{status}]")
        else:
            self._config.nut_interface = interface

    def nut_set_timeout(self, timeout: int):
        payload = struct.pack(">I", timeout)
        self._logger.debug(f"cracker_nut_timeout payload: {payload.hex()}")
        status, res = self.send_with_command(CommonCommands.NUT_TIMEOUT, payload=payload)
        if status != protocol.STATUS_OK:
            self._logger.error(f"Receive status code error [{status}]")
        else:
            self._config.nut_timeout = timeout

    def set_clock_nut_divisor(self, div: int):
        payload = struct.pack(">B", div)
        self._logger.debug(f"set_clock_nut_divisor payload: {payload.hex()}")
        status, res = self.send_with_command(CommonCommands.OSC_CLOCK_NUT_DIVISOR, payload=payload)
        if status != protocol.STATUS_OK:
            self._logger.error(f"Receive status code error [{status}]")
        else:
            self._config.osc_clock_divisor = div

    def _spi_transceive(
        self, data: bytes | str | None, is_delay: bool, delay: int, rx_count: int, is_trigger: bool
    ) -> bytes | None:
        """
        Basic interface for sending and receiving data through the SPI protocol.

        :param data: The data to send.
        :param is_delay: Whether the transmit delay is enabled.
        :type is_delay: bool
        :param delay: The transmit delay in milliseconds, with a minimum effective duration of 10 nanoseconds.
        :type delay: int
        :param rx_count: The number of received data bytes.
        :type rx_count: int
        :param is_trigger: Whether the transmit trigger is enabled.
        :type is_trigger: bool
        :return: The data received from the SPI device. Return None if an exception is caught.
        :rtype: bytes | None
        """
        if isinstance(data, str):
            data = bytes.fromhex(data)
        payload = struct.pack(">?IH?", is_delay, delay, rx_count, is_trigger)
        if data is not None:
            payload += data
        self._logger.debug(f"_spi_transceive payload: {payload.hex()}")
        status, res = self.send_with_command(CommonCommands.SPI_TRANSCEIVE, payload=payload)
        if status != protocol.STATUS_OK:
            self._logger.error(f"Receive status code error [{status}]")
            return None
        else:
            return res

    def spi_transmit(self, data: bytes | str, is_trigger: bool = False):
        """
        Send data through the SPI protocol.

        :param data: The data to send.
        :type data: str | bytes
        :param is_trigger: Whether the transmit trigger is enabled.
        :type is_trigger: bool
        """
        return self._spi_transceive(data, is_delay=False, delay=1_000_000_000, rx_count=0, is_trigger=is_trigger)

    def spi_receive(self, rx_count: int, is_trigger: bool = False) -> bytes | None:
        """
        Receive data through the SPI protocol.

        :param rx_count: The number of received data bytes.
        :type rx_count: int
        :param is_trigger: Whether the transmit trigger is enabled.
        :type is_trigger: bool
        :return: The data received from the SPI device. Return None if an exception is caught.
        :rtype: bytes | None
        """
        return self._spi_transceive(None, is_delay=False, delay=1_000_000_000, rx_count=rx_count, is_trigger=is_trigger)

    def spi_transmit_delay_receive(
        self, data: bytes | str, delay: int, rx_count: int, is_trigger: bool = False
    ) -> bytes | None:
        """
        Send and receive data with delay through the SPI protocol.

        :param data: The data to send.
        :type data: str | bytes
        :param delay: The transmit delay in milliseconds, with a minimum effective duration of 10 nanoseconds.
        :type delay: int
        :param rx_count: The number of received data bytes.
        :type rx_count: int
        :param is_trigger: Whether the transmit trigger is enabled.
        :type is_trigger: bool
        :return: The data received from the SPI device. Return None if an exception is caught.
        :rtype: bytes | None
        """
        return self._spi_transceive(data, is_delay=True, delay=delay, rx_count=rx_count, is_trigger=is_trigger)

    def spi_transceive(self, data: bytes | str, rx_count: int, is_trigger: bool = False) -> bytes | None:
        """
        Send and receive data without delay through the SPI protocol.

        :param data: The data to send.
        :type data: str | bytes
        :param rx_count: The number of received data bytes.
        :type rx_count: int
        :param is_trigger: Whether the transmit trigger is enabled.
        :type is_trigger: bool
        :return: The data received from the SPI device. Return None if an exception is caught.
        :rtype: bytes | None
        """
        return self._spi_transceive(data, is_delay=False, delay=0, rx_count=rx_count, is_trigger=is_trigger)

    def _i2c_transceive(
        self,
        addr: str | int,
        data: bytes | str | None,
        speed: int,
        combined_transfer_count_1: int,
        combined_transfer_count_2: int,
        transfer_rw: tuple[int, int, int, int, int, int, int, int],
        transfer_lens: tuple[int, int, int, int, int, int, int, int],
        is_delay: bool,
        delay: int,
        is_trigger: bool,
    ) -> bytes | None:
        """
        Basic API for sending and receiving data through the I2C protocol.

        :param addr: I2C device address, 7-bit length.
        :type addr: str | int
        :param data: The data to be sent.
        :type data: bytes | str | None
        :param speed: Transmit speed. 0：100K bit/s, 1：400K bit/s, 2：1M bit/s, 3：3.4M bit/s, 4：5M bit/s.
        :type speed: int
        :param combined_transfer_count_1: The first combined transmit transfer count.
        :type combined_transfer_count_1: int
        :param combined_transfer_count_2: The second combined transmit transfer count.
        :type combined_transfer_count_2: int
        :param transfer_rw: The read/write configuration tuple of the four transfers in the two sets
                            of Combined Transfer, with a tuple length of 8, where 0 represents write
                            and 1 represents read.
        :type transfer_rw: tuple[int, int, int, int, int, int, int, int, int]
        :param transfer_lens: The transfer length tuple of the four transfers in the two combined transmit sets.
        :param is_delay: Whether the transmit delay is enabled.
        :type is_delay: bool
        :param delay: Transmit delay duration, in nanoseconds, with a minimum effective duration of 10 nanoseconds.
        :type delay: int
        :param is_trigger: Whether the transmit trigger is enabled.
        :type is_trigger: bool
        :return: The data received from the I2C device. Return None if an exception is caught.
        :rtype: bytes | None
        """
        if isinstance(addr, str):
            addr = int(addr, 16)

        if addr > (1 << 7) - 1:
            raise ValueError("Illegal address")

        if isinstance(data, str):
            data = bytes.fromhex(data)

        if speed > 4:
            raise ValueError("Illegal speed")

        if combined_transfer_count_1 > 4:
            raise ValueError("Illegal combined combined_transfer_count_1")
        if combined_transfer_count_2 > 4:
            raise ValueError("Illegal combined combined_transfer_count_2")

        if len(transfer_rw) != 8:
            raise ValueError("transfer_rw length must be 8")
        if len(transfer_lens) != 8:
            raise ValueError("transfer_lens length must be 8")

        transfer_rw_num = sum(bit << (7 - i) for i, bit in enumerate(transfer_rw))

        payload = struct.pack(
            ">?I5B8H?",
            is_delay,
            delay,
            addr,
            speed,
            combined_transfer_count_1,
            combined_transfer_count_2,
            transfer_rw_num,
            *transfer_lens,
            is_trigger,
        )

        if data is not None:
            payload += data
        status, res = self.send_with_command(CommonCommands.CRACKER_I2C_TRANSCEIVE, payload=payload)
        if status != protocol.STATUS_OK:
            self._logger.error(f"Receive status code error [{status}]")
            return None
        else:
            return res

    def i2c_transmit(self, addr: str | int, data: bytes | str, is_trigger: bool = False):
        """
        Send data through the I2C protocol.

        :param addr: I2C device address, 7-bit length.
        :type addr: str | int
        :param data: The data to be sent.
        :type data: str | bytes
        :param is_trigger: Whether the transmit trigger is enabled.
        """
        transfer_rw = (0, 0, 0, 0, 0, 0, 0, 0)
        transfer_lens = (len(data), 0, 0, 0, 0, 0, 0, 0)
        self._i2c_transceive(
            addr,
            data,
            speed=0,
            combined_transfer_count_1=1,
            combined_transfer_count_2=0,
            transfer_rw=transfer_rw,
            transfer_lens=transfer_lens,
            is_delay=False,
            delay=0,
            is_trigger=is_trigger,
        )

    def i2c_receive(self, addr: str | int, rx_count, is_trigger: bool = False) -> bytes | None:
        """
        Receive data through the I2C protocol.

        :param addr: I2C device address, 7-bit length.
        :type addr: str | int
        :param rx_count: The number of received data bytes.
        :type rx_count: int
        :param is_trigger: Whether the transmit trigger is enabled.
        :return: The data received from the I2C device. Return None if an exception is caught.
        :rtype: bytes | None
        """
        transfer_rw = (1, 1, 1, 1, 1, 1, 1, 1)
        transfer_lens = (rx_count, 0, 0, 0, 0, 0, 0, 0)
        return self._i2c_transceive(
            addr,
            data=None,
            speed=0,
            combined_transfer_count_1=1,
            combined_transfer_count_2=0,
            transfer_rw=transfer_rw,
            transfer_lens=transfer_lens,
            is_delay=False,
            delay=0,
            is_trigger=is_trigger,
        )

    def i2c_transmit_delay_receive(
        self, addr: str | int, data: bytes | str, delay: int, rx_count: int, is_trigger: bool = False
    ) -> bytes | None:
        """
        Send and receive data with delay through the I2C protocol.

        :param addr: I2C device address, 7-bit length.
        :type addr: str | int
        :param data: The data to be sent.
        :type data: str | bytes
        :param delay: Transmit delay duration, in nanoseconds, with a minimum effective duration of 10 nanoseconds.
        :type delay: int
        :param rx_count: The number of received data bytes.
        :type rx_count: int
        :param is_trigger: Whether the transmit trigger is enabled.
        :type is_trigger: bool
        :return: The data received from the I2C device. Return None if an exception is caught.
        :rtype: bytes | None
        """
        transfer_rw = (0, 0, 0, 0, 1, 1, 1, 1)
        transfer_lens = (len(data), 0, 0, 0, rx_count, 0, 0, 0)
        return self._i2c_transceive(
            addr,
            data,
            speed=0,
            combined_transfer_count_1=1,
            combined_transfer_count_2=1,
            transfer_rw=transfer_rw,
            transfer_lens=transfer_lens,
            is_delay=True,
            delay=delay,
            is_trigger=is_trigger,
        )

    def i2c_transceive(self, addr, data, rx_count, is_trigger: bool = False) -> bytes | None:
        """
        Send and receive data without delay through the I2C protocol.

        :param addr: I2C device address, 7-bit length.
        :type addr: str | int
        :param data: The data to be sent.
        :type data: str | bytes
        :param rx_count: The number of received data bytes.
        :type rx_count: int
        :param is_trigger: Whether the transmit trigger is enabled.
        :type is_trigger: bool
        :return: The data received from the I2C device. Return None if an exception is caught.
        :rtype: bytes | None
        """
        transfer_rw = (0, 0, 0, 0, 1, 1, 1, 1)
        transfer_lens = (len(data), 0, 0, 0, rx_count, 0, 0, 0)
        return self._i2c_transceive(
            addr,
            data,
            speed=0,
            combined_transfer_count_1=1,
            combined_transfer_count_2=1,
            transfer_rw=transfer_rw,
            transfer_lens=transfer_lens,
            is_delay=False,
            delay=0,
            is_trigger=is_trigger,
        )

    def cracker_serial_baud(self, baud: int):
        payload = struct.pack(">I", baud)
        self._logger.debug(f"cracker_serial_baud payload: {payload.hex()}")
        status, res = self.send_with_command(CommonCommands.CRACKER_SERIAL_BAUD, payload=payload)
        if status != protocol.STATUS_OK:
            self._logger.error(f"Receive status code error [{status}]")
            return None
        else:
            return res

    def cracker_serial_width(self, width: int):
        payload = struct.pack(">B", width)
        self._logger.debug(f"cracker_serial_width payload: {payload.hex()}")
        status, res = self.send_with_command(CommonCommands.CRACKER_SERIAL_WIDTH, payload=payload)
        if status != protocol.STATUS_OK:
            self._logger.error(f"Receive status code error [{status}]")
            return None
        else:
            return res

    def cracker_serial_stop(self, stop: int):
        payload = struct.pack(">B", stop)
        self._logger.debug(f"cracker_serial_stop payload: {payload.hex()}")
        status, res = self.send_with_command(CommonCommands.CRACKER_SERIAL_STOP, payload=payload)
        if status != protocol.STATUS_OK:
            self._logger.error(f"Receive status code error [{status}]")
            return None
        else:
            return res

    def cracker_serial_odd_eve(self, odd_eve: int):
        payload = struct.pack(">B", odd_eve)
        self._logger.debug(f"cracker_serial_odd_eve payload: {payload.hex()}")
        status, res = self.send_with_command(CommonCommands.CRACKER_SERIAL_ODD_EVE, payload=payload)
        if status != protocol.STATUS_OK:
            self._logger.error(f"Receive status code error [{status}]")
            return None
        else:
            return res

    def cracker_serial_data(self, expect_len: int, data: bytes | str):
        if isinstance(data, str):
            data = bytes.fromhex(data)
        payload = struct.pack(">I", expect_len)
        payload += data
        self._logger.debug(f"cracker_serial_data payload: {payload.hex()}")
        status, res = self.send_with_command(CommonCommands.CRACKER_SERIAL_DATA, payload=payload)
        if status != protocol.STATUS_OK:
            self._logger.error(f"Receive status code error [{status}]")
            return None
        else:
            return res

    def cracker_spi_cpol(self, cpol: int):
        payload = struct.pack(">B", cpol)
        self._logger.debug(f"cracker_spi_cpol payload: {payload.hex()}")
        status, res = self.send_with_command(CommonCommands.CRACKER_SPI_CPOL, payload=payload)
        if status != protocol.STATUS_OK:
            self._logger.error(f"Receive status code error [{status}]")
            return None
        else:
            return res

    def cracker_spi_cpha(self, cpha: int):
        payload = struct.pack(">B", cpha)
        self._logger.debug(f"cracker_spi_cpha payload: {payload.hex()}")
        status, res = self.send_with_command(CommonCommands.CRACKER_SPI_CPHA, payload=payload)
        if status != protocol.STATUS_OK:
            self._logger.error(f"Receive status code error [{status}]")
            return None
        else:
            return res

    def cracker_spi_data_len(self, length: int):
        payload = struct.pack(">B", length)
        self._logger.debug(f"cracker_spi_data_len payload: {payload.hex()}")
        status, res = self.send_with_command(CommonCommands.CRACKER_SPI_DATA_LEN, payload=payload)
        if status != protocol.STATUS_OK:
            self._logger.error(f"Receive status code error [{status}]")
            return None
        else:
            return res

    def cracker_spi_freq(self, freq: int):
        payload = struct.pack(">B", freq)
        self._logger.debug(f"cracker_spi_freq payload: {payload.hex()}")
        status, res = self.send_with_command(CommonCommands.CRACKER_SPI_FREQ, payload=payload)
        if status != protocol.STATUS_OK:
            self._logger.error(f"Receive status code error [{status}]")
            return None
        else:
            return res

    def cracker_spi_timeout(self, timeout: int):
        payload = struct.pack(">B", timeout)
        self._logger.debug(f"cracker_spi_timeout payload: {payload.hex()}")
        status, res = self.send_with_command(CommonCommands.CRACKER_SPI_TIMEOUT, payload=payload)
        if status != protocol.STATUS_OK:
            self._logger.error(f"Receive status code error [{status}]")
            return None
        else:
            return res

    def cracker_i2c_freq(self, freq: int):
        payload = struct.pack(">B", freq)
        self._logger.debug(f"cracker_i2c_freq payload: {payload.hex()}")
        status, res = self.send_with_command(CommonCommands.CRACKER_I2C_FREQ, payload=payload)
        if status != protocol.STATUS_OK:
            self._logger.error(f"Receive status code error [{status}]")
            return None
        else:
            return res

    def cracker_i2c_timeout(self, timeout: int):
        payload = struct.pack(">B", timeout)
        self._logger.debug(f"cracker_i2c_timeout payload: {payload.hex()}")
        status, res = self.send_with_command(CommonCommands.CRACKER_I2C_TIMEOUT, payload=payload)
        if status != protocol.STATUS_OK:
            self._logger.error(f"Receive status code error [{status}]")
            return None
        else:
            return res

    def cracker_i2c_data(self, expect_len: int, data: bytes):
        payload = struct.pack(">I", expect_len)
        payload += data
        self._logger.debug(f"cracker_i2c_data payload: {payload.hex()}")
        status, res = self.send_with_command(CommonCommands.CRACKER_I2C_TRANSCEIVE, payload=payload)
        if status != protocol.STATUS_OK:
            self._logger.error(f"Receive status code error [{status}]")
            return None
        else:
            return res

    def cracker_can_freq(self, freq: int):
        payload = struct.pack(">B", freq)
        self._logger.debug(f"cracker_can_freq payload: {payload.hex()}")
        status, res = self.send_with_command(CommonCommands.CRACKER_CAN_FREQ, payload=payload)
        if status != protocol.STATUS_OK:
            self._logger.error(f"Receive status code error [{status}]")
            return None
        else:
            return res

    def cracker_can_timeout(self, timeout: int):
        payload = struct.pack(">B", timeout)
        self._logger.debug(f"cracker_can_timeout payload: {payload.hex()}")
        status, res = self.send_with_command(CommonCommands.CRACKER_CAN_TIMEOUT, payload=payload)
        if status != protocol.STATUS_OK:
            self._logger.error(f"Receive status code error [{status}]")
            return None
        else:
            return res

    def cracker_can_data(self, expect_len: int, data: bytes):
        payload = struct.pack(">I", expect_len)
        payload += data
        self._logger.debug(f"cracker_can_data payload: {payload.hex()}")
        status, res = self.send_with_command(CommonCommands.CRACKER_CA_DATA, payload=payload)
        if status != protocol.STATUS_OK:
            self._logger.error(f"Receive status code error [{status}]")
            return None
        else:
            return res
