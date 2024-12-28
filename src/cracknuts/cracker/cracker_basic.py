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


class ConfigBasic:
    def __init__(self):
        # The name list of fields whose value type is dict[int, Any]. When converting to a dictionary from JSON,
        # numbers are converted to strings, so this needs to be handled separately. The subclass should overwrite
        # this field when its field has a similar structure.
        self.int_dict_fields = ()

    def __str__(self):
        return f"Config({", ".join([f"{k}: {v}" for k, v in self.__dict__.items() if not k.startswith("_")])})"

    def __repr__(self):
        return self.__str__()

    def dump_to_json(self) -> str:
        """
        Dump the configuration to a JSON string.

        """
        return json.dumps({k: v for k, v in self.__dict__.items() if k != "_binder"})

    def load_from_json(self, json_str: str) -> "ConfigBasic":
        """
        Load configuration from a JSON string. If a value in the JSON string is null, it will be skipped,
        and the default configuration will be used.

        """
        for k, v in json.loads(json_str).items():
            if k in self.int_dict_fields:
                v = {int(_k): _v for _k, _v in v.items()}
            if v is not None:
                self.__dict__[k] = v
        return self


T = typing.TypeVar("T", bound=ConfigBasic)


class CrackerBasic(ABC, typing.Generic[T]):
    """
    The basic device class, provides support for the `CNP` protocol, configuration management, firmware maintenance,
    and other basic operations.

    For firmware updates, in the `Cracker` architecture, the host computer will attempt to update the latest firmware
    files from the following directories each time it connects to the device:

    - The directory carried by the current package: <site-packages>/cracknuts/bin
    - The user directory: ~/.cracknuts/bin
    - The working directory: <work-directory>/.bin

    Users can obtain the latest firmware by updating `cracknuts`. After downloading the latest firmware from the
    official website, simply place it in the working directory or user directory.

    """

    def __init__(
        self,
        address: tuple | str | None = None,
        bin_server_path: str | None = None,
        bin_bitstream_path: str | None = None,
        operator_port: int = None,
    ):
        """
        :param address: Cracker device address (ip, port) or "[cnp://]<ip>[:port]",
                        If no configuration is provided here,
                        it needs to be configured later by calling `set_address`, `set_ip_port`, or `set_uri`.
        :type address: str | tuple | None
        :param bin_server_path: The bin_server (firmware) file for updates; normally, the user should not specify this.
        :type bin_server_path: str | None
        :param bin_bitstream_path: The bin_bitstream (firmware) file for updates; normally,
                                   the user should not specify this.
        :type bin_bitstream_path: str | None
        :param operator_port: The operator port to connect to.
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

    def set_address(self, address: tuple[str, int] | str) -> None:
        """
        Set the device address in tuple format.

        :param address: address in tuple format: (ip, port).
        :type address: tuple[str, int]
        :return: None
        """
        if isinstance(address, tuple):
            self._server_address = address
        elif isinstance(address, str):
            self.set_uri(address)

    def get_address(self) -> tuple[str, int]:
        """
        Get the device address in tuple format.

        :return: address in tuple format: (ip, port).
        :rtype: tuple[str, int]
        """
        return self._server_address

    def set_ip_port(self, ip, port) -> None:
        """
        Set the device IP address.

        :param ip: IP address.
        :type ip: str
        :param port: Port.
        :type port: int
        :return: None
        """
        self._server_address = ip, port

    def set_uri(self, uri: str) -> None:
        """
        Set the device address in URI format.

        :param uri: URI.
        :type uri: str
        :return: None
        """
        if not uri.startswith("cnp://") and uri.count(":") < 2:
            uri = "cnp://" + uri

        uri = uri.replace("cnp://", "", 1)
        if ":" in uri:
            host, port = uri.split(":")
        else:
            host, port = uri, protocol.DEFAULT_PORT  # type: ignore

        self._server_address = host, int(port)

    def get_uri(self) -> str | None:
        """
        Get the device address in URI format.

        :return: URI. if cracker address is not specified, None is returned.
        :rtype: str | None
        """
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
        update_unknown: bool = False,
    ) -> None:
        """
        Connect to cracker device.

        :param update_bin: Whether to update the firmware.
        :type update_bin: bool
        :param force_update_bin: Whether to force update the firmware while the device is running normally
                          (by default, firmware updates are not performed when the device is running normally).
        :type force_update_bin: bool
        :param bin_server_path: The bin_server (firmware) file for updates.
        :type bin_server_path: str | None
        :param bin_bitstream_path: The bin_bitstream (firmware) file for updates.
        :type bin_bitstream_path: str | None
        :param update_unknown: Whether to update the unknown firmware.
        :type update_unknown: bool
        :return: None
        """
        if bin_server_path is None:
            bin_server_path = self._bin_server_path
        if bin_bitstream_path is None:
            bin_bitstream_path = self._bin_bitstream_path

        if update_bin and not self._update_cracker_bin(
            force_update_bin, bin_server_path, bin_bitstream_path, self._operator_port, update_unknown=update_unknown
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
        update_unknown: bool = False,
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
        if hardware_model == "unknown" and update_unknown:
            hardware_model = "*"

        bin_path = os.path.join(cracknuts.__file__, "firmware")
        user_home_bin_path = os.path.join(os.path.expanduser("~"), ".cracknuts", "firmware")
        current_bin_path = os.path.join(os.getcwd(), ".firmware")

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

        if hardware_model == "*" and update_unknown:
            self._logger.warning(
                f"Equipment return unknown hardware: {hardware_model}, and update_unknown is True,"
                f"The firmware bitstream: {bin_bitstream_path} and server: {bin_server_path} is used."
            )
        else:
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
        if hardware_model == "*":
            dict_by_hardware = {k: v for d in bin_dict.values() for k, v in d.items()}
        else:
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
        server_path_pattern = r"server-(?P<hardware>.+?)-(?P<firmware>.+?).bin"
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

    def disconnect(self) -> None:
        """
        Disconnect from cracker device.

        :return: None
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
        Reconnect to cracker device.

        :return: None
        """
        self.disconnect()
        self.connect()

    def get_connection_status(self) -> bool:
        """
        Get connection status.

        :return: True for connected and False for disconnected.
        :rtype: bool
        """
        return self._connection_status

    def send_and_receive(self, message: bytes) -> tuple[int, bytes | None]:
        """
        Send message to cracker device.

        :param message: The byte message to send.
        :type message: bytes
        :return: Received message in format: (status, message).
        :rtype: tuple[int, bytes | None]
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
    def get_default_config(self) -> T:
        """
        Get the default configuration. This method needs to be implemented by the specific device class,
        as different devices have different default configurations.

        :return: The default config object(The specific subclass of CommonConfig).
        :rtype: ConfigBasic
        """
        ...

    def get_current_config(self) -> T:
        """
        Get current configuration of `Cracker`.
        Note: Currently, the configuration returned is recorded on the host computer,
        not the ACTUAL configuration of the device. In the future, it should be
        synchronized from the device to the host computer.

        :return: Current configuration of `Cracker`.
        :rtype: ConfigBasic
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
        :type path: str | None
        :return: the content of JSON string or None if no path is specified.
        :rtype: str | None
        """
        config_json = self._config.dump_to_json()
        if path is None:
            return config_json
        else:
            with open(path, "w") as f:
                f.write(config_json)

    def load_config_from_file(self, path: str) -> None:
        """
        Load config from a JSON file.

        :param path: the path to the JSON file
        :type path: str
        :return: None
        """
        with open(path) as f:
            self.load_config_from_str("".join(f.readlines()))

    def load_config_from_str(self, json_str: str) -> None:
        """
        Load config from a JSON string.

        :param json_str: the JSON string
        :type json_str: str
        :return: None
        """
        self._config.load_from_json(json_str)

    def get_id(self) -> str | None:
        status, res = self.send_with_command(protocol.Command.GET_ID)
        if status != protocol.STATUS_OK:
            self._logger.error(f"Receive status code error [{status}]")
        return res.decode("ascii") if res is not None else None

    def get_name(self) -> str | None:
        status, res = self.send_with_command(protocol.Command.GET_NAME)
        if status != protocol.STATUS_OK:
            self._logger.error(f"Receive status code error [{status}]")
        return res.decode("ascii") if res is not None else None

    def get_version(self) -> str | None:
        status, res = self.send_with_command(protocol.Command.GET_VERSION)
        if status != protocol.STATUS_OK:
            self._logger.error(f"Receive status code error [{status}]")
        return res.decode("ascii") if res is not None else None

    def osc_single(self):
        payload = None
        self._logger.debug("scrat_sample_len payload: %s", payload)
        status, res = self.send_with_command(protocol.Command.OSC_SINGLE, payload=payload)
        if status != protocol.STATUS_OK:
            self._logger.error(f"Receive status code error [{status}]")

    def osc_is_triggered(self):
        payload = None
        self._logger.debug(f"scrat_is_triggered payload: {payload}")
        status, res = self.send_with_command(protocol.Command.OSC_IS_TRIGGERED, payload=payload)
        if status != protocol.STATUS_OK:
            self._logger.error(f"Receive status code error [{status}]")
            return False
        else:
            res_code = int.from_bytes(res, "big")
            return res_code == 4

    def osc_get_analog_wave(self, channel: int, offset: int, sample_count: int) -> np.ndarray:
        payload = struct.pack(">BII", channel, offset, sample_count)
        self._logger.debug(f"scrat_get_analog_wave payload: {payload.hex()}")
        status, wave_bytes = self.send_with_command(protocol.Command.OSC_GET_ANALOG_WAVES, payload=payload)
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
        status, wave_bytes = self.send_with_command(protocol.Command.OSC_GET_ANALOG_WAVES, payload=payload)
        if status != protocol.STATUS_OK:
            self._logger.error(f"Receive status code error [{status}]")
            return np.array([])
        else:
            if wave_bytes is None:
                return np.array([])
            else:
                wave = struct.unpack(f"{sample_count}h", wave_bytes)
                return np.array(wave, dtype=np.int16)
