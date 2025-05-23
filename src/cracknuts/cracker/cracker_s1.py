# Copyright 2024 CrackNuts. All rights reserved.

import re
import struct
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
        bytes_format = {
            "nut_enable": "?",
            "nut_voltage": "I",
            "nut_clock_enable": "?",
            "nut_clock": "I",
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
        }

        config = ConfigS1()

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
            if not hasattr(config, k):
                self._logger.warning(f"Parse config bytes error: {k} is not a valid config key.")
            else:
                default_value = getattr(config, k)
                if k == "nut_voltage":
                    v = v / 1000
                elif k == "nut_spi_speed":
                    v = round(100e6 / 2 / v, 2)
                elif default_value is not None and isinstance(default_value, Enum):
                    v = default_value.__class__(v)

                setattr(config, k, v)

        return config

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
        self._uart_enable(config.nut_uart_enable)

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

        :param source: Trigger source: It can be one of ('N', 'A', 'B', 'P') or ('Nut'、'ChA'、'ChB'、'Protocol')
                       or a number in 0, 1, 2, 3, represent Nut, Channel A, Channel B, and Protocol, respectively.
        :type source: int | str
        :return: The device response status
        :rtype: tuple[int, None]
        """
        sources1 = ("N", "A", "B", "P")
        sources2 = ("NUT", "CHA", "CHB", "PROTOCOL")
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
            if source > 3:
                self._logger.error("Invalid trigger source, it must be one of (0, 1, 2, 3)")
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
            elif clock == "48M":
                clock = 48000
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
                    self._logger.error("UnSupport osc sample rate, it should in 65M or 48M or 24M or 12M or 8M")
                    return self.NON_PROTOCOL_ERROR, None
        if clock not in (65000, 48000, 24000, 12000, 8000, 4000):
            self._logger.error("UnSupport osc sample clock, it should in (65000, 48000, 24000, 12000, 8000)")
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
    def nut_clock_freq(self, clock: int | str) -> tuple[int, None]:
        """
        Set nut clock.

        :param clock: The clock of the nut in kHz
        :type clock: int | str
        :return: The device response status
        :rtype: tuple[int, None]
        """
        if isinstance(clock, str):
            clock = clock.upper()
            if clock == "24M":
                clock = 24000
            elif clock == "12M":
                clock = 12000
            elif clock == "8M":
                clock = 8000
            elif clock == "4M":
                clock = 4000
            else:
                self._logger.error(f"Unknown clock type: {clock}, 24M or 12M or 8M or 4M")
                return protocol.STATUS_ERROR, None

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
        Enable the SPI

        :return: The device response status
        :rtype: tuple[int, None]
        """
        return self._spi_enable(True)

    def spi_disable(self) -> tuple[int, None]:
        """
        Disable the SPI

        :return: The device response status
        :rtype: tuple[int, None]
        """
        return self._spi_enable(False)

    @connection_status_check
    def _spi_enable(self, enable: bool):
        """
        Enable the SPI.

        :param enable: True for enable, False for disable.
        :type enable: bool
        :return: The device response status.
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

        :return: The device response status.
        :rtype: tuple[int, None]
        """
        payload = None
        self._logger.debug(f"cracker_spi_reset payload: {payload}")
        return self.send_with_command(protocol.Command.CRACKER_SPI_RESET)

    @connection_status_check
    def spi_config(
        self,
        speed: float | None = None,
        cpol: serial.SpiCpol | None = None,
        cpha: serial.SpiCpha | None = None,
        csn_auto: bool | None = None,
        csn_delay: bool | None = None,
    ) -> tuple[int, None | str]:
        """
        Config the SPI.

        :param speed: SPI speed.
        :type speed: int
        :param cpol: Clock polarity.
        :type cpol: serial.SpiCpol
        :param cpha: Clock phase.
        :type cpha: serial.SpiCpha
        :param csn_auto: In delay mode, does the chip select signal remain low throughout the delay phase?
                         Deselecting this option means that during the DELAY, the CS (Chip Select) signal is
                         normally pulled high.
                         Selecting this option indicates that during the DELAY, the CS signal is fixed at low.
        :type csn_auto: bool,
        :param csn_delay: In delay mode, does the chip select signal remain low throughout the delay phase?
                        True: CS stays low. False: CS behaves normally and goes high.
        :return: The device response status.
        :rtype: tuple[int, None]
        """

        if speed is None or cpol is None or csn_auto is None:
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
    def _spi_transceive(
        self, tx_data: bytes | str | None, is_delay: bool, delay: int, rx_count: int, is_trigger: bool
    ) -> tuple[int, bytes | None]:
        """
        Basic interface for sending and receiving data through the SPI protocol.

        :param tx_data: The data to send.
        :param is_delay: Whether the transmit delay is enabled.
        :type is_delay: bool
        :param delay: The transmit delay in milliseconds, with a minimum effective duration of 10 nanoseconds.
        :type delay: int
        :param rx_count: The number of received data bytes.
        :type rx_count: int
        :param is_trigger: Whether the transmit trigger is enabled.
        :type is_trigger: bool
        :return: The device response status and the data received from the SPI device.
                 Return None if an exception is caught.
        :rtype: tuple[int, bytes | None]
        """
        if isinstance(tx_data, str):
            tx_data = bytes.fromhex(tx_data)
        payload = struct.pack(">?IH?", is_delay, delay, rx_count, is_trigger)
        if tx_data is not None:
            payload += tx_data
        self._logger.debug(f"_spi_transceive payload: {payload.hex()}")
        status, res = self.send_with_command(protocol.Command.CRACKER_SPI_TRANSCEIVE, payload=payload)
        if status != protocol.STATUS_OK:
            self._logger.error(f"Receive status code error [{status}]")
            return status, None
        else:
            return status, res

    def spi_transmit(self, tx_data: bytes | str, is_trigger: bool = False) -> tuple[int, None]:
        """
        Send data through the SPI protocol.

        :param tx_data: The data to send.
        :type tx_data: str | bytes
        :param is_trigger: Whether the transmit trigger is enabled.
        :type is_trigger: bool
        :return: The device response status and the data received from the SPI device.
        :rtype: tuple[int, None]
        """
        status, _ = self._spi_transceive(
            tx_data, is_delay=False, delay=1_000_000_000, rx_count=0, is_trigger=is_trigger
        )
        return status, None

    def spi_receive(self, rx_count: int, is_trigger: bool = False) -> tuple[int, bytes | None]:
        """
        Receive data through the SPI protocol.

        :param rx_count: The number of received data bytes.
        :type rx_count: int
        :param is_trigger: Whether the transmit trigger is enabled.
        :type is_trigger: bool
        :return: The device response status and the data received from the SPI device.
                 Return None if an exception is caught.
        :rtype: tuple[int, bytes | None]
        """
        return self._spi_transceive(None, is_delay=False, delay=1_000_000_000, rx_count=rx_count, is_trigger=is_trigger)

    def spi_transmit_delay_receive(
        self, tx_data: bytes | str, delay: int, rx_count: int, is_trigger: bool = False
    ) -> tuple[int, bytes | None]:
        """
        Send and receive data with delay through the SPI protocol.

        :param tx_data: The data to send.
        :type tx_data: str | bytes
        :param delay: The transmit delay in milliseconds, with a minimum effective duration of 10 nanoseconds.
        :type delay: int
        :param rx_count: The number of received data bytes.
        :type rx_count: int
        :param is_trigger: Whether the transmit trigger is enabled.
        :type is_trigger: bool
        :return: The device response status and the data received from the SPI device.
                 Return None if an exception is caught.
        :rtype: tuple[int, bytes | None]
        """
        return self._spi_transceive(tx_data, is_delay=True, delay=delay, rx_count=rx_count, is_trigger=is_trigger)

    def spi_transceive(self, tx_data: bytes | str, rx_count: int, is_trigger: bool = False) -> tuple[int, bytes | None]:
        """
        Send and receive data without delay through the SPI protocol.

        :param tx_data: The data to send.
        :type tx_data: str | bytes
        :param rx_count: The number of received data bytes.
        :type rx_count: int
        :param is_trigger: Whether the transmit trigger is enabled.
        :type is_trigger: bool
        :return: The device response status and the data received from the SPI device.
                 Return None if an exception is caught.
        :rtype: tuple[int, bytes | None]
        """
        return self._spi_transceive(tx_data, is_delay=False, delay=0, rx_count=rx_count, is_trigger=is_trigger)

    def i2c_enable(self) -> tuple[int, None]:
        """
        Enable the I2C

        :return: The device response status
        :rtype: tuple[int, None]
        """
        return self._i2c_enable(True)

    def i2c_disable(self) -> tuple[int, None]:
        """
        Disable the I2C

        :return: The device response status
        :rtype: tuple[int, None]
        """
        return self._i2c_enable(False)

    @connection_status_check
    def _i2c_enable(self, enable: bool):
        """
        Enable the I2C.

        :param enable: True for enable, False for disable.
        :type enable: bool
        :return: The device response status.
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
        Reset the I2C.

        :return: The device response status.
        :rtype: tuple[int, None]
        """
        payload = None
        self._logger.debug(f"cracker_i2c_reset payload: {payload}")
        return self.send_with_command(protocol.Command.CRACKER_I2C_RESET)

    @connection_status_check
    def i2c_config(
        self,
        dev_addr: int | None = None,
        speed: serial.I2cSpeed | None = None,
    ) -> tuple[int, None]:
        """
        Config the SPI.

        :param dev_addr: The address of the device.
        :type dev_addr: int
        :param speed: The speed of the device.
        :type speed: serial.I2cSpeed
        :return: The device response status.
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

        payload = struct.pack(">BB", dev_addr, speed.value)
        self._logger.debug(f"cracker_i2c_config payload: {payload.hex()}")
        status, res = self.send_with_command(protocol.Command.CRACKER_I2C_CONFIG, payload=payload)
        if status == protocol.STATUS_OK:
            self._config.nut_i2c_dev_addr = dev_addr
            self._config.nut_i2c_speed = speed
        return status, res

    @connection_status_check
    def _i2c_transceive(
        self,
        tx_data: bytes | str | None,
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

        :param tx_data: The data to be sent.
        :type tx_data: bytes | str | None
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
        """
        if isinstance(tx_data, str):
            tx_data = bytes.fromhex(tx_data)

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

    def i2c_transmit(self, tx_data: bytes | str, is_trigger: bool = False) -> tuple[int, None]:
        """
        Send data through the I2C protocol.

        :param tx_data: The data to be sent.
        :type tx_data: str | bytes
        :param is_trigger: Whether the transmit trigger is enabled.
        """
        if isinstance(tx_data, str):
            tx_data = bytes.fromhex(tx_data)
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
        Receive data through the I2C protocol.

        :param rx_count: The number of received data bytes.
        :type rx_count: int
        :param is_trigger: Whether the transmit trigger is enabled.
        :return: The device response status and the data received from the I2C device.
                 Return None if an exception is caught.
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
        self, tx_data: bytes | str, delay: int, rx_count: int, is_trigger: bool = False
    ) -> tuple[int, bytes | None]:
        """
        Send and receive data with delay through the I2C protocol.

        :param tx_data: The data to be sent.
        :type tx_data: str | bytes
        :param delay: Transmit delay duration, in nanoseconds, with a minimum effective duration of 10 nanoseconds.
        :type delay: int
        :param rx_count: The number of received data bytes.
        :type rx_count: int
        :param is_trigger: Whether the transmit trigger is enabled.
        :type is_trigger: bool
        :return: The device response status and the data received from the I2C device.
                 Return None if an exception is caught.
        :rtype: tuple[int, bytes | None]
        """
        if isinstance(tx_data, str):
            tx_data = bytes.fromhex(tx_data)
        transfer_rw = (0, 0, 0, 0, 1, 1, 1, 1)
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

    def i2c_transceive(self, tx_data, rx_count, is_trigger: bool = False) -> tuple[int, bytes | None]:
        """
        Send and receive data without delay through the I2C protocol.

        :param tx_data: The data to be sent.
        :type tx_data: str | bytes
        :param rx_count: The number of received data bytes.
        :type rx_count: int
        :param is_trigger: Whether the transmit trigger is enabled.
        :type is_trigger: bool
        :return: The device response status and the data received from the I2C device.
                 Return None if an exception is caught.
        :rtype: tuple[int, bytes | None]
        """
        if isinstance(tx_data, str):
            tx_data = bytes.fromhex(tx_data)
        transfer_rw = (0, 0, 0, 0, 1, 1, 1, 1)
        transfer_lens = (len(tx_data), 0, 0, 0, rx_count, 0, 0, 0)
        return self._i2c_transceive(
            tx_data,
            combined_transfer_count_1=1,
            combined_transfer_count_2=1,
            transfer_rw=transfer_rw,
            transfer_lens=transfer_lens,
            is_delay=False,
            delay=0,
            is_trigger=is_trigger,
        )

    def uart_enable(self) -> tuple[int, None]:
        """
        Enable the UART.

        :return: The device response status
        :rtype: tuple[int, None]
        """
        return self._uart_enable(True)

    def uart_disable(self) -> tuple[int, None]:
        """
        Disable the UART.

        :return: The device response status
        :rtype: tuple[int, None]
        """
        return self._uart_enable(False)

    @connection_status_check
    def _uart_enable(self, enable: bool) -> tuple[int, None]:
        """
        Enable the uart.

        :param enable: True for enable, False for disable.
        :type enable: bool
        :return: The device response status.
        :rtype: tuple[int, None]
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
        Reset the UART hardware.

        :return: The device response status.
        :rtype: tuple[int, None]
        """
        payload = None
        self._logger.debug(f"cracker_uart_reset payload: {payload}")
        return self.send_with_command(protocol.Command.CRACKER_UART_RESET)

    @connection_status_check
    def uart_config(
        self,
        baudrate: serial.Baudrate | None = None,
        bytesize: serial.Bytesize | None = None,
        parity: serial.Parity | None = None,
        stopbits: serial.Stopbits | None = None,
    ) -> tuple[int, None]:
        """
        Config uart.

        :param baudrate: The baudrate of the uart.
        :type baudrate: serial.Baudrate
        :param bytesize: The bytesize of the uart.
        :type bytesize: serial.Bytesize
        :param parity: The parity of the uart.
        :type parity: serial.Parity
        :param stopbits: The stopbits of the uart.
        :type stopbits: serial.Stopbits
        :return: The device response status.
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

        payload = struct.pack(">BBBB", stopbits.value, parity.value, bytesize.value, baudrate.value)
        self._logger.debug(f"cracker_uart_config payload: {payload.hex()}")
        return self.send_with_command(protocol.Command.CRACKER_UART_CONFIG, payload=payload)

    @connection_status_check
    def uart_transmit_receive(
        self, tx_data: str | bytes = None, rx_count: int = 0, is_trigger: bool = False, timeout: int = 10000
    ) -> tuple[int, bytes | None]:
        """
        Transmit and receive data through the UART protocol.

        :param tx_data: The data to be sent.
        :type tx_data: str | bytes
        :param rx_count: The number of received data bytes.
        :type rx_count: int
        :param is_trigger: Whether the transmit trigger is enabled.
        :type is_trigger: bool
        :param timeout: Timeout in milliseconds.
        :type timeout: int
        :return: The device response status and the data received from the device.
        :rtype: tuple[int, bytes | None]
        """
        if isinstance(tx_data, str):
            tx_data = bytes.fromhex(tx_data)

        payload = struct.pack(">H?I", rx_count, is_trigger, timeout)
        if tx_data is not None:
            payload += tx_data
        self._logger.debug(f"cracker_uart_transmit_receive payload: {payload.hex()}")
        return self.send_with_command(protocol.Command.CRACKER_UART_TRANSCEIVE, payload=payload)

    @connection_status_check
    def uart_receive_fifo_remained(self) -> tuple[int, int]:
        """
        Get the number of remaining unread bytes in the UART receive FIFO.

        :return: The device response status and the number of remaining unread bytes.
        :rtype: tuple[int, int]
        """
        payload = None
        self._logger.debug(f"cracker_uart_receive_fifo_remained payload: {payload}")
        status, res = self.send_with_command(protocol.Command.CRACKER_UART_RECEIVE_FIFO_REMAINED)
        return status, struct.unpack(">H", res)[0]

    @connection_status_check
    def uart_receive_fifo_dump(self) -> tuple[int, bytes | None]:
        """
        Read all the remaining data from the UART receive FIFO.

        :return: The device response status and all the remaining unread bytes.
        :rtype: tuple[int, bytes | None]
        """
        payload = None
        self._logger.debug(f"cracker_uart_receive_fifo_dump payload: {payload}")
        return self.send_with_command(protocol.Command.CRACKER_UART_CRACKER_UART_RECEIVE_FIFO_DUMP)

    @connection_status_check
    def uart_receive_fifo_clear(self) -> tuple[int, bytes | None]:
        """
        Clear all the remaining data in the UART receive FIFO.

        :return: The device response status and all the remaining unread bytes.
        :rtype: tuple[int, bytes | None]
        """
        payload = None
        self._logger.debug(f"cracker_uart_receive_fifo_dump payload: {payload}")
        return self.send_with_command(protocol.Command.CRACKER_UART_CRACKER_UART_RECEIVE_CLEAR)
