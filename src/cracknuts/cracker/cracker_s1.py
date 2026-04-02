# Copyright 2024 CrackNuts. All rights reserved.

import re
import struct
import warnings
from enum import Enum

from cracknuts.cracker import protocol, serial
from cracknuts.cracker.cracker_basic import ConfigBasic, CrackerBasic, connection_status_check


class ConfigS1(ConfigBasic):
    def __init__(self):
        super().__init__()

        self.nut_enable: bool = False
        self.nut_voltage: float = 3.3
        self.nut_clock_enable = False
        self.nut_clock = 8000
        self.nut_timeout: int | None = None
        self.nut_reset_io_enable: bool = False

        self.nut_uart_enable: bool = False
        self.nut_uart_baudrate: serial.Baudrate = serial.Baudrate.BAUDRATE_115200
        self.nut_uart_bytesize: serial.Bytesize = serial.Bytesize.EIGHTBITS
        self.nut_uart_parity: serial.Parity = serial.Parity.PARITY_NONE
        self.nut_uart_stopbits: serial.Stopbits = serial.Stopbits.STOPBITS_ONE

        self.nut_spi_enable: bool | None = False
        self.nut_spi_speed: float = 10_000.0
        self.nut_spi_cpol: serial.SpiCpol = serial.SpiCpol.SPI_CPOL_LOW
        self.nut_spi_cpha: serial.SpiCpha = serial.SpiCpha.SPI_CPHA_LOW
        self.nut_spi_csn_auto: bool = True
        self.nut_spi_csn_delay: bool = True

        self.nut_i2c_enable: bool = False
        self.nut_i2c_dev_addr: int = 0x00
        self.nut_i2c_speed: serial.I2cSpeed = serial.I2cSpeed.STANDARD_100K
        self.nut_i2c_stretch_enable = False

    def __str__(self):
        return super().__str__()

    def __repr__(self):
        return super().__repr__()


