# Copyright 2024 CrackNuts. All rights reserved.

import abc
import functools
import importlib.util
import json
import logging
import os
import socket
import struct
import threading
import typing
from abc import ABC
from dataclasses import dataclass
from enum import Enum

import numpy as np

import cracknuts.utils.hex_util as hex_util
from cracknuts import logger
from cracknuts.cracker import protocol
from cracknuts.cracker.cracker_manager import CrackerManager
from cracknuts.cracker.operator import Operator
from cracknuts.cracker.ssh_client import SSHCracker


class ConfigBasic:
    def __init__(self):
        self.osc_channel_0_enable = False
        self.osc_channel_1_enable = True
        self.osc_channel_0_gain = 10
        self.osc_channel_1_gain = 10
        self.osc_sample_length = 1024
        self.osc_sample_delay = 0
        self.osc_sample_clock = 48000
        self.osc_sample_phase = 0
        self.osc_trigger_source = 0
        self.osc_trigger_mode = 0
        self.osc_trigger_edge = 0
        self.osc_trigger_edge_level = 1

    def __str__(self):
        return f"Config({', '.join([f'{k}: {v}' for k, v in self.__dict__.items() if not k.startswith('_')])})"

    def __repr__(self):
        return self.__str__()

    def dump_to_json(self) -> str:
        """
        Dump the configuration to a JSON string.

        """

        def enum_converter(obj):
            if isinstance(obj, Enum):
                return obj.value
            raise TypeError(f"Type {type(obj)} not serializable")

        return json.dumps(
            {k: v for k, v in self.__dict__.items() if not k.startswith("_")}, indent=4, default=enum_converter
        )

    def load_from_json(self, json_str: str) -> "ConfigBasic":
        """
        Load configuration from a JSON string. If a value in the JSON string is null, it will be skipped,
        and the default configuration will be used.

        """
        for k, v in json.loads(json_str).items():
            if v is not None:
                self.__dict__[k] = v
        return self


T = typing.TypeVar("T", bound=ConfigBasic)


# === Since the device does not support the channel enable function,
# the information is temporarily saved to the host software. ===
@dataclass
class _ChannelConfig:
    osc_channel_0_enable: bool = False
    osc_channel_1_enable: bool = True


# === end ===


def connection_status_check(func):
    """
    This is a decorator to check the connection status of the cracker device. user should use this directly.
    """

    @functools.wraps(func)
    def wrapper(self: "CrackerBasic", *args, **kwargs):
        if not self._connection_status:
            print("Error: Cracker not connected")
            sig_result = func.__annotations__.get("return", None)
            if sig_result is tuple:
                return self.DISCONNECTED, None
            else:
                return None
        return func(self, *args, **kwargs)

    return wrapper


