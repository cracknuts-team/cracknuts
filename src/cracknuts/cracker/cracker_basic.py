# Copyright 2024 CrackNuts. All rights reserved.

import abc
import importlib.util
import json
import logging
import os
import socket
import struct
import threading
import typing
from abc import ABC

import numpy as np

import cracknuts.utils.hex_util as hex_util
from cracknuts import logger
from cracknuts.cracker import protocol
from cracknuts.cracker.operator import Operator


class ConfigBasic:
    def __init__(self):
        self.osc_analog_channel_enable = {0: False, 1: True}
        self.osc_analog_gain = {0: 50, 1: 50}
        self.osc_sample_length = 1024
        self.osc_sample_delay = 0
        self.osc_sample_clock = 48000
        self.osc_sample_phase = 0
        self.osc_analog_trigger_source = 0
        self.osc_trigger_mode = 0
        self.osc_analog_trigger_edge = 0
        self.osc_analog_trigger_edge_level = 1
        self.osc_analog_coupling: dict[int, int] = {}
        self.osc_analog_voltage: dict[int, int] = {}
        self.osc_analog_bias_voltage: dict[int, int] = {}
        self.osc_digital_voltage: int | None = None
        self.osc_digital_trigger_source: int | None = None
        self.osc_analog_gain_raw: dict[int, int] = {}
        self.osc_clock_base_freq_mul_div: tuple[int, int, int] | None = None
        self.osc_clock_sample_divisor: tuple[int, int] | None = None
        self.osc_clock_simple: tuple[int, int, int] | None = None
        self.osc_clock_phase: int | None = None
        self.osc_clock_divisor: int | None = None
        # The name list of fields whose value type is dict[int, Any]. When converting to a dictionary from JSON,
        # numbers are converted to strings, so this needs to be handled separately. The subclass should overwrite
        # this field when its field has a similar structure.
        self.int_dict_fields = (
            "osc_analog_channel_enable",
            "osc_analog_coupling",
            "osc_analog_voltage",
            "osc_analog_bias_voltage",
            "osc_analog_gain",
            "osc_analog_gain_raw",
        )

    def __str__(self):
        return f"Config({", ".join([f"{k}: {v}" for k, v in self.__dict__.items() if not k.startswith("_")])})"

    def __repr__(self):
        return self.__str__()

    def dump_to_json(self) -> str:
        """
        Dump the configuration to a JSON string.

        """
        return json.dumps({k: v for k, v in self.__dict__.items() if (k != "_binder" and k != "int_dict_fields")})

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
    NON_PROTOCOL_ERROR = -1

    """
    The basic device class, provides support for the `CNP` protocol, configuration management, firmware maintenance,
    and other basic operations.

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
        self._logger_debug_payload_max_length = 512
        self._logger_info_payload_max_length = 16
        self._command_lock = threading.Lock()
        self._logger = logger.get_logger(self)
        self._socket: socket.socket | None = None
        self._connection_status = False
        self._bin_server_path = bin_server_path
        self._bin_bitstream_path = bin_bitstream_path
        self._operator_port = protocol.DEFAULT_OPERATOR_PORT if operator_port is None else operator_port
        self._server_address: tuple[str, int] | None = None
        self.set_address(address)
        self._operator = Operator(self._server_address[0], self._operator_port)
        self._config = self.get_default_config()
        self._hardware_model = None
        self._installed_bin_server_path = None
        self._installed_bin_bitstream_path = None

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

    def set_logging_level(self, level: str) -> None:
        """
        Set logging level.

        :param level: The logging level, debug, info, warning, error,
        """

        if level.lower() not in ("debug", "info", "warning", "error"):
            self._logger.error("Invalid logging level.")

        self.send_and_receive(
            protocol.build_send_message(protocol.Command.SET_LOGGING_LEVEL, payload=level.encode("ascii"))
        )

    def get_operator(self) -> Operator:
        """
        Get the operator object for this Cracker instance.

        :return: Operator object.
        :rtype: Operator
        """
        return self._operator

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
        :return: None
        """
        if bin_server_path is None:
            bin_server_path = self._bin_server_path
        if bin_bitstream_path is None:
            bin_bitstream_path = self._bin_bitstream_path

        if update_bin and not self._update_cracker_bin(force_update_bin, bin_server_path, bin_bitstream_path):
            return

        if force_update_bin and self._socket and self._connection_status:
            # Reset the connection if forcing a bin update when it was previously connected.
            self._socket = None
            self._connection_status = False

        if self._socket and self._connection_status:
            self._logger.debug("Already connected, reuse.")
            return

        try:
            if not self._socket:
                self._socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                self._socket.settimeout(5)
            self._socket.connect(self._server_address)
            self._connection_status = True
            self._logger.info(f"Connected to cracker: {self._server_address}")
            self.sync_config_to_cracker()
            self._logger.info("Synchronize the configuration to Cracker successfully.")
        except OSError as e:
            self._logger.error("Connection failed: %s", e)
            self._socket = None
            self._connection_status = False

    def _update_cracker_bin(
        self,
        force_update: bool = False,
        bin_server_path: str | None = None,
        bin_bitstream_path: str | None = None,
    ) -> bool:
        """
        Update cracker's firmwares: server.bin and bitstream.bin.

        :param force_update: Whether to force update the firmware if the device already has the firmware installed.
        :type force_update: bool
        :param bin_server_path: The bin_server file path for updates, will use the embedded firmware if not specified.
        :type bin_server_path: str | None
        :param bin_bitstream_path: The bin_bitstream file path for updates,
                                   will use the embedded firmware if not specified.
        :type bin_bitstream_path: str | None
        """
        if not self._operator.connect():
            return False

        if not force_update and self._operator.get_status():
            return True

        self._hardware_model = self._operator.get_hardware_model()

        if bin_server_path is None or bin_bitstream_path is None:
            if self._hardware_model is None or self._hardware_model == "unknown":
                self._logger.error(
                    "The hardware model is unknown, and the Cracker bin cannot be updated. Alternatively, "
                    "you can specify the bin_server_path and bin_bitstream_path in the connect API."
                )
                return False

            _bin_server_path, _bin_bitstream_path = self._get_bin_file_path(self._hardware_model)

            if bin_server_path is None:
                bin_server_path = _bin_server_path
            if bin_bitstream_path is None:
                bin_bitstream_path = _bin_bitstream_path

            if bin_server_path is None:
                self._logger.error(f"Can't find bin_server file for hardware model: {self._hardware_model}.")
                return False
            if bin_bitstream_path is None:
                self._logger.error(f"Can't find bin_bitstream file for hardware model: {self._hardware_model}.")
                return False

        try:
            bin_server = open(bin_server_path, "rb").read()
            bin_bitstream = open(bin_bitstream_path, "rb").read()
            success = (
                self._operator.update_server(bin_server)
                and self._operator.update_bitstream(bin_bitstream)
                and self._operator.get_status()
            )
            if success:
                self._installed_bin_server_path = bin_server_path
                self._installed_bin_bitstream_path = bin_bitstream_path
            return success
        except OSError as e:
            self._logger.error(f"Update cracker bin failed: {e.args}")
            return False

    def get_firmware_info(self):
        if self._installed_bin_server_path is None or self._installed_bin_bitstream_path is None:
            self._logger.warning("The Cracker has not successfully installed any firmware.")

        return (
            f"hardware model: {self._hardware_model}, "
            f"bin server: {self._installed_bin_server_path}, "
            f"bin_bitstream: {self._installed_bin_bitstream_path}"
        )

    def _get_bin_file_path(self, model: str):
        firmware_path = os.path.join(os.path.dirname(importlib.util.find_spec("cracknuts").origin), "firmware")
        map_json_path = os.path.join(firmware_path, "map.json")
        map_json = json.load(open(map_json_path))
        if model not in map_json:
            return None, None

        bin_server_path = map_json[model]["server"]
        if bin_server_path is not None:
            bin_server_path = os.path.join(firmware_path, bin_server_path)
        bin_bitstream_path = map_json[model]["bitstream"]
        if bin_bitstream_path is not None:
            bin_bitstream_path = os.path.join(firmware_path, bin_bitstream_path)
        if not os.path.exists(bin_server_path) or not os.path.isfile(bin_server_path):
            self._logger.error("Find bin server path, but it is not exist or not a file.")
            bin_server_path = None
        if not os.path.exists(bin_bitstream_path) or not os.path.isfile(bin_bitstream_path):
            self._logger.error("Find bin_bitstream path, but it is not exist or not a file.")
            bin_bitstream_path = None

        return bin_server_path, bin_bitstream_path

    def disconnect(self) -> None:
        """
        Disconnect from cracker device.

        :return: None
        """
        self._operator.disconnect()
        try:
            if self._socket:
                self._socket.close()
            self._logger.info(f"Disconnect from {self._server_address}")
        except OSError as e:
            self._logger.error("Disconnection failed: %s", e)
        finally:
            self._connection_status = False
            self._socket = None
            self._hardware_model = None
            self._installed_bin_server_path = None
            self._installed_bin_bitstream_path = None

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
                self._logger.debug(
                    f"Send message to {self._server_address}: \n{hex_util.get_bytes_matrix(
                        message, max_bytes_count=self._logger_info_payload_max_length
                    )}"
                )
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
                    f"{magic}, {version}, {direction}, 0x{status:04X}, {length}"
                )
            if length == 0:
                return status, None
            resp_payload = self._recv(length)
            if status != protocol.STATUS_OK:
                self._logger.warning(
                    f"Received a non-OK response status code: 0x{status:04X}, "
                    f"with the payload: {resp_payload.decode('utf-8')}"
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
        if self._logger.isEnabledFor(logging.INFO):
            self._logger.info(
                f"Send command [0x{command:04x}] with payload: "
                f"{None if payload is None else hex_util.get_hex(
                                  payload, self._logger_info_payload_max_length)}] "
                f"to {self._server_address}"
            )
        status, payload = self.send_and_receive(protocol.build_send_message(command, rfu, payload))
        if self._logger.isEnabledFor(logging.INFO):
            self._logger.info(
                f"Receive response for command: [0x{command:04x}] from {self._server_address}, "
                f"status: {status}, payload: length: {0 if payload is None else len(payload)}, content: "
                f"{None if payload is None else hex_util.get_hex(
                                  payload, self._logger_info_payload_max_length)}"
            )
        return status, payload

    def set_logger_info_payload_max_length(self, length):
        self._logger_info_payload_max_length = length

    def set_logger_debug_payload_max_length(self, length):
        self._logger_debug_payload_max_length = length

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
            content = f.readlines()
            config_json = json.loads("".join(content))
            if "config" in config_json:
                content = config_json["config"]
            self.load_config_from_str(content)

    def load_config_from_str(self, json_str: str) -> None:
        """
        Load config from a JSON string.

        :param json_str: the JSON string
        :type json_str: str
        :return: None
        """
        self._config.load_from_json(json_str)
        self.sync_config_to_cracker()

    def get_id(self) -> tuple[int, str | None]:
        """
        Get the ID of the equipment.

        :return: The equipment response status code and the ID of the equipment.
        :rtype: tuple[int, str | None]
        """
        return protocol.STATUS_OK, self._operator.get_sn()

    def get_hardware_model(self) -> tuple[int, str | None]:
        """
        Get the name of the equipment.

        :return: The equipment response status code and the name of the equipment.
        :rtype: tuple[int, str | None]
        """
        return protocol.STATUS_OK, self._operator.get_hardware_model()

    def get_bitstream_version(self):
        return self.send_with_command(protocol.Command.GET_BITSTREAM_VERSION)

    def get_firmware_version(self) -> tuple[int, str | None]:
        """
        Get the version of the equipment.

        :return: The equipment response status code and the version of the equipment.
        :rtype: tuple[int, str | None]
        """
        bitstream_status, bitstream_version = self.get_bitstream_version()
        server_version = self._operator.get_server_version()
        operator_version = self._operator.get_version()

        return (
            protocol.STATUS_OK,
            f"operator_version: {operator_version}, "
            f"server_version: {server_version}, "
            f"bitstream_version: {bitstream_version}",
        )

    def osc_single(self) -> tuple[int, None]:
        payload = None
        self._logger.debug("scrat_sample_len payload: %s", payload)
        status, res = self.send_with_command(protocol.Command.OSC_SINGLE, payload=payload)
        return status, None

    def osc_force(self) -> tuple[int, None]:
        """
        Force produce a wave data.

        :return: The device response status
        :rtype: tuple[int, None]
        """
        payload = None
        self._logger.debug(f"scrat_force payload: {payload}")
        return self.send_with_command(protocol.Command.OSC_FORCE, payload=payload)

    def osc_is_triggered(self) -> tuple[int, bool]:
        payload = None
        self._logger.debug(f"scrat_is_triggered payload: {payload}")
        status, res = self.send_with_command(protocol.Command.OSC_IS_TRIGGERED, payload=payload)
        if status != protocol.STATUS_OK:
            self._logger.error(f"Receive status code error [{status}]")
            return status, False
        else:
            if res is None:
                self._logger.error("is_triggered get empty payload.")
                return status, False
            else:
                res_code = int.from_bytes(res, "big")
                return status, res_code == 4

    def osc_get_analog_wave(self, channel: int, offset: int, sample_count: int) -> tuple[int, np.ndarray]:
        """
        Get the analog wave.

        :param channel: the channel of the analog wave.
        :type channel: int
        :param offset: the offset of the analog wave.
        :type offset: int
        :param sample_count: the sample count of the analog wave.
        :type sample_count: int
        :return: the analog wave.
        :rtype: tuple[int, np.ndarray]
        """
        payload = struct.pack(">BII", channel, offset, sample_count)
        self._logger.debug(f"scrat_get_analog_wave payload: {payload.hex()}")
        status, wave_bytes = self.send_with_command(protocol.Command.OSC_GET_ANALOG_WAVES, payload=payload)
        if status != protocol.STATUS_OK:
            return status, np.array([])
        else:
            if wave_bytes is None:
                return status, np.array([])
            else:
                wave = struct.unpack(f"{sample_count}h", wave_bytes)
                return status, np.array(wave, dtype=np.int16)

    def osc_get_digital_wave(self, channel: int, offset: int, sample_count: int) -> tuple[int, np.ndarray]:
        payload = struct.pack(">BII", channel, offset, sample_count)
        self._logger.debug(f"scrat_get_digital_wave payload: {payload.hex()}")
        status, wave_bytes = self.send_with_command(protocol.Command.OSC_GET_ANALOG_WAVES, payload=payload)
        if status != protocol.STATUS_OK:
            return status, np.array([])
        else:
            if wave_bytes is None:
                return status, np.array([])
            else:
                wave = struct.unpack(f"{sample_count}h", wave_bytes)
                return status, np.array(wave, dtype=np.int16)