class CrackerS1(CrackerBasic[ConfigS1]):
    def get_default_config(self) -> ConfigS1:
        return ConfigS1()

    @connection_status_check
    def get_current_config(self) -> ConfigS1 | None:
        status, res = self.send_with_command(protocol.Command.GET_CONFIG)
        if status == protocol.STATUS_OK:
            # === Since the device does not support the channel enable function,
            # the information is temporarily saved to the host software. ===
            # return self._parse_config_bytes(res)
            config = self._parse_config_bytes(res)
            config.osc_channel_0_enable = self._channel_enable.osc_channel_0_enable
            config.osc_channel_1_enable = self._channel_enable.osc_channel_1_enable
            # Cracker only supports sampling length in multiples of 1024,
            # record actual length to truncate waveform data later.
            config.osc_sample_length = self._osc_sample_length
            return config
            # === end ===
        else:
            self._logger.error(f"Get config from cracker error, return code 0x{status:02x}.")
            return None

    def _update_config_from_cracker(self):
        for k, v in self.get_current_config().__dict__.items():
            setattr(self._config, k, v)

    def _parse_config_bytes(self, config_bytes: bytes) -> ConfigS1 | None:
        if config_bytes is None:
            return None
        bytes_format, config = self._get_config_bytes_format()
        res_bytes_length = len(config_bytes)
        struct_fmt = f">{"".join(bytes_format.values())}"
        bytes_length = struct.calcsize(struct_fmt)
        if res_bytes_length != bytes_length:
            if res_bytes_length < bytes_length:
                self._logger.warning(
                    f"The length of the config info from Cracker is incorrect: "
                    f"expected {bytes_length}, but got {res_bytes_length}."
                )
                return None
            config_bytes = config_bytes[:bytes_length]

        try:
            config_tuple = struct.unpack(f">{"".join(bytes_format.values())}", config_bytes)
        except Exception as e:
            self._logger.error(
                f"Parse config bytes error: {e.args}, origin bytes is: [{config_bytes.hex(' ')}], "
                f"Default configuration will be used."
            )
            return config

        for i, k in enumerate(bytes_format.keys()):
            v = config_tuple[i]
            if hasattr(config, k):
                default_value = getattr(config, k)
                v = self._parse_config_special_case(k, v)
                if default_value is not None and isinstance(default_value, Enum):
                    v = default_value.__class__(v)

                setattr(config, k, v)
            else:
                self._logger.info(f"Parse config bytes error: {k} is not a valid config key.")

        return config

    def _parse_config_special_case(self, k, v):
        if k == "nut_voltage":
            v = v / 1000
        elif k == "nut_spi_speed":
            v = round(100e6 / 2 / v, 2)
        return v

    def _get_config_bytes_format(self) -> tuple[dict[str, str], ConfigS1]:
        return (
            {
                "nut_enable": "?",
                "nut_voltage": "I",
                "nut_clock_enable": "?",
                "nut_clock": "I",
                "nut_reset_io_enable": "?",
                "osc_sample_clock": "I",
                "osc_sample_phase": "I",
                "osc_sample_length": "I",
                "osc_sample_delay": "I",
                "osc_channel_0_enable": "?",
                "osc_channel_0_gain": "B",
                "osc_channel_1_enable": "?",
                "osc_channel_1_gain": "B",
                "osc_trigger_mode": "B",
                "osc_trigger_source": "B",
                "osc_trigger_edge": "B",
                "osc_trigger_edge_level": "H",
                "nut_i2c_enable": "?",
                "nut_i2c_dev_addr": "B",
                "nut_i2c_speed": "B",
                "nut_i2c_stretch_enable": "?",
                "nut_uart_enable": "?",
                "nut_uart_stopbits": "B",
                "nut_uart_parity": "B",
                "nut_uart_bytesize": "B",
                "nut_uart_baudrate": "B",
                "nut_spi_enable": "?",
                "nut_spi_speed": "H",
                "nut_spi_cpol": "B",
                "nut_spi_cpha": "B",
                "nut_spi_csn_auto": "?",
                "nut_spi_csn_delay": "?",
            },
            ConfigS1(),
        )

    @connection_status_check
    def write_config_to_cracker(self, config: ConfigS1):
        self._osc_set_analog_all_channel_enable({0: config.osc_channel_0_enable, 1: config.osc_channel_1_enable})
        self.osc_analog_gain(0, config.osc_channel_0_gain)
        self.osc_analog_gain(1, config.osc_channel_1_gain)
        self.osc_sample_length(config.osc_sample_length)
        self.osc_sample_delay(config.osc_sample_delay)
        self.osc_sample_clock(config.osc_sample_clock)
        self.osc_sample_clock_phase(config.osc_sample_phase)
        self.osc_trigger_source(config.osc_trigger_source)
        self.osc_trigger_mode(config.osc_trigger_mode)
        self.osc_trigger_edge(config.osc_trigger_edge)
        self.osc_trigger_level(config.osc_trigger_edge_level)

        self.spi_config(
            config.nut_spi_speed,
            config.nut_spi_cpol,
            config.nut_spi_cpha,
            config.nut_spi_csn_auto,
            config.nut_spi_csn_delay,
        )
        self._spi_enable(config.nut_spi_enable)

        self.uart_config(
            config.nut_uart_baudrate,
            config.nut_uart_bytesize,
            config.nut_uart_parity,
            config.nut_uart_stopbits,
        )
        self._uart_io_enable(config.nut_uart_enable)

        self.i2c_config(config.nut_i2c_dev_addr, config.nut_i2c_speed)
        self._i2c_enable(config.nut_i2c_enable)

        self.nut_voltage(config.nut_voltage)
        self._nut_set_enable(config.nut_enable)

        self.nut_clock_freq(config.nut_clock)
        self._nut_set_clock_enable(config.nut_clock_enable)

    @connection_status_check
    def register_read(self, base_address: int, offset: int) -> tuple[int, bytes | None]:
        """
        Read register.

        :param base_address: Base address of the register.
        :type base_address: int
        :param offset: Offset of the register.
        :type offset: int
        :return: The device response status and the value read from the register or None if an exception is raised.
        :rtype: tuple[int, bytes | None]
        """
        payload = struct.pack(">II", base_address, offset)
        self._logger.debug(f"register_read payload: {payload.hex()}")
        status, res = self.send_with_command(protocol.Command.CRACKER_READ_REGISTER, payload=payload)
        if status != protocol.STATUS_OK:
            return status, None
        else:
            return status, res

    @connection_status_check
    def register_write(self, base_address: int, offset: int, data: bytes | int | str) -> tuple[int, None]:
        """
        Write register.

        :param base_address: Base address of the register.
        :type base_address: int
        :param offset: Offset of the register.
        :type offset: int
        :param data: Data to write.
        :return: The device response status
        :rtype: tuple[int, None]
        """
        if isinstance(data, str):
            if data.startswith("0x") or data.startswith("0X"):
                data = data[2:]
            data = bytes.fromhex(data)
        if isinstance(data, int):
            data = struct.pack(">I", data)
        payload = struct.pack(">II", base_address, offset) + data
        self._logger.debug(f"register_write payload: {payload.hex()}")
        status, _ = self.send_with_command(protocol.Command.CRACKER_WRITE_REGISTER, payload=payload)
        return status, None

    def osc_analog_enable(self, channel: int | str) -> tuple[int, None]:
        """
        Enable osc analog.

        :param channel: Channel to enable, it can be 'A' or 'B', or 0, 1
        :type channel: int | str
        :return: The device response status
        :rtype: tuple[int, None]
        """
        return self._osc_set_analog_channel_enable(channel, True)

    def osc_analog_disable(self, channel: int | str) -> tuple[int, None]:
        """
        Disable osc analog.

        :param channel: Channel to enable, it can be 'A' or 'B', or 0, 1
        :type channel: int | str
        :return: The device response status
        :rtype: tuple[int, None]
        """
        return self._osc_set_analog_channel_enable(channel, False)

    @connection_status_check
    def _osc_set_analog_channel_enable(self, channel: int | str, enable: bool) -> tuple[int, None]:
        """
        Set analog channel enable.

        :param channel: Channel to enable, it can be 'A' or 'B', or 0, 1
        :type channel: int | str
        :param enable: Enable or disable.
        :type enable: bool
        :return: The device response status
        :rtype: tuple[int, None]
        """

        # === Since the device does not support the channel enable function,
        # the information is temporarily saved to the host software. ===
        # config = self.get_current_config()
        # === end ===
        config = self._channel_enable

        channels = ("A", "B")
        if isinstance(channel, str):
            channel = channel.upper()
            if channel in channels:
                channel = channels.index(channel)
            else:
                self._logger.error("Channel error, it should in 'A' or 'B'")
                return self.NON_PROTOCOL_ERROR, None
        else:
            if channel > 1:
                self._logger.error("Channel error, it should in 0 or 1")
                return self.NON_PROTOCOL_ERROR, None
        if channel == 0:
            final_enable = {0: enable, 1: config.osc_channel_1_enable}
        elif channel == 1:
            final_enable = {0: config.osc_channel_0_enable, 1: enable}
        else:
            final_enable = {0: config.osc_channel_0_enable, 1: config.osc_channel_1_enable}
        # === Since the device does not support the channel enable function,
        # the information is temporarily saved to the host software. ===
        # status, res = self._osc_set_analog_all_channel_enable(final_enable)
        self._channel_enable.osc_channel_0_enable = final_enable[0]
        self._channel_enable.osc_channel_1_enable = final_enable[1]
        self._config.osc_channel_0_enable = final_enable[0]
        self._config.osc_channel_1_enable = final_enable[1]
        # === end ===

    @connection_status_check
    def _osc_set_analog_all_channel_enable(self, final_enable: dict[int, bool]):
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
        payload = struct.pack(">B", mask)
        return self.send_with_command(protocol.Command.OSC_ANALOG_CHANNEL_ENABLE, payload=payload)

    @connection_status_check
    def osc_trigger_mode(self, mode: int | str) -> tuple[int, None]:
        """
        Set trigger mode.

        :param mode: Trigger mode. Trigger mode can be one of ("EDGE", "PATTERN") or ("E", "P"),
                     or the index of the string value.
        :type mode: int | str
        :return: The device response status
        :rtype: tuple[int, None]
        """
        modes1 = ("EDGE", "PATTERN")
        modes2 = ("E", "P")
        if isinstance(mode, str):
            mode = mode.upper()
            if mode in modes1:
                mode = modes1.index(mode)
            elif mode in modes2:
                mode = modes2.index(mode)
            else:
                self._logger.error(f"Mode must be one of {modes1} or {modes2} if specified as a string.")
                return self.NON_PROTOCOL_ERROR, None
        else:
            if mode > 1:
                self._logger.error(f"Unknown trigger mode: {mode}, it must be one of (0, 1)")
                return self.NON_PROTOCOL_ERROR, None
        payload = struct.pack(">B", mode)
        self._logger.debug(f"osc_trigger_mode payload: {payload.hex()}")
        status, res = self.send_with_command(protocol.Command.OSC_TRIGGER_MODE, payload=payload)
        if status == protocol.STATUS_OK:
            self._config.osc_trigger_mode = mode

        return status, None

    @connection_status_check
    def osc_trigger_source(self, source: int | str) -> tuple[int, None]:
        """
        Set trigger source.

        :param source: Trigger source: It can be one of ('N', 'A', 'B', 'P', 'R', 'V')
                       or ('Nut', 'ChA', 'ChB', 'Protocol', 'Reset', 'Voltage') or a number in 0 1 2 3 4 5 represent
                       Nut, Channel A, Channel B, Protocol, Reset and Voltage respectively.
        :type source: int | str
        :return: The device response status
        :rtype: tuple[int, None]
        """
        sources1 = ("N", "A", "B", "P", "R", "V")
        sources2 = ("NUT", "CHA", "CHB", "PROTOCOL", "RESET", "VOLTAGE")
        if isinstance(source, str):
            source = source.upper()
            if source in sources1:
                source = sources1.index(source)
            elif source in sources2:
                source = sources2.index(source)
            else:
                self._logger.error(
                    f"Invalid trigger source: {source}. it must be one of {sources1} or {sources2} "
                    f"if specified as a string."
                )
                return self.NON_PROTOCOL_ERROR, None
        else:
            if source > 5:
                self._logger.error("Invalid trigger source, it must be one of (0, 1, 2, 3, 4, 5)")
                return self.NON_PROTOCOL_ERROR, None
        payload = struct.pack(">B", source)
        self._logger.debug(f"osc_trigger_source payload: {payload.hex()}")
        status, res = self.send_with_command(protocol.Command.OSC_ANALOG_TRIGGER_SOURCE, payload=payload)
        if status == protocol.STATUS_OK:
            self._config.osc_trigger_source = source

        return status, None

    @connection_status_check
    def osc_trigger_edge(self, edge: int | str) -> tuple[int, None]:
        """
        Set trigger edge.

        :param edge: Trigger edge. ('up', 'down', 'either') or ('u', 'd', 'e') or 0, 1, 2
                     represent up, down, either, respectively.
        :type edge: int | str
        :return: The device response status
        :rtype: tuple[int, None]
        """
        edges1 = ("UP", "DOWN", "EITHER")
        edges2 = ("U", "D", "E")
        if isinstance(edge, str):
            edge = edge.upper()
            if edge in edges1:
                edge = edges1.index(edge)
            elif edge in edges2:
                edge = edges2.index(edge)
            else:
                self._logger.error(
                    f"Invalid trigger edge: {edge}. it must be one of {edges1} or {edges2} "
                    f"if specified as a string."
                )
                return self.NON_PROTOCOL_ERROR, None
        if edge not in (0, 1, 2):
            self._logger.error("Invalid trigger edge, it must be one of (0, 1, 2)")
            return self.NON_PROTOCOL_ERROR, None

        payload = struct.pack(">B", edge)
        self._logger.debug(f"osc_trigger_edge payload: {payload.hex()}")
        status, res = self.send_with_command(protocol.Command.OSC_TRIGGER_EDGE, payload=payload)
        if status == protocol.STATUS_OK:
            self._config.osc_trigger_edge = edge

        return status, None

    def osc_trigger_level(self, edge_level: int) -> tuple[int, None]:
        """
        Set trigger edge level.

        :param edge_level: Edge level.
        :type edge_level: int
        :return: The device response status
        :rtype: tuple[int, None]
        """
        payload = struct.pack(">h", edge_level)
        self._logger.debug(f"osc_trigger_level payload: {payload.hex()}")
        status, res = self.send_with_command(protocol.Command.OSC_TRIGGER_EDGE_LEVEL, payload=payload)
        if status == protocol.STATUS_OK:
            self._config.osc_trigger_edge_level = edge_level

        return status, None

    @connection_status_check
    def osc_sample_delay(self, delay: int | str) -> tuple[int, None]:
        """
        Set sample delay.

        :param delay: Sample delay. It can be a number or a string, if the input is a string,
                       you can specify the unit, ending with the value,
                       using either 'k' (representing 1024) or 'm' (representing 1024^2).
                       For example, "1k" means 1024 and "2m" means 2097152.
        :type delay: int
        :return: The device response status
        :rtype: tuple[int, None]
        """
        if isinstance(delay, str):
            m = re.match(r"^(\d+)([kKmM])?$", delay)

            if m:
                delay = int(m.group(1))
            else:
                self._logger.error(
                    "Input format error, it should be a number or a string "
                    "ending with the value, using either k or m."
                )
                return self.NON_PROTOCOL_ERROR, None

            if m.group(2):
                unit = m.group(2).lower()
                if unit == "k":
                    delay *= 1024
                elif unit == "m":
                    delay *= 1024 * 1024
                else:
                    self._logger.error(f"Unknown unit: {unit}")
                    return self.NON_PROTOCOL_ERROR, None
        payload = struct.pack(">i", delay)
        self._logger.debug(f"osc_sample_delay payload: {payload.hex()}")
        status, res = self.send_with_command(protocol.Command.OSC_SAMPLE_DELAY, payload=payload)
        if status == protocol.STATUS_OK:
            self._config.osc_sample_delay = delay

        return status, None

    @connection_status_check
    def osc_sample_length(self, length: int | str) -> tuple[int, None]:
        """
        Set sample length.

        :param length: Sample length. It can be a number or a string, if the input is a string,
                       you can specify the unit, ending with the value,
                       using either 'k' (representing 1024) or 'm' (representing 1024^2).
                       For example, "1k" means 1024 and "2m" means 2097152.
        :type length: int | str
        :return: The device response status
        :rtype: tuple[int, None]
        """
        if isinstance(length, str):
            m = re.match(r"^(\d+)([kKmM])?$", length)

            if m:
                length = int(m.group(1))
            else:
                self._logger.error(
                    "Input format error, it should be a number or a string "
                    "ending with the value, using either k or m."
                )
                return self.NON_PROTOCOL_ERROR, None

            if m.group(2):
                unit = m.group(2).lower()
                if unit == "k":
                    length *= 1024
                elif unit == "m":
                    length *= 1024 * 1024
                else:
                    self._logger.error(f"Unknown unit: {unit}")
                    return self.NON_PROTOCOL_ERROR, None
        # Cracker only supports sampling length in multiples of 1024,
        # record actual length to truncate waveform data later.
        self._osc_sample_length = length
        payload = struct.pack(">I", length)
        self._logger.debug(f"osc_sample_length payload: {payload.hex()}")
        status, res = self.send_with_command(protocol.Command.OSC_SAMPLE_LENGTH, payload=payload)
        if status == protocol.STATUS_OK:
            self._config.osc_sample_length = length

        return status, None

    @connection_status_check
    def osc_sample_clock(self, clock: int | str) -> tuple[int, None]:
        """
        Set osc sample rate

        :param clock: The sample rate in kHz can be one of (65000, 48000, 24000, 12000, 8000)
                      or a string in (65M, 48M, 24M, 12M, 8M).
        :type clock: int | str
        :return: The device response status
        :rtype: tuple[int, None]
        """
        if isinstance(clock, str):
            clock = clock.upper()
            if clock == "65M":
                clock = 65000
            elif clock == "64M":
                clock = 64000
            elif clock == "48M":
                clock = 48000
            elif clock == "40M":
                clock = 40000
            elif clock == "24M":
                clock = 24000
            elif clock == "12M":
                clock = 12000
            elif clock == "8M":
                clock = 8000
            else:
                if re.match(r"^\d+$", clock):
                    clock = int(clock)
                else:
                    self._logger.error(
                        "UnSupport osc sample rate, it should in " "65M or 64M or 48M or 40M or 24M or 12M or 8M"
                    )
                    return self.NON_PROTOCOL_ERROR, None
        if clock not in (65000, 64000, 48000, 40000, 24000, 12000, 8000, 4000):
            self._logger.error(
                "UnSupport osc sample clock, it should in " "(65000, 64000, 48000, 40000, 24000, 12000, 8000, 4000)"
            )
            return self.NON_PROTOCOL_ERROR, None
        payload = struct.pack(">I", clock)
        self._logger.debug(f"osc_sample_clock_rate payload: {payload.hex()}")
        status, res = self.send_with_command(protocol.Command.OSC_SAMPLE_RATE, payload=payload)
        if status == protocol.STATUS_OK:
            self._config.osc_sample_clock = clock

        return status, None

    @connection_status_check
    def osc_analog_gain(self, channel: int | str, gain: int) -> tuple[int, None]:
        """
        Set analog gain.

        :param channel: Analog channel, it can be 'A' or 'B', or 0, 1
        :type channel: int | str
        :param gain: Analog gain.
        :type gain: int
        :return: The device response status
        :rtype: tuple[int, None]
        """
        channels = ("A", "B")
        if isinstance(channel, str):
            channel = channel.upper()
            if channel in channels:
                channel = channels.index(channel)
            else:
                self._logger.error("Channel error, it should in 'A' or 'B'")
                return self.NON_PROTOCOL_ERROR, None
        else:
            if channel > 1:
                self._logger.error("Channel error, it should in 0 or 1")
                return self.NON_PROTOCOL_ERROR, None

        if not 1 <= gain <= 50:
            self._logger.error("Gain error, it should in 1 to 50")
            return self.NON_PROTOCOL_ERROR, None
        payload = struct.pack(">BB", channel, gain)
        status, res = self.send_with_command(protocol.Command.OSC_ANALOG_GAIN, payload=payload)
        if status == protocol.STATUS_OK:
            if channel == 0:
                self._config.osc_channel_0_gain = gain
            elif channel == 1:
                self._config.osc_channel_1_gain = gain

    @connection_status_check
    def osc_sample_clock_phase(self, phase: int) -> tuple[int, None]:
        """
        Set sample phase.

        :param phase: Sample phase.
        :type phase: int
        :return: The device response status
        :rtype: tuple[int, None]
        """
        payload = struct.pack(">I", phase)
        self._logger.debug(f"osc_sample_clock_phase payload: {payload.hex()}")
        status, res = self.send_with_command(protocol.Command.OSC_CLOCK_SAMPLE_PHASE, payload=payload)
        if status == protocol.STATUS_OK:
            self._config.osc_sample_phase = phase

        return status, None

    def nut_voltage_disable(self) -> tuple[int, None]:
        """
        Disable the nut voltage.

        :return: The device response status
        :rtype: tuple[int, None]
        """
        return self._nut_set_enable(False)

    def nut_voltage_enable(self) -> tuple[int, None]:
        """
        Enable the nut voltage.

        :return: The device response status
        :rtype: tuple[int, None]
        """
        return self._nut_set_enable(True)

    @connection_status_check
    def _nut_set_enable(self, enable: int | bool) -> tuple[int, None]:
        """
        Set nut enable.

        :param enable: Enable or disable. 0 for disable, 1 for enable if specified as a integer.
        :type enable: int | bool
        :return: The device response status
        :rtype: tuple[int, None]
        """
        if isinstance(enable, int):
            enable = True if enable == 1 else False
        payload = struct.pack(">?", enable)
        self._logger.debug(f"nut_enable payload: {payload.hex()}")
        status, res = self.send_with_command(protocol.Command.NUT_ENABLE, payload=payload)
        if status == protocol.STATUS_OK:
            self._config.nut_enable = enable

        return status, None

    @connection_status_check
    def nut_voltage(self, voltage: float | str | int) -> tuple[int, None]:
        """
        Set nut voltage.

        :param voltage: Nut voltage can be a number or a string. If the input is a float,
                        the voltage will be treated as a V value. If the input is a string,
                        you can specify the unit, ending with the value, using either mV or V.
        :type voltage: float | str | int
        :return: The device response status
        :rtype: tuple[int, None]
        """
        if isinstance(voltage, str):
            m = re.match(r"^(\d+(?:\.\d+)?)([mM]?[vV])?$", voltage)
            if not m:
                self._logger.error(
                    "Input format error: " "it should be a number or a string and end with a unit in V or mV."
                )
                return self.NON_PROTOCOL_ERROR, None
            voltage = float(m.group(1))
            if m.group(2):
                unit = m.group(2)
            else:
                unit = "v"
            if unit.lower() == "v":
                voltage = voltage * 1000
        else:
            voltage = voltage * 1000
        voltage = int(voltage)
        if voltage > 4000 or voltage < 2000:
            self._logger.error("Nut voltage error, it should in 2.0V to 4.0V")
            return self.NON_PROTOCOL_ERROR, None
        payload = struct.pack(">I", voltage)
        self._logger.debug(f"nut_voltage payload: {payload.hex()}")
        status, res = self.send_with_command(protocol.Command.NUT_VOLTAGE, payload=payload)
        if status == protocol.STATUS_OK:
            self._config.nut_voltage = voltage / 1000

        return status, None

    @connection_status_check
    def nut_clock_disable(self) -> tuple[int, None]:
        """
        Disable the nut clock.

        :return: The device response status
        :rtype: tuple[int, None]
        """
        return self._nut_set_clock_enable(False)

    @connection_status_check
    def nut_clock_enable(self) -> tuple[int, None]:
        """
        Enable the nut clock.

        :return: The device response status
        :rtype: tuple[int, None]
        """
        return self._nut_set_clock_enable(True)

    @connection_status_check
    def _nut_set_clock_enable(self, enable: bool) -> tuple[int, None]:
        payload = struct.pack(">?", enable)
        self._logger.debug(f"nut_set_clock_enable payload: {payload.hex()}")
        status, res = self.send_with_command(protocol.Command.NUT_CLOCK_ENABLE, payload=payload)
        if status == protocol.STATUS_OK:
            self._config.nut_clock_enable = enable

        return status, None

    @connection_status_check
    def nut_clock_freq(self, clock: float | int | str) -> tuple[int, None]:
        """
        Set nut clock.

        :param clock: The clock of the nut in kHz
        :type clock: float | int | str
        :return: The device response status
        :rtype: tuple[int, None]
        """
        if isinstance(clock, str):
            clock = clock.upper()
            if clock == "64M":
                clock = 64000
            if clock == "40M":
                clock = 40000
            elif clock == "24M":
                clock = 24000
            elif clock == "12M":
                clock = 12000
            elif clock == "8M":
                clock = 8000
            elif clock == "4M":
                clock = 4000
            else:
                self._logger.error(f"Unknown clock type: {clock}, 64M or 40M or 24M or 12M or 8M or 4M")
                return protocol.STATUS_ERROR, None
        clock = round(clock)  # TODO 这里由于这些设置是在cracker中的server程序完成的，目前只支持这些整数值，后续优化
        validate_nut_clock = (64000, 40000, 24000, 12000, 8000, 4000)
        if clock not in validate_nut_clock:
            self._logger.error(f"UnSupport osc clock, it should in {validate_nut_clock}")
        payload = struct.pack(">I", clock)
        self._logger.debug(f"nut_set_clock payload: {payload.hex()}")
        status, res = self.send_with_command(protocol.Command.NUT_CLOCK, payload=payload)
        if status == protocol.STATUS_OK:
            self._config.nut_clock = clock

        return status, None

    @connection_status_check
    def nut_timeout_ms(self, timeout: int) -> tuple[int, None]:
        """
        Set nut timeout.

        :param timeout: Nut timeout.
        :type timeout: int
        :return: The device response status
        :rtype: tuple[int, None]
        """
        payload = struct.pack(">I", timeout)
        self._logger.debug(f"nut_timeout_ms payload: {payload.hex()}")
        status, res = self.send_with_command(protocol.Command.NUT_TIMEOUT, payload=payload)
        if status == protocol.STATUS_OK:
            self._config.nut_timeout = timeout

        return status, None

    def spi_enable(self) -> tuple[int, None]:
        """
        Enable the SPI interface.

        :return: Device response status and received data: (status, response).
        :rtype: tuple[int, None]
        """
        return self._spi_enable(True)

    def spi_disable(self) -> tuple[int, None]:
        """
        Disable the SPI interface.

        :return: Device response status and received data: (status, response).
        :rtype: tuple[int, None]
        """
        return self._spi_enable(False)

    @connection_status_check
    def _spi_enable(self, enable: bool):
        """
        Configure whether the SPI interface is enabled.

        :param enable: True to enable, False to disable.
        :type enable: bool
        :return: Device response status and received data: (status, response).
        :rtype: tuple[int, None]
        """
        payload = struct.pack(">?", enable)
        self._logger.debug(f"cracker_spi_enable payload: {payload.hex()}")
        status, res = self.send_with_command(protocol.Command.CRACKER_SPI_ENABLE, payload=payload)
        if status == protocol.STATUS_OK:
            self._config.nut_spi_enable = enable
        return status, res

    @connection_status_check
    def spi_reset(self) -> tuple[int, None]:
        """
        Reset the SPI hardware.

        :return: Device response status and received data: (status, response).
        :rtype: tuple[int, None]
        """
        payload = None
        self._logger.debug(f"cracker_spi_reset payload: {payload}")
        return self.send_with_command(protocol.Command.CRACKER_SPI_RESET)

    @connection_status_check
    def spi_config(
        self,
        speed: float | None = None,
        cpol: serial.SpiCpol | int | str | None = None,
        cpha: serial.SpiCpha | int | str | None = None,
        csn_auto: bool | None = None,
        csn_delay: bool | None = None,
    ) -> tuple[int, None | str]:
        """
        Configure the SPI interface parameters, including CPOL (clock polarity) and CPHA (clock phase).

        Accepts enum members from ``cracknuts.cracker.serial`` or direct numeric/string values
        (eliminating the need to import the enum module). Invalid values are rejected with
        an error and the function returns ``(self.NON_PROTOCOL_ERROR, None)``.

        :param speed: Communication speed in kHz (default 10 kHz). Relationship to PSC register:
            speed = (100e6) / (2 * PSC). Default: current config value.
        :type speed: float | None
        :param cpol: Clock polarity. Can be a ``serial.SpiCpol`` enum, int (0=LOW, 1=HIGH),
            or string ("LOW", "HIGH", "0", "1"). Default: current config value.
        :type cpol: serial.SpiCpol | int | str | None
        :param cpha: Clock phase. Can be a ``serial.SpiCpha`` enum, int (0=LOW, 1=HIGH),
            or string ("LOW", "HIGH", "0", "1"). Default: current config value.
        :type cpha: serial.SpiCpha | int | str | None
        :param csn_auto: If True, the chip-select (CSN) signal is pulled low only during data
            communication. If False, CSN remains low continuously.
            Default: current config value.
        :type csn_auto: bool | None
        :param csn_delay: If True, the CSN signal stays low during the delay period. If False,
            CSN is high during the delay. Default: current config value.
        :type csn_delay: bool | None
        :return: Device response status and optional error message.
        :rtype: tuple[int, None | str]
        """

        if speed is None or cpol is None or csn_auto is None or csn_delay is None:
            config = self.get_current_config()
            if config is None:
                self._logger.error("Get config from cracker error.")
                return self.NON_PROTOCOL_ERROR, None
            if speed is None:
                speed = config.nut_spi_speed
            if cpol is None:
                cpol = config.nut_spi_cpol
            if cpha is None:
                cpha = config.nut_spi_cpha
            if csn_auto is None:
                csn_auto = config.nut_spi_csn_auto
            if csn_delay is None:
                csn_delay = config.nut_spi_csn_delay

        # Coerce cpol and cpha to enum types
        cpol_map = {
            0: serial.SpiCpol.SPI_CPOL_LOW,
            1: serial.SpiCpol.SPI_CPOL_HIGH,
            "0": serial.SpiCpol.SPI_CPOL_LOW,
            "1": serial.SpiCpol.SPI_CPOL_HIGH,
            "LOW": serial.SpiCpol.SPI_CPOL_LOW,
            "HIGH": serial.SpiCpol.SPI_CPOL_HIGH,
        }
        cpha_map = {
            0: serial.SpiCpha.SPI_CPHA_LOW,
            1: serial.SpiCpha.SPI_CPHA_HIGH,
            "0": serial.SpiCpha.SPI_CPHA_LOW,
            "1": serial.SpiCpha.SPI_CPHA_HIGH,
            "LOW": serial.SpiCpha.SPI_CPHA_LOW,
            "HIGH": serial.SpiCpha.SPI_CPHA_HIGH,
        }

        try:
            if isinstance(cpol, serial.SpiCpol):
                pass
            elif isinstance(cpol, int | str):
                if isinstance(cpol, str):
                    cpol = cpol.strip().upper()
                if cpol not in cpol_map:
                    self._logger.error(f"Invalid cpol: {cpol}. Allowed values: {list(cpol_map.keys())}")
                    return self.NON_PROTOCOL_ERROR, None
                cpol = cpol_map[cpol]
            else:
                self._logger.error(f"Invalid cpol type: {type(cpol)}")
                return self.NON_PROTOCOL_ERROR, None

            if isinstance(cpha, serial.SpiCpha):
                pass
            elif isinstance(cpha, int | str):
                if isinstance(cpha, str):
                    cpha = cpha.strip().upper()
                if cpha not in cpha_map:
                    self._logger.error(f"Invalid cpha: {cpha}. Allowed values: {list(cpha_map.keys())}")
                    return self.NON_PROTOCOL_ERROR, None
                cpha = cpha_map[cpha]
            else:
                self._logger.error(f"Invalid cpha type: {type(cpha)}")
                return self.NON_PROTOCOL_ERROR, None
        except Exception as e:
            self._logger.error(f"Error coercing SPI parameters: {e}")
            return self.NON_PROTOCOL_ERROR, None

        # System clock is 100e6
        # Clock divider is 2
        # psc max is 65535
        psc = 100e6 / 2 / speed
        if psc > 65535 or psc < 2:
            self._logger.error("Not support speed.")
            return self.NON_PROTOCOL_ERROR, f"Not support speed {speed}."

        if not psc.is_integer():
            psc = round(psc)
            if psc > 65535 or psc < 2:
                self._logger.error(f"Not support  speed {speed}.")
                return self.NON_PROTOCOL_ERROR, f"Not support speed {speed}."
            _speed = speed
            speed = round(100e6 / 2 / psc, 2)
            self._logger.warning(
                f"The speed: [{_speed}] cannot calculate an integer Prescaler, "
                f"so the integer value is set to {speed} and psc is {psc}."
            )

        speed = round(100e6 / 2 / psc, 2)

        payload = struct.pack(">HBB??", int(psc), cpol.value, cpha.value, csn_auto, csn_delay)
        self._logger.debug(f"cracker_spi_config payload: {payload.hex()}")
        status, res = self.send_with_command(protocol.Command.CRACKER_SPI_CONFIG, payload=payload)
        if status == protocol.STATUS_OK:
            self._config.nut_spi_speed = speed
            self._config.nut_spi_cpol = cpol
            self._config.nut_spi_cpha = cpha
            self._config.nut_spi_csn_auto = csn_auto
            self._config.nut_spi_csn_delay = csn_delay
        return status, res

    @staticmethod
    def _find_divisors(clock):
        if clock <= 0:
            raise ValueError("Input must be a positive integer.")

        n = clock / 2

        divisors = []

        for i in range(1, int(n**0.5) + 1):
            q, b = divmod(n, i)
            if b == 0 and 2 < q < 65535:
                divisors.append(int(i))
                if i != n // i:
                    divisors.append(int(n // i))

        return sorted(divisors)

    @connection_status_check
    def spi_transceive_delay_transceive(
        self,
        tx_data1: bytes | str | int | None,
        tx_data2: bytes | str | int | None,
        is_delay: bool,
        delay: int,
        is_trigger: bool,
    ) -> tuple[int, tuple[bytes | None, bytes | None] | None]:
        """
        Send tx_data1 via SPI, wait for the specified delay (in units of 10 ns), then send tx_data2
        and read back the response.

        When is_trigger=True, the Trigger signal is pulled low at the start of transmission and
        high upon completion::

            TRIG: ───┐            ┌────────────┐            ┌─── HIGH
                     |            |            |            |
                     └────────────┘            └────────────┘    LOW
                     ┌────────────┬────────────┬────────────┐
                     │  tx_data1  │    delay   │  tx_data2  │
                     └────────────┴────────────┴────────────┘

        When is_trigger=False, the Trigger signal remains unchanged::

            TRIG: ────────────────────────────────────────────── HIGH

                                                                 LOW
                     ┌────────────┬────────────┬────────────┐
                     │  tx_data1  │   timeout  │  rx_data2  │
                     └────────────┴────────────┴────────────┘

        :param tx_data1: Data to send in the first phase. Accepts bytes, a hex string, an integer
                         (converted to big-endian bytes using the minimum required length), or None.
        :type tx_data1: bytes | str | int | None
        :param tx_data2: Data to send in the second phase. Same type rules as tx_data1.
        :type tx_data2: bytes | str | int | None
        :param is_delay: Whether to enable the inter-phase delay.
        :type is_delay: bool
        :param delay: Delay between the two phases, in units of 10 nanoseconds.
        :type delay: int
        :param is_trigger: Whether to generate a trigger signal during transmission
                           (pulled low at start, high at end).
        :type is_trigger: bool
        :return: Device response status and received data: (status, (response1, response2)).
        :rtype: tuple[int, tuple[bytes | None, bytes | None] | None]
        :raises TypeError: If tx_data1 or tx_data2 is not bytes, str, int, or None.
        """
        if isinstance(tx_data1, int):
            byte_length = max(1, (tx_data1.bit_length() + 7) // 8)
            tx_data1 = tx_data1.to_bytes(byte_length, byteorder="big")
        elif isinstance(tx_data1, str):
            tx_data1 = bytes.fromhex(tx_data1)
        elif tx_data1 is not None and not isinstance(tx_data1, bytes):
            raise TypeError(f"tx_data1 must be bytes, str, int, or None, got {type(tx_data1).__name__}")
        if isinstance(tx_data2, int):
            byte_length = max(1, (tx_data2.bit_length() + 7) // 8)
            tx_data2 = tx_data2.to_bytes(byte_length, byteorder="big")
        elif isinstance(tx_data2, str):
            tx_data2 = bytes.fromhex(tx_data2)
        elif tx_data2 is not None and not isinstance(tx_data2, bytes):
            raise TypeError(f"tx_data2 must be bytes, str, int, or None, got {type(tx_data2).__name__}")
        tx_data1_len = 0 if tx_data1 is None else len(tx_data1)
        tx_data2_len = 0 if tx_data2 is None else len(tx_data2)
        payload = struct.pack(">?IH?", is_delay, delay, tx_data2_len, is_trigger)
        if tx_data1 is not None:
            payload += tx_data1
        if tx_data2 is not None:
            payload += tx_data2
        self._logger.debug(f"spi_transmit_delay_receive payload: {payload.hex()}")
        status, res = self.send_with_command(protocol.Command.CRACKER_SPI_TRANSCEIVE, payload=payload)
        if status != protocol.STATUS_OK:
            self._logger.error(f"Receive status code error [{status}]")
            return status, (None, None)
        else:
            return status, (res[:tx_data1_len], res[-tx_data2_len:])

    def spi_transmit(self, tx_data: bytes | str | int, is_trigger: bool = False) -> tuple[int, None]:
        """
        Send data over the SPI interface, optionally generating a trigger signal after transmission.

        When is_trigger=True, the Trigger signal is pulled low at the start of transmission and
        high upon completion::

            TRIG: ───┐            ┌─── HIGH
                     |            |
                     └────────────┘    LOW
                     ┌────────────┐
                     │   tx_data  │
                     └────────────┘

        When is_trigger=False, the Trigger signal remains unchanged::

            TRIG: ──────────────────── HIGH

                                       LOW
                     ┌────────────┐
                     │   tx_data  │
                     └────────────┘

        :param tx_data: Data to send. Accepts bytes, a hex string, or an integer (converted to
                        big-endian bytes using the minimum required length).
        :type tx_data: bytes | str | int
        :param is_trigger: Whether to generate a trigger signal during transmission
                           (pulled low at start, high at end).
        :type is_trigger: bool
        :return: Device response status and None: (status, None).
        :rtype: tuple[int, None]
        """
        status, _ = self.spi_transceive_delay_transceive(
            tx_data1=tx_data, tx_data2=None, is_delay=False, delay=1_000_000_000, is_trigger=is_trigger
        )
        return status, None

    def spi_receive(
        self, rx_count: int, dummy: bytes | str = b"\x00", is_trigger: bool = False
    ) -> tuple[int, bytes | None]:
        """
        Receive ``rx_count`` bytes over the SPI interface.

        When ``is_trigger=True``, the Trigger signal is pulled low at the start of transmission and
        high upon completion::

            TRIG: ───┐            ┌─── HIGH
                     |            |
                     └────────────┘    LOW
                     ┌────────────┐
                     │   rx_data  │
                     └────────────┘

        When ``is_trigger=False``, the Trigger signal remains unchanged::

            TRIG: ──────────────────── HIGH

                                       LOW
                     ┌────────────┐
                     │   rx_data  │
                     └────────────┘

        :param rx_count: Number of bytes to read.
        :type rx_count: int
        :param dummy: Filler data sent during the SPI read phase.
        :type dummy: bytes | str
        :param is_trigger: Whether to generate a trigger signal during data transmission
            (pulled low at start, high at end).
        :type is_trigger: bool
        :return: Device response status and received data: (status, response).
            Returns None if an exception is caught.
        :rtype: tuple[int, bytes | None]
        """
        if isinstance(dummy, str):
            dummy = bytes.fromhex(dummy)
        dummy = dummy[:1]

        status, (_, res) = self.spi_transceive_delay_transceive(
            tx_data1=dummy * rx_count, tx_data2=None, is_delay=False, delay=1_000_000_000, is_trigger=is_trigger
        )

        return status, res

    def spi_transmit_delay_receive(
        self,
        tx_data: bytes | str | int,
        delay: int,
        rx_count: int,
        dummy: bytes | str = b"\x00",
        is_trigger: bool = False,
    ) -> tuple[int, bytes | None]:
        """
        Send tx_data over SPI, wait for the specified delay (in units of 10 ns), then clock out
        rx_count dummy bytes and capture the slave's response as rx_data.

        When is_trigger=True, the Trigger signal is pulled low at the start of transmission and
        high upon completion::

            TRIG: ───┐            ┌────────────┐            ┌─── HIGH
                     |            |            |            |
                     └────────────┘            └────────────┘    LOW
                     ┌────────────┬────────────┬────────────┐
            MASTER   │  tx_data   │    delay   │    dummy   │
                     └────────────┴────────────┴────────────┘
                     ┌────────────┬────────────┬────────────┐
            SLAVE    │   dummy    │    delay   │   rx_data  │
                     └────────────┴────────────┴────────────┘

        When is_trigger=False, the Trigger signal remains unchanged::

            TRIG: ────────────────────────────────────────────── HIGH

                                                                 LOW
                     ┌────────────┬────────────┬────────────┐
            MASTER   │  tx_data   │    delay   │    dummy   │
                     └────────────┴────────────┴────────────┘
                     ┌────────────┬────────────┬────────────┐
            SLAVE    │   dummy    │    delay   │   rx_data  │
                     └────────────┴────────────┴────────────┘

        :param tx_data: Data to send. Accepts bytes, a hex string, or an integer (converted to
                        big-endian bytes using the minimum required length).
        :type tx_data: bytes | str | int
        :param delay: Delay between transmit and receive phases, in units of 10 nanoseconds.
        :type delay: int
        :param rx_count: Number of bytes to read.
        :type rx_count: int
        :param dummy: Filler byte(s) clocked out during the receive phase.
        :type dummy: bytes | str
        :param is_trigger: Whether to generate a trigger signal during transmission
                           (pulled low at start, high at end).
        :type is_trigger: bool
        :return: Device response status and received data: (status, response).
        :rtype: tuple[int, bytes | None]
        """
        status, (_, res) = self.spi_transceive_delay_transceive(
            tx_data1=tx_data, tx_data2=dummy * rx_count, is_delay=True, delay=delay, is_trigger=is_trigger
        )

        return status, res

    def spi_transceive(
        self, tx_data: bytes | str | int, rx_count: int = None, dummy: bytes | str = b"\x00", is_trigger: bool = False
    ) -> tuple[int, bytes | None]:
        """
        Send tx_data over the SPI interface and receive data simultaneously. By default, the number
        of bytes received equals the length of tx_data.

        When is_trigger=True, the Trigger signal is pulled low at the start of transmission and
        high upon completion::

            TRIG: ───┐            ┌─── HIGH
                     |            |
                     └────────────┘    LOW
                     ┌────────────┐
                     │   tx_data  │
                     └────────────┘
                     ┌────────────┐
                     │   rx_data  │
                     └────────────┘

        When is_trigger=False, the Trigger signal remains unchanged::

            TRIG: ──────────────────── HIGH

                                       LOW
                     ┌────────────┐
                     │   tx_data  │
                     └────────────┘
                     ┌────────────┐
                     │   rx_data  │
                     └────────────┘

        :param tx_data: Data to send. Accepts bytes, a hex string, or an integer (converted to
                        big-endian bytes using the minimum required length).
        :type tx_data: bytes | str | int
        :param rx_count: Number of bytes to receive. Defaults to the length of tx_data.
                         If specified:
                         1. When rx_count > len(tx_data), dummy bytes are appended to tx_data.
                         2. When rx_count < len(tx_data), the received data is truncated to rx_count.
        :type rx_count: int
        :param dummy: Filler byte used to pad tx_data when rx_count > len(tx_data).
        :type dummy: bytes | str
        :param is_trigger: Whether to generate a trigger signal during transmission
                           (pulled low at start, high at end).
        :type is_trigger: bool
        :return: Device response status and received data: (status, response).
        :rtype: tuple[int, bytes | None]
        :raises TypeError: If tx_data is not bytes, str, or int.
        """
        if isinstance(dummy, str):
            dummy = bytes.fromhex(dummy)
        dummy = dummy[:1]
        if isinstance(tx_data, int):
            byte_length = max(1, (tx_data.bit_length() + 7) // 8)
            tx_data = tx_data.to_bytes(byte_length, byteorder="big")
        elif isinstance(tx_data, str):
            tx_data = bytes.fromhex(tx_data)
        elif not isinstance(tx_data, bytes):
            raise TypeError(f"tx_data must be bytes, str, or int, got {type(tx_data).__name__}")
        tx_data_len = len(tx_data)
        if rx_count and rx_count > tx_data_len:
            tx_data += dummy * (rx_count - tx_data_len)

        status, (res, _) = self.spi_transceive_delay_transceive(
            tx_data1=tx_data, tx_data2=None, is_delay=False, delay=0, is_trigger=is_trigger
        )

        if rx_count and tx_data_len > rx_count:
            res = res[:rx_count]

        return status, res

    def i2c_enable(self) -> tuple[int, None]:
        """
        Enable the I2C interface.

        :return: Device response status and received data: (status, response).
        :rtype: tuple[int, None]
        """
        return self._i2c_enable(True)

    def i2c_disable(self) -> tuple[int, None]:
        """
        Disable the I2C interface.

        :return: Device response status and received data: (status, response).
        :rtype: tuple[int, None]
        """
        return self._i2c_enable(False)

    @connection_status_check
    def _i2c_enable(self, enable: bool):
        """
        Enable or disable the I2C interface.

        :param enable: True to enable, False to disable.
        :type enable: bool
        :return: Device response status and received data: (status, response).
        :rtype: tuple[int, None]
        """
        payload = struct.pack(">?", enable)
        self._logger.debug(f"cracker_i2c_enable payload: {payload.hex()}")
        status, res = self.send_with_command(protocol.Command.CRACKER_I2C_ENABLE, payload=payload)
        if status == protocol.STATUS_OK:
            self._config.nut_i2c_enable = enable
        return status, res

    @connection_status_check
    def i2c_reset(self) -> tuple[int, None]:
        """
        Reset the I2C configuration.

        :return: Device response status and received data: (status, response).
        :rtype: tuple[int, None]
        """
        payload = None
        self._logger.debug(f"cracker_i2c_reset payload: {payload}")
        return self.send_with_command(protocol.Command.CRACKER_I2C_RESET)

    @connection_status_check
    def i2c_config(
        self,
        dev_addr: int | str | None = None,
        speed: serial.I2cSpeed | int | str | None = None,
        enable_stretch: bool = False,
    ) -> tuple[int, None]:
        """
        Configure the I2C interface.

        Accepts enum members from ``cracknuts.cracker.serial`` or direct numeric/string values
        (eliminating the need to import the enum module). Invalid values are rejected with
        an error and the function returns ``(self.NON_PROTOCOL_ERROR, None)``.

        :param dev_addr: Device address (0-127). Can be an int (0-127), or string in hex format
            ("0x1A", "1A") or decimal format ("26"). Default: current config value.
        :type dev_addr: int | str | None
        :param speed: Bus speed. Can be a ``serial.I2cSpeed`` enum, int (100000, 400000, 1000000,
            3400000, 5000000 Hz), or string ("100K", "400K", "1M", "3400K", "5M").
            Default: current config value.
        :type speed: serial.I2cSpeed | int | str | None
        :param enable_stretch: Whether to enable clock stretching.
        :type enable_stretch: bool
        :return: Device response status and None.
        :rtype: tuple[int, None]
        """

        if dev_addr is None or speed is None:
            config = self.get_current_config()
            if config is None:
                self._logger.error("Get config from cracker error.")
                return self.NON_PROTOCOL_ERROR, None
            if dev_addr is None:
                dev_addr = config.nut_i2c_dev_addr
            if speed is None:
                speed = config.nut_i2c_speed

        # Coerce dev_addr (allow hex string or decimal)
        if isinstance(dev_addr, str):
            s = dev_addr.strip()
            if s.lower().startswith("0x"):
                try:
                    dev_addr = int(s, 16)
                except Exception:
                    self._logger.error(f"Invalid dev_addr hex string: {dev_addr}")
                    return self.NON_PROTOCOL_ERROR, None
            else:
                if s.isdigit():
                    dev_addr = int(s)
                else:
                    try:
                        dev_addr = int(s, 16)
                    except Exception:
                        self._logger.error(f"Invalid dev_addr string: {dev_addr}")
                        return self.NON_PROTOCOL_ERROR, None

        if not isinstance(dev_addr, int) or not (0 <= dev_addr <= 0x7F):
            self._logger.error("I2C dev_addr must be an integer in range 0..127")
            return self.NON_PROTOCOL_ERROR, None

        # Mappings for I2C speeds
        speed_map = {
            100000: serial.I2cSpeed.STANDARD_100K,
            400000: serial.I2cSpeed.FAST_400K,
            1000000: serial.I2cSpeed.FAST_PLUS_1M,
            3400000: serial.I2cSpeed.HIGH_SPEED_3400K,
            5000000: serial.I2cSpeed.ULTRA_FAST_5M,
            "100K": serial.I2cSpeed.STANDARD_100K,
            "400K": serial.I2cSpeed.FAST_400K,
            "1M": serial.I2cSpeed.FAST_PLUS_1M,
            "3400K": serial.I2cSpeed.HIGH_SPEED_3400K,
            "5M": serial.I2cSpeed.ULTRA_FAST_5M,
        }

        try:
            if isinstance(speed, serial.I2cSpeed):
                pass
            elif isinstance(speed, int | str):
                if isinstance(speed, str):
                    speed = speed.strip().upper()
                if speed not in speed_map:
                    self._logger.error(f"Invalid I2C speed: {speed}. Allowed values: {list(speed_map.keys())}")
                    return self.NON_PROTOCOL_ERROR, None
                speed = speed_map[speed]
            else:
                self._logger.error(f"Invalid speed type: {type(speed)}")
                return self.NON_PROTOCOL_ERROR, None
        except Exception as e:
            self._logger.error(f"Error coercing I2C speed: {e}")
            return self.NON_PROTOCOL_ERROR, None

        payload = struct.pack(">BB?", dev_addr, speed.value, enable_stretch)
        self._logger.debug(f"cracker_i2c_config payload: {payload.hex()}")
        status, res = self.send_with_command(protocol.Command.CRACKER_I2C_CONFIG, payload=payload)
        if status == protocol.STATUS_OK:
            self._config.nut_i2c_dev_addr = dev_addr
            self._config.nut_i2c_speed = speed
        return status, res

    @connection_status_check
    def _i2c_transceive(
        self,
        tx_data: bytes | str | int | None,
        combined_transfer_count_1: int,
        combined_transfer_count_2: int,
        transfer_rw: tuple[int, int, int, int, int, int, int, int],
        transfer_lens: tuple[int, int, int, int, int, int, int, int],
        is_delay: bool,
        delay: int,
        is_trigger: bool,
    ) -> tuple[int, bytes | None]:
        """
        Basic API for sending and receiving data through the I2C protocol.

        :param tx_data: Data to be sent. Accepts bytes, a hex string, an integer (converted to
                        big-endian bytes using the minimum required length), or None.
        :type tx_data: bytes | str | int | None
        :param combined_transfer_count_1: The first combined transmit transfer count.
        :type combined_transfer_count_1: int
        :param combined_transfer_count_2: The second combined transmit transfer count.
        :type combined_transfer_count_2: int
        :param transfer_rw: The read/write configuration tuple of the four transfers in the two sets
                            of Combined Transfer, with a tuple length of 8, where 0 represents write
                            and 1 represents read.
        :type transfer_rw: tuple[int, int, int, int, int, int, int, int, int]
        :param transfer_lens: The transfer length tuple of the four transfers in the two combined transmit sets.
        :type transfer_lens: tuple[int, int, int, int, int, int, int, int]
        :param is_delay: Whether the transmit delay is enabled.
        :type is_delay: bool
        :param delay: Transmit delay duration, in nanoseconds, with a minimum effective duration of 10 nanoseconds.
        :type delay: int
        :param is_trigger: Whether the transmit trigger is enabled.
        :type is_trigger: bool
        :return: The device response status and the data received from the I2C device.
                 Return None if an exception is caught.
        :rtype: tuple[int, bytes | None]
        :raises TypeError: If tx_data is not bytes, str, int, or None.
        """
        if isinstance(tx_data, int):
            byte_length = max(1, (tx_data.bit_length() + 7) // 8)
            tx_data = tx_data.to_bytes(byte_length, byteorder="big")
        elif isinstance(tx_data, str):
            tx_data = bytes.fromhex(tx_data)
        elif tx_data is not None and not isinstance(tx_data, bytes):
            raise TypeError(f"tx_data must be bytes, str, int, or None, got {type(tx_data).__name__}")

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
            ">?I3B8H?",
            is_delay,
            delay,
            combined_transfer_count_1,
            combined_transfer_count_2,
            transfer_rw_num,
            *transfer_lens,
            is_trigger,
        )

        if tx_data is not None:
            payload += tx_data
        status, res = self.send_with_command(protocol.Command.CRACKER_I2C_TRANSCEIVE, payload=payload)
        if status != protocol.STATUS_OK:
            self._logger.error(f"Receive status code error [{status}]")
            return status, None
        else:
            return status, res

    def i2c_transmit(self, tx_data: bytes | str | int, is_trigger: bool = False) -> tuple[int, None]:
        """
        Send data over the I2C interface.

        When is_trigger=True, the Trigger signal is pulled low at the start of transmission and
        high upon completion::

            TRIG: ───┐            ┌─── HIGH
                     |            |
                     └────────────┘    LOW
                     ┌────────────┐
                     │   tx_data  │
                     └────────────┘

        When is_trigger=False, the Trigger signal remains unchanged::

            TRIG: ──────────────────── HIGH

                                       LOW
                     ┌────────────┐
                     │   tx_data  │
                     └────────────┘

        :param tx_data: Data to send. Accepts bytes, a hex string, or an integer (converted to
                        big-endian bytes using the minimum required length).
        :type tx_data: bytes | str | int
        :param is_trigger: Whether to generate a trigger signal during transmission
                           (pulled low at start, high at end).
        :type is_trigger: bool
        :return: Device response status and None: (status, None).
        :rtype: tuple[int, None]
        :raises TypeError: If tx_data is not bytes, str, or int.
        """
        if isinstance(tx_data, int):
            byte_length = max(1, (tx_data.bit_length() + 7) // 8)
            tx_data = tx_data.to_bytes(byte_length, byteorder="big")
        elif isinstance(tx_data, str):
            tx_data = bytes.fromhex(tx_data)
        elif not isinstance(tx_data, bytes):
            raise TypeError(f"tx_data must be bytes, str, or int, got {type(tx_data).__name__}")
        transfer_rw = (0, 0, 0, 0, 0, 0, 0, 0)
        transfer_lens = (len(tx_data), 0, 0, 0, 0, 0, 0, 0)
        status, _ = self._i2c_transceive(
            tx_data,
            combined_transfer_count_1=1,
            combined_transfer_count_2=0,
            transfer_rw=transfer_rw,
            transfer_lens=transfer_lens,
            is_delay=False,
            delay=0,
            is_trigger=is_trigger,
        )
        return status, None

    def i2c_receive(self, rx_count, is_trigger: bool = False) -> tuple[int, bytes | None]:
        """
        Receive data over the I2C interface.

        When ``is_trigger=True``, the Trigger signal is pulled low at the start of reception and
        high upon completion::

            TRIG: ───┐            ┌─── HIGH
                     |            |
                     └────────────┘    LOW
                     ┌────────────┐
                     │   rx_data  │
                     └────────────┘

        When ``is_trigger=False``, the Trigger signal remains unchanged::

            TRIG: ──────────────────── HIGH

                                       LOW
                     ┌────────────┐
                     │   rx_data  │
                     └────────────┘

        :param rx_count: Number of bytes to receive.
        :type rx_count: int
        :param is_trigger: Whether to generate a trigger signal during data reception
            (pulled low at start, high at end).
        :type is_trigger: bool
        :return: Device response status and received data: (status, response).
        :rtype: tuple[int, bytes | None]
        """
        transfer_rw = (1, 1, 1, 1, 1, 1, 1, 1)
        transfer_lens = (rx_count, 0, 0, 0, 0, 0, 0, 0)
        return self._i2c_transceive(
            tx_data=None,
            combined_transfer_count_1=1,
            combined_transfer_count_2=0,
            transfer_rw=transfer_rw,
            transfer_lens=transfer_lens,
            is_delay=False,
            delay=0,
            is_trigger=is_trigger,
        )

    def i2c_transmit_delay_receive(
        self, tx_data: bytes | str | int, delay: int, rx_count: int, is_trigger: bool = False
    ) -> tuple[int, bytes | None]:
        """
        Send data over I2C, wait for the specified delay, then receive data.

        When is_trigger=True, the Trigger signal is pulled low at the start of transmission and
        high upon completion::

            TRIG: ───┐            ┌────────────┐            ┌─── HIGH
                     |            |            |            |
                     └────────────┘            └────────────┘    LOW
                     ┌────────────┬────────────┬────────────┐
                     │  tx_data   │    delay   │   rx_data  │
                     └────────────┴────────────┴────────────┘

        When is_trigger=False, the Trigger signal remains unchanged::

            TRIG: ────────────────────────────────────────────── HIGH

                                                                 LOW
                     ┌────────────┬────────────┬────────────┐
                     │  tx_data   │    delay   │   rx_data  │
                     └────────────┴────────────┴────────────┘

        :param tx_data: Data to send. Accepts bytes, a hex string, or an integer (converted to
                        big-endian bytes using the minimum required length).
        :type tx_data: bytes | str | int
        :param delay: Delay between transmit and receive phases, in units of 10 nanoseconds.
        :type delay: int
        :param rx_count: Number of bytes to receive.
        :type rx_count: int
        :param is_trigger: Whether to generate a trigger signal during transmission
                           (pulled low at start, high at end).
        :type is_trigger: bool
        :return: Device response status and received data: (status, response).
        :rtype: tuple[int, bytes | None]
        :raises TypeError: If tx_data is not bytes, str, or int.
        """
        if isinstance(tx_data, int):
            byte_length = max(1, (tx_data.bit_length() + 7) // 8)
            tx_data = tx_data.to_bytes(byte_length, byteorder="big")
        elif isinstance(tx_data, str):
            tx_data = bytes.fromhex(tx_data)
        elif not isinstance(tx_data, bytes):
            raise TypeError(f"tx_data must be bytes, str, or int, got {type(tx_data).__name__}")
        transfer_rw = (1, 1, 1, 1, 0, 0, 0, 0)
        transfer_lens = (len(tx_data), 0, 0, 0, rx_count, 0, 0, 0)
        return self._i2c_transceive(
            tx_data,
            combined_transfer_count_1=1,
            combined_transfer_count_2=1,
            transfer_rw=transfer_rw,
            transfer_lens=transfer_lens,
            is_delay=True,
            delay=delay,
            is_trigger=is_trigger,
        )

    def i2c_transceive(
        self, tx_data: bytes | str | int, rx_count: int, is_trigger: bool = False
    ) -> tuple[int, bytes | None]:
        """
        Send and receive data over I2C without any inter-phase delay.

        When is_trigger=True, the Trigger signal is pulled low at the start of transmission and
        high upon completion::

            TRIG: ───┐                         ┌─── HIGH
                     |                         |
                     └─────────────────────────┘    LOW
                     ┌────────────┬────────────┐
                     │  tx_data   │   rx_data  │
                     └────────────┴────────────┘

        When is_trigger=False, the Trigger signal remains unchanged::

            TRIG: ──────────────────────────────── HIGH

                                                   LOW
                     ┌────────────┬────────────┐
                     │  tx_data   │   rx_data  │
                     └────────────┴────────────┘

        :param tx_data: Data to send. Accepts bytes, a hex string, or an integer (converted to
                        big-endian bytes using the minimum required length).
        :type tx_data: bytes | str | int
        :param rx_count: Number of bytes to receive.
        :type rx_count: int
        :param is_trigger: Whether to generate a trigger signal during transmission
                           (pulled low at start, high at end).
        :type is_trigger: bool
        :return: Device response status and received data: (status, response).
        :rtype: tuple[int, bytes | None]
        :raises TypeError: If tx_data is not bytes, str, or int.
        """
        if isinstance(tx_data, int):
            byte_length = max(1, (tx_data.bit_length() + 7) // 8)
            tx_data = tx_data.to_bytes(byte_length, byteorder="big")
        elif isinstance(tx_data, str):
            tx_data = bytes.fromhex(tx_data)
        elif not isinstance(tx_data, bytes):
            raise TypeError(f"tx_data must be bytes, str, or int, got {type(tx_data).__name__}")
        transfer_rw = (0, 0, 0, 0, 0, 0, 1, 0)
        transfer_lens = (len(tx_data), rx_count, 0, 0, 0, 0, 0, 0)
        return self._i2c_transceive(
            tx_data,
            combined_transfer_count_1=2,
            combined_transfer_count_2=0,
            transfer_rw=transfer_rw,
            transfer_lens=transfer_lens,
            is_delay=False,
            delay=0,
            is_trigger=is_trigger,
        )

    def uart_io_enable(self) -> tuple[int, None]:
        """
        Enable the UART communication interface. After enabling, the TX pin goes high and the RX
        pin is set to a tri-state input.

        :return: Device response status and received data: (status, response).
        :rtype: tuple[int, bytes | None]
        """
        return self._uart_io_enable(True)

    def uart_enable(self) -> tuple[int, None]:
        """
        Enable the UART interface.

        .. deprecated:: 0.19.0
            This function will be removed in a future version. Use ``uart_io_enable`` instead.

        :return: Device response status and received data: (status, response).
        :rtype: tuple[int, bytes | None]
        """
        warnings.warn(
            "uart_enable() 已弃用，将在未来版本中移除，请使用 uart_io_enable() 替代。",
            category=DeprecationWarning,
            stacklevel=2,
        )
        return self._uart_io_enable(True)

    def uart_io_disable(self) -> tuple[int, None]:
        """
        Disable the UART communication interface. After disabling, both TX and RX pins are set to
        a tri-state input.

        :return: Device response status and received data: (status, response).
        :rtype: tuple[int, bytes | None]
        """
        return self._uart_io_enable(False)

    def uart_disable(self) -> tuple[int, None]:
        """
        Disable the UART interface.

        .. deprecated:: 0.19.0
            This function will be removed in a future version. Use ``uart_io_disable`` instead.

        :return: Device response status and received data: (status, response).
        :rtype: tuple[int, bytes | None]
        """
        warnings.warn(
            "uart_disable() 已弃用，将在未来版本中移除，请使用 uart_io_disable() 替代。",
            category=DeprecationWarning,
            stacklevel=2,
        )
        return self._uart_io_enable(False)

    @connection_status_check
    def _uart_io_enable(self, enable: bool) -> tuple[int, None]:
        """
        Configure the UART communication interface enable state.

        When True, the UART interface is enabled: TX pin goes high and RX pin is set to tri-state.
        When False, the UART interface is disabled: both TX and RX pins are set to tri-state.

        :param enable: True to enable, False to disable.
        :type enable: bool
        :return: Device response status and received data: (status, response).
        :rtype: tuple[int, bytes | None]
        """
        payload = struct.pack(">?", enable)
        self._logger.debug(f"cracker_uart_enable payload: {payload.hex()}")
        status, res = self.send_with_command(protocol.Command.CRACKER_UART_ENABLE, payload=payload)
        if status == protocol.STATUS_OK:
            self._config.nut_uart_enable = enable
        return status, res

    @connection_status_check
    def uart_reset(self) -> tuple[int, None]:
        """
        Reset the UART hardware logic.

        :return: Device response status and received data: (status, response).
        :rtype: tuple[int, bytes | None]
        """
        payload = None
        self._logger.debug(f"cracker_uart_reset payload: {payload}")
        return self.send_with_command(protocol.Command.CRACKER_UART_RESET)

    @connection_status_check
    def uart_config(
        self,
        baudrate: serial.Baudrate | int | str | None = None,
        bytesize: serial.Bytesize | int | str | None = None,
        parity: serial.Parity | int | str | None = None,
        stopbits: serial.Stopbits | int | str | None = None,
    ) -> tuple[int, None]:
        """
        Configure the UART interface parameters.

        Accepts enum members from ``cracknuts.cracker.serial`` or direct numeric/string values
        (eliminating the need to import the enum module). Invalid values are rejected with
        an error and the function returns ``(self.NON_PROTOCOL_ERROR, None)``.

        :param baudrate: Baud rate. Can be a ``serial.Baudrate`` enum, int (9600, 19200,
            38400, 57600, 115200, 1000000), or string ("9600", "115200", etc.).
            Default: current config value.
        :type baudrate: serial.Baudrate | int | str | None
        :param bytesize: Data bit length. Can be a ``serial.Bytesize`` enum, int (8),
            or string ("8", "EIGHTBITS"). Default: current config value.
        :type bytesize: serial.Bytesize | int | str | None
        :param parity: Parity mode. Can be a ``serial.Parity`` enum, int (0=NONE, 1=EVEN,
            2=ODD), or string ("NONE", "EVEN", "ODD", "0", "1", "2").
            Default: current config value.
        :type parity: serial.Parity | int | str | None
        :param stopbits: Stop bits. Can be a ``serial.Stopbits`` enum, int (1=ONE, 2=TWO),
            or string ("1", "2", "ONE", "TWO"). Default: current config value.
        :type stopbits: serial.Stopbits | int | str | None
        :return: Device response status and None.
        :rtype: tuple[int, None]
        """

        if baudrate is None or bytesize is None or parity is None or stopbits is None:
            config = self.get_current_config()
            if config is None:
                self._logger.error("Get config from cracker error.")
                return self.NON_PROTOCOL_ERROR, None
            if baudrate is None:
                baudrate = config.nut_uart_baudrate
            if bytesize is None:
                bytesize = config.nut_uart_bytesize
            if parity is None:
                parity = config.nut_uart_parity
            if stopbits is None:
                stopbits = config.nut_uart_stopbits

        # Coerce parameters to enum types
        baud_map = {
            9600: serial.Baudrate.BAUDRATE_9600,
            19200: serial.Baudrate.BAUDRATE_19200,
            38400: serial.Baudrate.BAUDRATE_38400,
            57600: serial.Baudrate.BAUDRATE_57600,
            115200: serial.Baudrate.BAUDRATE_115200,
            1000000: serial.Baudrate.BAUDRATE_1000000,
            "9600": serial.Baudrate.BAUDRATE_9600,
            "19200": serial.Baudrate.BAUDRATE_19200,
            "38400": serial.Baudrate.BAUDRATE_38400,
            "57600": serial.Baudrate.BAUDRATE_57600,
            "115200": serial.Baudrate.BAUDRATE_115200,
            "1000000": serial.Baudrate.BAUDRATE_1000000,
        }
        bytesize_map = {
            8: serial.Bytesize.EIGHTBITS,
            "8": serial.Bytesize.EIGHTBITS,
            "EIGHTBITS": serial.Bytesize.EIGHTBITS,
        }
        parity_map = {
            0: serial.Parity.PARITY_NONE,
            1: serial.Parity.PARITY_EVEN,
            2: serial.Parity.PARITY_ODD,
            "0": serial.Parity.PARITY_NONE,
            "1": serial.Parity.PARITY_EVEN,
            "2": serial.Parity.PARITY_ODD,
            "NONE": serial.Parity.PARITY_NONE,
            "EVEN": serial.Parity.PARITY_EVEN,
            "ODD": serial.Parity.PARITY_ODD,
        }
        stopbits_map = {
            1: serial.Stopbits.STOPBITS_ONE,
            2: serial.Stopbits.STOPBITS_TWO,
            "1": serial.Stopbits.STOPBITS_ONE,
            "2": serial.Stopbits.STOPBITS_TWO,
            "ONE": serial.Stopbits.STOPBITS_ONE,
            "TWO": serial.Stopbits.STOPBITS_TWO,
        }

        try:
            if isinstance(baudrate, serial.Baudrate):
                pass
            elif isinstance(baudrate, int | str):
                if isinstance(baudrate, str):
                    baudrate = baudrate.strip()
                if baudrate not in baud_map:
                    self._logger.error(f"Invalid baudrate: {baudrate}. Allowed values: {list(baud_map.keys())}")
                    return self.NON_PROTOCOL_ERROR, None
                baudrate = baud_map[baudrate]
            else:
                self._logger.error(f"Invalid baudrate type: {type(baudrate)}")
                return self.NON_PROTOCOL_ERROR, None

            if isinstance(bytesize, serial.Bytesize):
                pass
            elif isinstance(bytesize, int | str):
                if isinstance(bytesize, str):
                    bytesize = bytesize.strip()
                if bytesize not in bytesize_map:
                    self._logger.error(f"Invalid bytesize: {bytesize}. Allowed values: {list(bytesize_map.keys())}")
                    return self.NON_PROTOCOL_ERROR, None
                bytesize = bytesize_map[bytesize]
            else:
                self._logger.error(f"Invalid bytesize type: {type(bytesize)}")
                return self.NON_PROTOCOL_ERROR, None

            if isinstance(parity, serial.Parity):
                pass
            elif isinstance(parity, int | str):
                if isinstance(parity, str):
                    parity = parity.strip().upper()
                if parity not in parity_map:
                    self._logger.error(f"Invalid parity: {parity}. Allowed values: {list(parity_map.keys())}")
                    return self.NON_PROTOCOL_ERROR, None
                parity = parity_map[parity]
            else:
                self._logger.error(f"Invalid parity type: {type(parity)}")
                return self.NON_PROTOCOL_ERROR, None

            if isinstance(stopbits, serial.Stopbits):
                pass
            elif isinstance(stopbits, int | str):
                if isinstance(stopbits, str):
                    stopbits = stopbits.strip().upper()
                if stopbits not in stopbits_map:
                    self._logger.error(f"Invalid stopbits: {stopbits}. Allowed values: {list(stopbits_map.keys())}")
                    return self.NON_PROTOCOL_ERROR, None
                stopbits = stopbits_map[stopbits]
            else:
                self._logger.error(f"Invalid stopbits type: {type(stopbits)}")
                return self.NON_PROTOCOL_ERROR, None
        except Exception as e:
            self._logger.error(f"Error coercing UART parameters: {e}")
            return self.NON_PROTOCOL_ERROR, None

        payload = struct.pack(">BBBB", stopbits.value, parity.value, bytesize.value, baudrate.value)
        self._logger.debug(f"cracker_uart_config payload: {payload.hex()}")
        return self.send_with_command(protocol.Command.CRACKER_UART_CONFIG, payload=payload)

    @connection_status_check
    def uart_transmit_receive(
        self, tx_data: str | bytes | int = None, rx_count: int = 0, timeout: int = 10000, is_trigger: bool = False
    ) -> tuple[int, bytes | None]:
        """
        Send data over the UART interface, wait for a timeout period, then receive data.

        When is_trigger=True, the Trigger signal is pulled low at the start of transmission and
        high upon completion::

            TRIG: ───┐            ┌────────────┐            ┌─── HIGH
                     |            |            |            |
                     └────────────┘            └────────────┘    LOW
                     ┌────────────┬────────────┬────────────┐
                     │  tx_data   │   process  │   rx_data  │
                     └────────────┴────────────┴────────────┘
                                  | <------ timeout ------> |

        When is_trigger=False, the Trigger signal remains unchanged::

            TRIG: ────────────────────────────────────────────── HIGH

                                                                 LOW
                     ┌────────────┬────────────┬────────────┐
                     │  tx_data   │   process  │   rx_data  │
                     └────────────┴────────────┴────────────┘
                                  | <------ timeout ------> |

        :param tx_data: Data to send. Accepts bytes, a hex string, an integer (converted to
                        big-endian bytes using the minimum required length), or None.
        :type tx_data: str | bytes | int | None
        :param rx_count: Number of bytes to receive.
        :type rx_count: int
        :param timeout: Receive timeout in milliseconds.
        :type timeout: int
        :param is_trigger: Whether to generate a trigger signal during transmission
                           (pulled low at start, high at end).
        :type is_trigger: bool
        :return: Device response status and received data: (status, response).
        :rtype: tuple[int, bytes | None]
        :raises TypeError: If tx_data is not bytes, str, int, or None.
        """
        if isinstance(tx_data, int):
            byte_length = max(1, (tx_data.bit_length() + 7) // 8)
            tx_data = tx_data.to_bytes(byte_length, byteorder="big")
        elif isinstance(tx_data, str):
            tx_data = bytes.fromhex(tx_data)
        elif tx_data is not None and not isinstance(tx_data, bytes):
            raise TypeError(f"tx_data must be bytes, str, int, or None, got {type(tx_data).__name__}")

        payload = struct.pack(">H?I", rx_count, is_trigger, timeout)
        if tx_data is not None:
            payload += tx_data
        self._logger.debug(f"cracker_uart_transmit_receive payload: {payload.hex()}")
        return self.send_with_command(protocol.Command.CRACKER_UART_TRANSCEIVE, payload=payload)

    def uart_transmit(self, tx_data: str | bytes | int, is_trigger: bool = False) -> tuple[int, None]:
        """
        Send data over the UART interface, optionally generating a trigger signal.

        When is_trigger=True, the Trigger signal is pulled low at the start of transmission and
        high upon completion::

            TRIG: ───┐            ┌─── HIGH
                     |            |
                     └────────────┘    LOW
                     ┌────────────┐
                     │  tx_data   │
                     └────────────┘

        When is_trigger=False, the Trigger signal remains unchanged::

            TRIG: ──────────────────── HIGH

                                       LOW
                     ┌────────────┐
                     │  tx_data   │
                     └────────────┘

        :param tx_data: Data to send. Accepts bytes, a hex string, or an integer (converted to
                        big-endian bytes using the minimum required length).
        :type tx_data: str | bytes | int
        :param is_trigger: Whether to generate a trigger signal during transmission
                           (pulled low at start, high at end).
        :type is_trigger: bool
        :return: Device response status and None: (status, None).
        :rtype: tuple[int, None]
        """
        return self.uart_transmit_receive(tx_data=tx_data, rx_count=0, timeout=0, is_trigger=is_trigger)

    def uart_receive(self, rx_count: int, timeout: int = 10000, is_trigger: bool = False) -> tuple[int, bytes | None]:
        """
        Receive data over the UART interface, optionally generating a trigger signal.

        When ``is_trigger=True``, the Trigger signal is pulled low at the start of reception and
        high upon completion::

            TRIG: ───┐            ┌─── HIGH
                     |            |
                     └────────────┘    LOW
                     ┌────────────┐
                     │   rx_data  │
                     └────────────┘

        When ``is_trigger=False``, the Trigger signal remains unchanged::

            TRIG: ──────────────────── HIGH

                                       LOW
                     ┌────────────┐
                     │   rx_data  │
                     └────────────┘

        :param rx_count: Number of bytes to receive.
        :type rx_count: int
        :param timeout: Receive timeout in milliseconds.
        :type timeout: int
        :param is_trigger: Whether to generate a trigger signal upon reception completion.
            True: Trigger signal goes high when reception completes.
            False: Trigger signal remains unchanged.
        :type is_trigger: bool
        :return: Device response status and received data: (status, response).
        :rtype: tuple[int, bytes | None]
        """
        return self.uart_transmit_receive(tx_data=None, rx_count=rx_count, timeout=timeout, is_trigger=is_trigger)

    @connection_status_check
    def uart_receive_fifo_remained(self) -> tuple[int, int]:
        """
        Read the number of unread bytes remaining in the UART receive FIFO.

        :return: Device response status and the remaining byte count: (status, count).
        :rtype: tuple[int, int]
        """
        payload = None
        self._logger.debug(f"cracker_uart_receive_fifo_remained payload: {payload}")
        status, res = self.send_with_command(protocol.Command.CRACKER_UART_RECEIVE_FIFO_REMAINED)
        return status, struct.unpack(">H", res)[0]

    @connection_status_check
    def uart_receive_fifo_dump(self) -> tuple[int, bytes | None]:
        """
        Read all remaining data from the UART receive FIFO.

        :return: Device response status and received data: (status, response).
        :rtype: tuple[int, bytes | None]
        """
        payload = None
        self._logger.debug(f"cracker_uart_receive_fifo_dump payload: {payload}")
        return self.send_with_command(protocol.Command.CRACKER_UART_CRACKER_UART_RECEIVE_FIFO_DUMP)

    @connection_status_check
    def uart_receive_fifo_clear(self) -> tuple[int, bytes | None]:
        """
        Clear all remaining data in the UART receive FIFO.

        :return: Device response status and received data: (status, response).
        :rtype: tuple[int, bytes | None]
        """
        payload = None
        self._logger.debug(f"cracker_uart_receive_fifo_dump payload: {payload}")
        return self.send_with_command(protocol.Command.CRACKER_UART_CRACKER_UART_RECEIVE_CLEAR)

    def nut_reset(self, polar: int = 0, time: int = 10):
        """
        Reset the RESET pin of the nut chip. The reset level polarity and duration are configurable.
        By default the RESET pin is in tri-state input mode; the board design must ensure the default
        state is non-reset (e.g. pulled high). After calling ``nut_reset()``, the RESET pin is driven
        to the configured polarity level for the specified duration.

        ::

            polar=LOW
            TRIG: ~~~ ┐            ┌ ~~~
                      └────────────┘     LOW
                      |<-  time  ->|

            polar=HIGH
            TRIG:    ┌────────────┐     HIGH
                 ~~~ ┘            └ ~~~
                     |<-  time  ->|

        :param polar: Polarity: 0 for low level, 1 for high level.
        :type polar: int
        :param time: Duration of the reset level (in milliseconds).
        :type time: int
        :return: Device response status and received data: (status, response).
        :rtype: tuple[int, bytes | None]
        """
        time = time * 1_000_00  # the uint is 10 ns
        payload = struct.pack(">BI", polar, time)
        self._logger.debug(f"cracker_nut_reset payload: {payload}")
        return self.send_with_command(protocol.Command.NUT_RESET, payload=payload)

    def nut_reset_io_enable(self, enable: bool):
        payload = struct.pack(">B", enable)
        self._logger.debug(f"cracker_nut_reset_io_enable payload: {payload}")
        return self.send_with_command(protocol.Command.NUT_RESET_IO_ENABLE, payload=payload)

    @staticmethod
    def _get_bit_stream_lsb(data: bytes, bit_index: int) -> int:
        value = int.from_bytes(data, byteorder="big")
        return (value >> bit_index) & 1

    def digital_read(self, pin_num: int):
        """
        Read the level state of a digital IO pin.

        :param pin_num: Pin number (zero-indexed); supports pins 5 and 6.
        :type pin_num: int
        :return: Device response status and pin level: (status, level).
        :rtype: tuple[int, bytes | None | int]
        """
        pin_num = pin_num - 5  # 从第五个引脚开始编号
        s, r = self.register_read(base_address=self._BASE_ADDRESS, offset=self._OFFSET_GPIO_DATA)
        if s != protocol.STATUS_OK:
            self._logger.error(f"Get GPIO data failed, status: {s}")
            return s, r
        else:
            return s, self._get_bit_stream_lsb(r, pin_num)

    def digital_write(self, pin_num: int, value: int):
        """
        Set the level state of a digital IO pin.

        :param pin_num: Pin number (zero-indexed); supports pins 5 and 6.
        :type pin_num: int
        :param value: Pin level state: 1 for high, 0 for low.
        :type value: int
        :return: Device response status and received data: (status, response).
        :rtype: tuple[int, bytes | None]
        """
        pin_num = pin_num - 5  # 从第五个引脚开始编号
        s, r = self.register_read(base_address=self._BASE_ADDRESS, offset=self._OFFSET_GPIO_DATA)
        if s != protocol.STATUS_OK:
            self._logger.error(f"Get old GPIO data failed, status: {s}")
            return s, r
        else:
            gpio_data = int.from_bytes(r, byteorder="big")
            if value:
                gpio_data |= 1 << pin_num
            else:
                gpio_data &= ~(1 << pin_num)
            gpio_data_bytes = gpio_data.to_bytes(len(r), byteorder="big")
            return self.register_write(
                base_address=self._BASE_ADDRESS, offset=self._OFFSET_GPIO_DATA, data=gpio_data_bytes
            )

    def digital_pin_mode(self, pin_num: int, mode: int | str):
        """
        Set the operating mode of a digital IO pin.

        :param pin_num: Pin number (zero-indexed); supports pins 5 and 6.
        :type pin_num: int
        :param mode: Pin operating mode: 1 for input, 0 for output, or ``"INPUT"`` / ``"OUTPUT"``.
        :type mode: int | str
        :return: Device response status and received data: (status, response).
        :rtype: tuple[int, bytes | None]
        """
        if isinstance(mode, str):
            if mode.upper() == "INPUT":
                mode = 1
            elif mode.upper() == "OUTPUT":
                mode = 0
            else:
                raise ValueError("Invalid mode string, must be 'INPUT' or 'OUTPUT'")
        pin_num = pin_num - 5  # 从第五个引脚开始编号
        s, r = self.register_read(base_address=self._BASE_ADDRESS, offset=self._OFFSET_GPIO_DIR)
        if s != protocol.STATUS_OK:
            self._logger.error(f"Get old GPIO dir failed, status: {s}")
            return s, r
        else:
            gpio_dir = int.from_bytes(r, byteorder="big")
            if mode:
                gpio_dir |= 1 << pin_num
            else:
                gpio_dir &= ~(1 << pin_num)
            gpio_dir_bytes = gpio_dir.to_bytes(len(r), byteorder="big")
            return self.register_write(
                base_address=self._BASE_ADDRESS, offset=self._OFFSET_GPIO_DIR, data=gpio_dir_bytes
            )