class CrackerBasic(ABC, typing.Generic[T]):
    NON_PROTOCOL_ERROR = -1
    DISCONNECTED = -2
    _cracker_manager: CrackerManager | None = None

    _BASE_ADDRESS = 0x43C10000

    _OFFSET_GPIO_DATA = 0x0C00
    _OFFSET_GPIO_DIR = 0x0C04

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
        self._operator: Operator | None = None
        self.shell: SSHCracker | None = None
        self.set_address(address)
        self._config = self.get_default_config()
        self._hardware_model = None
        self._installed_bin_server_path = None
        self._installed_bin_bitstream_path = None
        # === Since the device does not support the channel enable function,
        # the information is temporarily saved to the host software. ===
        self._channel_enable = _ChannelConfig()
        # === end ===
        # Cracker only supports sampling length in multiples of 1024,
        # record actual length to truncate waveform data later.
        self._osc_sample_length: int | None = None

    def change_ip(self, new_ip: str, new_mask: str = None, new_gateway: str = None) -> bool:
        """
        Change the network address of the current target device.

        This instance method uses the IP currently configured on this object as
        the target device IP, then delegates the network change to the shared
        ``CrackerManager`` instance. If the device is currently connected and the
        IP change succeeds, the object updates its own target address and
        reconnects when possible.

        :param new_ip: New device IP address, or ``"dhcp"`` to enable DHCP.
        :type new_ip: str
        :param new_mask: Subnet mask or prefix length for a static IP change. If
                         omitted, the device's current mask is reused.
        :type new_mask: str | None
        :param new_gateway: Default gateway for a static IP change. If omitted,
                            the device's current gateway is reused.
        :type new_gateway: str | None
        :return: ``True`` if the device accepted the change request, otherwise ``False``.
        :rtype: bool
        """
        if self._server_address is None:
            self._logger.error("Change ip failed: cracker address is not configured.")
            return False

        target_ip = self._server_address[0]
        was_connected = self._connection_status
        if was_connected:
            self.disconnect()

        ack = type(self).set_device_ip(
            target_ip=target_ip,
            new_ip=new_ip,
            mask=new_mask,
            gateway=new_gateway,
        )
        if ack is None or ack.get("status") != 0:
            if was_connected:
                self.connect()
            return False

        if new_ip != "dhcp":
            self.set_ip_port(new_ip, self._server_address[1])
            if was_connected:
                self.connect()
        else:
            self._logger.info("Device switched to DHCP. Re-discover the device before reconnecting.")

        return True

    @classmethod
    def _resolve_network_settings(
        cls,
        target_ip: str,
        mask: str | None,
        gateway: str | None,
    ) -> tuple[str, str | None]:
        if mask and gateway:
            return mask, gateway

        operator = Operator(target_ip, protocol.DEFAULT_OPERATOR_PORT)
        if not operator.connect():
            raise RuntimeError(f"Cannot connect to operator service on {target_ip} to read current network settings.")

        try:
            current_config = operator.get_ip()
        finally:
            operator.disconnect()

        if current_config is None:
            raise RuntimeError(f"Cannot read current network settings from {target_ip}.")

        _, current_mask, current_gateway = current_config
        return mask or current_mask, gateway or current_gateway

    @classmethod
    def _create_device_manager(
        cls,
        broadcast: str = "255.255.255.255",
        scan_interval: float = 3.0,
        offline_grace: float = 15.0,
        device_timeout: float = 60.0,
        continuous: bool = False,
    ) -> CrackerManager:
        """
        Return the shared ``CrackerManager`` instance for this class.

        The manager is created lazily on first use and reused by subsequent
        class-level device discovery and IP update calls. Each call refreshes
        the cached manager configuration to match the provided arguments.

        :param broadcast: Broadcast address for discovery.
        :type broadcast: str
        :param scan_interval: Seconds between discovery scans.
        :type scan_interval: float
        :param offline_grace: Seconds without response before marking offline.
        :type offline_grace: float
        :param device_timeout: Seconds without response before removing a device.
        :type device_timeout: float
        :param continuous: Whether the shared manager should keep background scanning enabled.
        :type continuous: bool
        :return: Shared manager instance.
        :rtype: CrackerManager
        """
        if cls._cracker_manager is None:
            cls._cracker_manager = CrackerManager(
                broadcast=broadcast,
                scan_interval=scan_interval,
                offline_grace=offline_grace,
                device_timeout=device_timeout,
                continuous=continuous,
            )
        else:
            cls._cracker_manager._broadcast = broadcast
            cls._cracker_manager._scan_interval = scan_interval
            cls._cracker_manager._offline_grace = offline_grace
            cls._cracker_manager._device_timeout = device_timeout

            if continuous and not cls._cracker_manager._running:
                cls._cracker_manager.start_discovery()
            elif not continuous and cls._cracker_manager._running:
                cls._cracker_manager.stop_discovery()

            cls._cracker_manager._continuous = continuous

        return cls._cracker_manager

    @classmethod
    def discover_devices(
        cls,
        broadcast: str = "255.255.255.255",
        scan_interval: float = 3.0,
        offline_grace: float = 15.0,
        device_timeout: float = 60.0,
    ) -> list[dict]:
        """
        Discover devices on the local network once.

        This class method reuses the shared ``CrackerManager`` instance and
        performs a single discovery scan without starting continuous background
        monitoring.

        :param broadcast: Broadcast address for discovery.
        :type broadcast: str
        :param scan_interval: Cached scan interval for the shared manager.
        :type scan_interval: float
        :param offline_grace: Cached offline grace period for the shared manager.
        :type offline_grace: float
        :param device_timeout: Cached device timeout for the shared manager.
        :type device_timeout: float
        :return: List of discovered device information dictionaries.
        :rtype: list[dict]
        """
        manager = cls._create_device_manager(
            broadcast=broadcast,
            scan_interval=scan_interval,
            offline_grace=offline_grace,
            device_timeout=device_timeout,
            continuous=False,
        )
        return manager.discover_once()

    @classmethod
    def set_device_ip(
        cls,
        target_ip: str,
        new_ip: str,
        mask: str = "",
        gateway: str | None = None,
        delay_ms: int = 200,
        broadcast: str = "255.255.255.255",
    ) -> dict | None:
        """
        Change the network address of a device identified by its current IP.

        This class method reuses the shared ``CrackerManager`` instance and
        sends a single IP change request to the target device.

        :param target_ip: Current IP address of the target device.
        :type target_ip: str
        :param new_ip: New device IP address, or ``"dhcp"`` to enable DHCP.
        :type new_ip: str
        :param mask: Subnet mask or prefix length for a static IP change. If
                     omitted, the device's current mask is reused.
        :type mask: str
        :param gateway: Default gateway for a static IP change. If omitted, the
                        device's current gateway is reused.
        :type gateway: str | None
        :param delay_ms: Delay before the device applies the change.
        :type delay_ms: int
        :param broadcast: Broadcast address cached on the shared manager.
        :type broadcast: str
        :return: ACK information from the device, or ``None`` on timeout.
        :rtype: dict | None
        """
        if new_ip != "dhcp":
            mask, gateway = cls._resolve_network_settings(target_ip, mask, gateway)

        manager = cls._create_device_manager(
            broadcast=broadcast,
            continuous=False,
        )
        return manager.set_ip(
            target_ip=target_ip,
            new_ip=new_ip,
            mask=mask,
            gateway=gateway,
            delay_ms=delay_ms,
        )

    def _sync_inner_obj_ip(self) -> None:
        """
        Synchronize inner helper objects to the current target IP.

        This updates the cached ``Operator`` and ``SSHCracker`` instances so
        they point at the address currently stored in ``self._server_address``.
        """
        if self._server_address is None:
            self._operator = None
            self.shell = None
            return

        operator_address = (self._server_address[0], self._operator_port)
        if self._operator is None or self._operator._server_address != operator_address:
            self._operator = Operator(self._server_address[0], self._operator_port)
        if self.shell is None or self.shell.ip != self._server_address[0]:
            self.shell = SSHCracker(ip=self._server_address[0])

    def set_address(self, address: tuple[str, int] | str | None) -> None:
        """
        Update the target cracker address stored in this instance.

        This method updates the local target address metadata used by this
        object and synchronizes the inner ``Operator`` and ``SSHCracker`` target
        IP settings. It does not communicate with the device, so it does not
        modify the real device network configuration.

        :param address: Device address as ``(ip, port)``, URI-like string, or
                        ``None`` to clear the current target.
        :type address: tuple[str, int] | str | None
        :return: None
        """
        if isinstance(address, tuple):
            self._server_address = address
            self._sync_inner_obj_ip()
        elif address is None:
            self._server_address = None
            self._sync_inner_obj_ip()
        elif isinstance(address, str):
            self.set_uri(address)

    def get_address(self) -> tuple[str, int] | None:
        """
        Get the device address in tuple format.

        :return: address in tuple format: (ip, port).
        :rtype: tuple[str, int]
        """
        return self._server_address

    def set_ip_port(self, ip, port) -> None:
        """
        Update the target cracker IP and port stored in this instance.

        This method updates the local target address used by subsequent
        operations and synchronizes the inner ``Operator`` and ``SSHCracker``
        objects to the same target. It does not modify the real device network
        configuration.

        :param ip: IP address.
        :type ip: str
        :param port: Port.
        :type port: int
        :return: None
        """
        self._server_address = ip, port
        self._sync_inner_obj_ip()

    def set_uri(self, uri: str) -> None:
        """
        Update the target cracker address stored in this instance from a URI.

        This method parses and stores the local target address, then synchronizes
        the inner ``Operator`` and ``SSHCracker`` objects to that target. It
        does not communicate with the device and does not modify the device IP.

        :param uri: Device URI in the form ``cnp://<ip>[:port]`` or ``<ip>[:port]``.
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
        self._sync_inner_obj_ip()

    @connection_status_check
    def set_logging_level(self, level: str) -> None:
        """
        Set the Cracker OS logging level.

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
        self._sync_inner_obj_ip()
        if self._operator is None:
            raise RuntimeError("Cracker address is not configured.")
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
            return f"cnp://{self._server_address[0]}{'' if port is None else f':{port}'}"

    def connect(
        self,
        update_bin: bool = True,
        force_update_bin: bool = False,
        bin_server_path: str | None = None,
        bin_bitstream_path: str | None = None,
        force_write_default_config: bool = False,
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
        :param force_write_default_config: Whether to force update the configuration while the device is running
                                           normally (by default, configuration updates are only performed when updating
                                           the firmware).
        :type force_write_default_config: bool
        :return: None
        """
        self._sync_inner_obj_ip()
        if bin_server_path is None:
            bin_server_path = self._bin_server_path
        if bin_bitstream_path is None:
            bin_bitstream_path = self._bin_bitstream_path

        bin_updated = False
        if update_bin:
            success, bin_updated = self._update_cracker_bin(force_update_bin, bin_server_path, bin_bitstream_path)
            if not success:
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
                self._socket.settimeout(
                    60
                )  # todo 由于在IO通信时，delay的存在，可能超过这个超时时间，这里暂时设置为60秒的超时
            self._socket.connect(self._server_address)
            self._connection_status = True
            self._logger.info(f"Connected to cracker: {self._server_address}")
            if (update_bin and bin_updated) or force_write_default_config:
                # Sync the default configuration to the cracker when updating its firmware.
                self.write_config_to_cracker(self.get_default_config())
                self._logger.info("Write default configuration to Cracker.")
            self._config = self.get_current_config()
            self._logger.info("Synchronize the configuration from Cracker.")
            self._sync_inner_obj_ip()
            if self.shell is not None:
                try:
                    if not self.shell.is_connected():
                        self.shell.connect()
                        self._logger.info(f"Connected to SSH cracker: {self.shell.ip}")
                except Exception as e:
                    self._logger.warning(f"Failed to connect SSH cracker: {e}")
        except OSError as e:
            self._logger.error("Connection failed: %s", e)
            self._socket = None
            self._connection_status = False

    def _update_cracker_bin(
        self,
        force_update: bool = False,
        bin_server_path: str | None = None,
        bin_bitstream_path: str | None = None,
    ) -> tuple[bool, bool]:
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
            return False, False

        if not force_update and self._operator.get_status():
            return True, False

        self._hardware_model = self._operator.get_hardware_model()

        if bin_server_path is None or bin_bitstream_path is None:
            if self._hardware_model is None or self._hardware_model == "unknown":
                self._logger.error(
                    "The hardware model is unknown, and the Cracker bin cannot be updated. Alternatively, "
                    "you can specify the bin_server_path and bin_bitstream_path in the connect API."
                )
                return False, False

            _bin_server_path, _bin_bitstream_path = self._get_bin_file_path(self._hardware_model)

            if bin_server_path is None:
                bin_server_path = _bin_server_path
            if bin_bitstream_path is None:
                bin_bitstream_path = _bin_bitstream_path

            if bin_server_path is None:
                self._logger.error(f"Can't find bin_server file for hardware model: {self._hardware_model}.")
                return False, False
            if bin_bitstream_path is None:
                self._logger.error(f"Can't find bin_bitstream file for hardware model: {self._hardware_model}.")
                return False, False

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
            return success, success
        except OSError as e:
            self._logger.error(f"Update cracker bin failed: {e.args}")
            return False, False

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
        if not self._connection_status:
            return
        if self._operator is not None:
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
                    f"Send message to {self._server_address}: \n{
                        hex_util.get_bytes_matrix(message, max_bytes_count=self._logger_debug_payload_max_length)
                    }"
                )
            self._socket.sendall(message)
            resp_header = self._socket.recv(protocol.RES_HEADER_SIZE)
            if self._logger.isEnabledFor(logging.DEBUG):
                self._logger.debug(
                    "Get response header from %s: \n%s",
                    self._server_address,
                    hex_util.get_bytes_matrix(resp_header),
                )
            try:
                magic, version, direction, status, length = struct.unpack(protocol.RES_HEADER_FORMAT, resp_header)
            except Exception as e:
                self._logger.error("Get response header failed: %s", e)
                self._logger.error(f"The request is {hex_util.get_bytes_matrix(message)}")
                self._logger.error(f"The header is [{hex_util.get_hex(resp_header)}]")
                # import traceback
                #
                # traceback.print_stack()
                return protocol.STATUS_ERROR, None

            if self._logger.isEnabledFor(logging.DEBUG):
                self._logger.debug(
                    f"Receive header from {self._server_address}: "
                    f"{magic}, {version}, {direction}, 0x{status:04X}, {length}"
                )
            if length == 0:
                resp_payload = None
            else:
                resp_payload = self._recv(length)
            if status != protocol.STATUS_OK:
                try:
                    resp_payload_str = resp_payload.decode("utf-8") if resp_payload is not None else ""
                except UnicodeDecodeError:
                    resp_payload_str = hex_util.get_hex(resp_payload, max_len=len(resp_payload))
                req_command, req_payload = protocol.unpack_send_message(message)
                if req_command is None:
                    self._logger.warning("Request message format error, cannot unpack command.")
                self._logger.warning(
                    f"Command {f'0x{req_command:04X}' if req_command is not None else 'None'} "
                    f"with payload {hex_util.get_hex(req_payload, max_len=len(req_payload))} "
                    f"received a non-OK response with status code 0x{status:04X}, "
                    f"and payload [{resp_payload_str}]."
                )
            else:
                if self._logger.isEnabledFor(logging.DEBUG):
                    self._logger.debug(
                        f"Receive payload from {self._server_address}: \n"
                        f"{
                            hex_util.get_bytes_matrix(
                                resp_payload, max_bytes_count=self._logger_debug_payload_max_length
                            )
                        }"
                    )
            return status, resp_payload
        except OSError as e:
            self._logger.error(
                f"Send message failed: {e}, and msg, command :0x{message[7:9].hex()}"
                f", payload: {hex_util.get_hex(message[10:])}"
            )
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
                f"{None if payload is None else hex_util.get_hex(payload, self._logger_info_payload_max_length)}] "
                f"to {self._server_address}"
            )
        status, payload = self.send_and_receive(protocol.build_send_message(command, rfu, payload))
        if self._logger.isEnabledFor(logging.INFO):
            self._logger.info(
                f"Receive response for command: [0x{command:04x}] from {self._server_address}, "
                f"status: 0x{status:04X}, payload: length: {0 if payload is None else len(payload)}, content: "
                f"{None if payload is None else hex_util.get_hex(payload, self._logger_info_payload_max_length)}"
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

    @connection_status_check
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

    @connection_status_check
    def write_config_to_cracker(self, config: T):
        """
        Sync config to cracker.

        To prevent configuration inconsistencies between the host and the device,
        so all configuration information needs to be written to the device.
        User should call this function before get data from device.

        NOTE: This function is currently ignored and will be resumed after all Cracker functions are completed.
        """
        ...

    @connection_status_check
    def dump_config(self, path=None) -> str | None:
        """
        Dump the current config to a JSON file if a path is specified, or to a JSON string if no path is specified.

        :param path: the path to the JSON file
        :type path: str | None
        :return: the content of JSON string or None if no path is specified.
        :rtype: str | None
        """
        config_json = self.get_current_config().dump_to_json()
        if path is None:
            return config_json
        else:
            with open(path, "w") as f:
                f.write(config_json)

    @connection_status_check
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
            if "cracker" in config_json:
                content = config_json["cracker"]
            self.load_config_from_str(content)

    @connection_status_check
    def load_config_from_str(self, json_str: str) -> None:
        """
        Load config from a JSON string.

        :param json_str: the JSON string
        :type json_str: str
        :return: None
        """
        self._config.load_from_json(json_str)
        self.write_config_to_cracker(self._config)

    @connection_status_check
    def get_id(self) -> tuple[int, str | None]:
        """
        Get the ID of the equipment.

        :return: The equipment response status code and the ID of the equipment.
        :rtype: tuple[int, str | None]
        """
        return protocol.STATUS_OK, self._operator.get_sn()

    @connection_status_check
    def get_hardware_model(self) -> tuple[int, str | None]:
        """
        Get the name of the equipment.

        :return: The equipment response status code and the name of the equipment.
        :rtype: tuple[int, str | None]
        """
        return protocol.STATUS_OK, self._operator.get_hardware_model()

    @connection_status_check
    def get_bitstream_version(self):
        return self.send_with_command(protocol.Command.GET_BITSTREAM_VERSION)

    @connection_status_check
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

    @connection_status_check
    def osc_single(self) -> tuple[int, None]:
        payload = None
        self._logger.debug("scrat_sample_len payload: %s", payload)
        status, res = self.send_with_command(protocol.Command.OSC_SINGLE, payload=payload)
        return status, None

    @connection_status_check
    def osc_force(self) -> tuple[int, None]:
        """
        Force produce a wave data.

        :return: The device response status
        :rtype: tuple[int, None]
        """
        payload = None
        self._logger.debug(f"scrat_force payload: {payload}")
        return self.send_with_command(protocol.Command.OSC_FORCE, payload=payload)

    @connection_status_check
    def osc_is_triggered(self) -> tuple[int, bool]:
        payload = None
        self._logger.debug(f"scrat_is_triggered payload: {payload}")
        status, res = self.send_with_command(protocol.Command.OSC_IS_TRIGGERED, payload=payload)
        if status != protocol.STATUS_OK:
            self._logger.error(f"is_triggered receive status code error [0x{status:04X}]")
            return status, False
        else:
            if res is None:
                self._logger.error("is_triggered get empty payload.")
                return status, False
            else:
                res_code = int.from_bytes(res, "big")
                return status, res_code == 4

    def osc_get_wave(self, channel: int | str, offset: int, sample_count: int) -> tuple[int, np.ndarray | None]:
        return self.osc_get_analog_wave(channel, offset, sample_count)

    @connection_status_check
    def osc_get_analog_wave(self, channel: int, offset: int, sample_count: int) -> tuple[int, np.ndarray | None]:
        """
        Get the analog wave.

        :param channel: The channel of the analog wave. It can be either 0, 1, or 'A', 'B'.
        :type channel: int|str
        :param offset: the offset of the analog wave.
        :type offset: int
        :param sample_count: the sample count of the analog wave.
        :type sample_count: int
        :return: the analog wave.
        :rtype: tuple[int, np.ndarray]
        """
        if isinstance(channel, str):
            channels = ("A", "B")
            if channel not in channels:
                self._logger.error(f"Invalid channel: {channel}. it must be one of {channels}.")
                return self.NON_PROTOCOL_ERROR, None
            channel = channels.index(channel)
        payload = struct.pack(">BII", channel, offset, sample_count)
        self._logger.debug(f"scrat_get_analog_wave payload: {payload.hex()}")
        status, wave_bytes = self.send_with_command(protocol.Command.OSC_GET_ANALOG_WAVES, payload=payload)
        if status != protocol.STATUS_OK:
            return status, np.array([])
        else:
            if wave_bytes is None:
                return status, np.array([])
            else:
                wbl = len(wave_bytes)
                expect_wbl = sample_count * 2
                if wbl != expect_wbl:
                    self._logger.error(
                        f"Wave bytes length error: require {expect_wbl} but get {wbl}:\n{hex_util.get_hex(wave_bytes)}"
                    )
                    if wbl != 0:
                        self._logger.error("Wave bytes length is not expected, will get actually length wave.")
                        if wbl % 2 != 0:
                            self._logger.error("Wave bytes length is a odd number, will get a even length wave.")
                        wave = struct.unpack(f"{wbl // 2}h", wave_bytes)
                        return status, np.array(wave, dtype=np.int16)
                    else:
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
