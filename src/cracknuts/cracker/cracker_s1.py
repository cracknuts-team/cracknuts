# Copyright 2024 CrackNuts. All rights reserved.

import struct

from cracknuts.cracker import protocol, serial
from cracknuts.cracker.cracker_basic import ConfigBasic, CrackerBasic


class ConfigS1(ConfigBasic):
    def __init__(self):
        super().__init__()

        self.nut_enable = False
        self.nut_voltage = 3500
        self.nut_clock = 65000
        self.nut_voltage_raw: int | None = None
        self.nut_interface: int | None = None
        self.nut_timeout: int | None = None

        self.cracker_uart_enable: bool | None = False
        self.cracker_uart_config: dict | None = {}

        self.cracker_spi_enable: bool | None = False
        self.cracker_spi_config: dict | None = {}

        self.cracker_i2c_enable: bool | None = False
        self.cracker_i2c_config: dict | None = {}


class CrackerS1(CrackerBasic[ConfigS1]):
    def get_default_config(self) -> ConfigS1:
        return ConfigS1()

    def sync_config_to_cracker(self):
        config = self.get_current_config()
        self.nut_set_enable(config.nut_enable)
        self.nut_set_voltage(config.nut_voltage)
        self.nut_set_clock(config.nut_clock)
        for k, v in config.osc_analog_channel_enable.items():
            self.osc_set_analog_channel_enable(k, v)
            self.osc_set_analog_gain(k, config.osc_analog_gain.get(k, False))
        self.osc_set_sample_len(config.osc_sample_len)
        self.osc_set_sample_delay(config.osc_sample_delay)
        self.osc_set_sample_rate(config.osc_sample_rate)
        self.osc_set_sample_phase(config.osc_sample_phase)
        self.osc_set_analog_trigger_source(config.osc_analog_trigger_source)
        self.osc_set_trigger_mode(config.osc_trigger_mode)
        self.osc_set_trigger_edge(config.osc_analog_trigger_edge)
        self.osc_set_trigger_edge_level(config.osc_analog_trigger_edge_level)

    def cracker_read_register(self, base_address: int, offset: int) -> tuple[int, bytes | None]:
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
        self._logger.debug(f"cracker_read_register payload: {payload.hex()}")
        status, res = self.send_with_command(protocol.Command.CRACKER_READ_REGISTER, payload=payload)
        if status != protocol.STATUS_OK:
            return status, None
        else:
            return status, res

    def cracker_write_register(self, base_address: int, offset: int, data: bytes | int | str) -> tuple[int, None]:
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
        self._logger.debug(f"cracker_write_register payload: {payload.hex()}")
        status, _ = self.send_with_command(protocol.Command.CRACKER_WRITE_REGISTER, payload=payload)
        return status, None

    def osc_set_analog_channel_enable(self, channel: int, enable: bool) -> tuple[int, None]:
        """
        Set analog channel enable.

        :param channel: Channel to enable.
        :type channel: int
        :param enable: Enable or disable.
        :type enable: bool
        :return: The device response status
        :rtype: tuple[int, None]
        """
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
        status, res = self.send_with_command(protocol.Command.OSC_ANALOG_CHANNEL_ENABLE, payload=payload)
        if status == protocol.STATUS_OK:
            self._config.osc_analog_channel_enable = final_enable
        return status, None

    def osc_set_analog_coupling(self, channel: int, coupling: int) -> tuple[int, None]:
        """
        Set analog coupling.

        :param channel: Channel to enable.
        :type channel: int
        :param coupling: 1 for DC and 0 for AC.
        :type coupling: int
        :return: The device response status
        :rtype: tuple[int, None]
        """
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

        status, res = self.send_with_command(protocol.Command.OSC_ANALOG_COUPLING, payload=payload)
        if status == protocol.STATUS_OK:
            self._config.osc_analog_coupling = final_coupling

        return status, None

    def osc_set_analog_voltage(self, channel: int, voltage: int) -> tuple[int, None]:
        """
        Set analog voltage.

        :param channel: Channel to enable.
        :type channel: int
        :param voltage: Voltage to set. unit: mV.
        :type voltage: int
        :return: The device response status
        :rtype: tuple[int, None]
        """
        payload = struct.pack(">BI", channel, voltage)
        self._logger.debug(f"scrat_analog_coupling payload: {payload.hex()}")
        status, res = self.send_with_command(protocol.Command.OSC_ANALOG_VOLTAGE, payload=payload)
        if status == protocol.STATUS_OK:
            self._config.osc_analog_voltage[channel] = voltage

        return status, None

    def osc_set_analog_bias_voltage(self, channel: int, voltage: int) -> tuple[int, None]:
        """
        Set analog bias voltage.

        :param channel: Channel to enable.
        :type channel: int
        :param voltage: Voltage to set. unit: mV.
        :type voltage: int
        :return: The device response status
        :rtype: tuple[int, None]
        """
        payload = struct.pack(">BI", channel, voltage)
        self._logger.debug(f"scrat_analog_bias_voltage payload: {payload.hex()}")
        status, res = self.send_with_command(protocol.Command.OSC_ANALOG_BIAS_VOLTAGE, payload=payload)
        if status == protocol.STATUS_OK:
            self._config.osc_analog_bias_voltage[channel] = voltage

        return status, None

    def osc_set_digital_channel_enable(self, channel: int, enable: bool) -> tuple[int, None]:
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
        status, res = self.send_with_command(protocol.Command.OSC_DIGITAL_CHANNEL_ENABLE, payload=payload)
        if status == protocol.STATUS_OK:
            self._config.osc_digital_channel_enable = final_enable

        return status, None

    def osc_set_digital_voltage(self, voltage: int) -> tuple[int, None]:
        payload = struct.pack(">I", voltage)
        self._logger.debug(f"scrat_digital_voltage payload: {payload.hex()}")
        status, res = self.send_with_command(protocol.Command.OSC_DIGITAL_VOLTAGE, payload=payload)
        if status == protocol.STATUS_OK:
            self._config.osc_digital_voltage = voltage

        return status, None

    def osc_set_trigger_mode(self, mode: int) -> tuple[int, None]:
        """
        Set trigger mode.

        :param mode: Trigger mode. Trigger mode: 0 for edge, 1 for wave.
        :type mode: int
        :return: The device response status
        :rtype: tuple[int, None]
        """
        payload = struct.pack(">B", mode)
        self._logger.debug(f"osc_set_trigger_mode payload: {payload.hex()}")
        status, res = self.send_with_command(protocol.Command.OSC_TRIGGER_MODE, payload=payload)
        if status == protocol.STATUS_OK:
            self._config.osc_trigger_mode = mode

        return status, None

    def osc_set_analog_trigger_source(self, source: int | str) -> tuple[int, None]:
        """
        Set trigger source.

        :param source: Trigger source: 'N', 'A', 'B', 'P', or 0, 1, 2, 3
                       represent Nut, Channel A, Channel B, and Protocol, respectively.
        :type source: int | str
        :return: The device response status
        :rtype: tuple[int, None]
        """
        if isinstance(source, str):
            if source == "N":
                source = 0
            elif source == "A":
                source = 1
            elif source == "B":
                source = 2
            elif source == "P":
                source = 3
            else:
                self._logger.error(
                    f"Invalid trigger source: {source}. " f"  It must be one of (N, A, B, P) if specified as a string."
                )
        payload = struct.pack(">B", source)
        self._logger.debug(f"scrat_analog_trigger_source payload: {payload.hex()}")
        status, res = self.send_with_command(protocol.Command.OSC_ANALOG_TRIGGER_SOURCE, payload=payload)
        if status == protocol.STATUS_OK:
            self._config.osc_analog_trigger_source = source

        return status, None

    def osc_set_digital_trigger_source(self, channel: int) -> tuple[int, None]:
        payload = struct.pack(">B", channel)
        self._logger.debug(f"scrat_digital_trigger_source payload: {payload.hex()}")
        status, res = self.send_with_command(protocol.Command.OSC_DIGITAL_TRIGGER_SOURCE, payload=payload)
        if status == protocol.STATUS_OK:
            self._config.osc_digital_trigger_source = channel

        return status, None

    def osc_set_trigger_edge(self, edge: int | str) -> tuple[int, None]:
        """
        Set trigger edge.

        :param edge: Trigger edge. 'up', 'down', 'either' or 0, 1, 2 represent up, down, either, respectively.
        :type edge: int
        :return: The device response status
        :rtype: tuple[int, None]
        """
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
        status, res = self.send_with_command(protocol.Command.OSC_TRIGGER_EDGE, payload=payload)
        if status == protocol.STATUS_OK:
            self._config.osc_analog_trigger_edge = edge

        return status, None

    def osc_set_trigger_edge_level(self, edge_level: int) -> tuple[int, None]:
        """
        Set trigger edge level.

        :param edge_level: Edge level.
        :type edge_level: int
        :return: The device response status
        :rtype: tuple[int, None]
        """
        payload = struct.pack(">H", edge_level)
        self._logger.debug(f"scrat_analog_trigger_edge_level payload: {payload.hex()}")
        status, res = self.send_with_command(protocol.Command.OSC_TRIGGER_EDGE_LEVEL, payload=payload)
        if status == protocol.STATUS_OK:
            self._config.osc_analog_trigger_edge_level = edge_level

        return status, None

    def osc_set_analog_trigger_voltage(self, voltage: int) -> tuple[int, None]:
        """
        Set analog trigger voltage.

        :param voltage: Analog trigger voltage.
        :type voltage: int
        :return: The device response status
        :rtype: tuple[int, None]
        """
        payload = struct.pack(">I", voltage)
        self._logger.debug(f"scrat_analog_trigger_voltage payload: {payload.hex()}")
        status, res = self.send_with_command(protocol.Command.OSC_ANALOG_TRIGGER_VOLTAGE, payload=payload)
        if status == protocol.STATUS_OK:
            self._config.osc_analog_trigger_voltage = voltage

        return status, None

    def osc_set_sample_delay(self, delay: int) -> tuple[int, None]:
        """
        Set sample delay.

        :param delay: Sample delay.
        :type delay: int
        :return: The device response status
        :rtype: tuple[int, None]
        """
        payload = struct.pack(">i", delay)
        self._logger.debug(f"osc_sample_delay payload: {payload.hex()}")
        status, res = self.send_with_command(protocol.Command.OSC_SAMPLE_DELAY, payload=payload)
        if status == protocol.STATUS_OK:
            self._config.osc_sample_delay = delay

        return status, None

    def osc_set_sample_len(self, length: int) -> tuple[int, None]:
        """
        Set sample length.

        :param length: Sample length.
        :type length: int
        :return: The device response status
        :rtype: tuple[int, None]
        """
        payload = struct.pack(">I", length)
        self._logger.debug(f"osc_set_sample_len payload: {payload.hex()}")
        status, res = self.send_with_command(protocol.Command.OSC_SAMPLE_LENGTH, payload=payload)
        if status == protocol.STATUS_OK:
            self._config.osc_sample_len = length

        return status, None

    def osc_set_sample_rate(self, rate: int) -> tuple[int, None]:
        """
        Set osc sample rate

        :param rate: The sample rate in kHz, one of (65000, 48000, 24000, 12000, 8000, 4000)
        :type rate: int
        :return: The device response status
        :rtype: tuple[int, None]
        """
        payload = struct.pack(">I", rate)
        self._logger.debug(f"osc_set_sample_rate payload: {payload.hex()}")
        status, res = self.send_with_command(protocol.Command.OSC_SAMPLE_RATE, payload=payload)
        if status == protocol.STATUS_OK:
            self._config.osc_sample_rate = rate

        return status, None

    def osc_set_analog_gain(self, channel: int, gain: int) -> tuple[int, None]:
        """
        Set analog gain.

        :param channel: Analog channel.
        :type channel: int
        :param gain: Analog gain.
        :type gain: int
        :return: The device response status
        :rtype: tuple[int, None]
        """
        payload = struct.pack(">BB", channel, gain)
        self._logger.debug(f"scrat_analog_gain payload: {payload.hex()}")
        status, res = self.send_with_command(protocol.Command.OSC_ANALOG_GAIN, payload=payload)
        if status == protocol.STATUS_OK:
            self._config.osc_analog_gain[channel] = gain

        return status, None

    def osc_set_analog_gain_raw(self, channel: int, gain: int) -> tuple[int, None]:
        """
        Set analog gain.

        :param channel: Analog channel.
        :type channel: int
        :param gain: Analog gain.
        :type gain: int
        :return: The device response status
        :rtype: tuple[int, None]
        """
        payload = struct.pack(">BB", channel, gain)
        self._logger.debug(f"scrat_analog_gain payload: {payload.hex()}")
        status, res = self.send_with_command(protocol.Command.OSC_ANALOG_GAIN_RAW, payload=payload)
        if status == protocol.STATUS_OK:
            self._config.osc_analog_gain_raw[channel] = gain

        return status, None

    def osc_set_clock_base_freq_mul_div(self, mult_int: int, mult_fra: int, div: int) -> tuple[int, None]:
        """
        Set clock base frequency.

        :param mult_int: Mult integration factor.
        :type mult_int: int
        :param mult_fra: Mult frequency in Hz.
        :type mult_fra: int
        :param div: Division factor.
        :type div: int
        :return: The device response status
        :rtype: tuple[int, None]
        """
        payload = struct.pack(">BHB", mult_int, mult_fra, div)
        self._logger.debug(f"osc_set_clock_base_freq_mul_div payload: {payload.hex()}")
        status, res = self.send_with_command(protocol.Command.OSC_CLOCK_BASE_FREQ_MUL_DIV, payload=payload)
        if status == protocol.STATUS_OK:
            self._config.osc_clock_base_freq_mul_div = mult_int, mult_fra, div

        return status, None

    def osc_set_sample_divisor(self, div_int: int, div_frac: int) -> tuple[int, None]:
        """
        Set sample divisor.

        :param div_int: Division factor.
        :type div_int: int
        :param div_frac: Division factor.
        :type div_frac: int
        :return: The device response status
        :rtype: tuple[int, None]
        """
        payload = struct.pack(">BH", div_int, div_frac)
        self._logger.debug(f"osc_set_sample_divisor payload: {payload.hex()}")
        status, res = self.send_with_command(protocol.Command.OSC_CLOCK_SAMPLE_DIVISOR, payload=payload)
        if status == protocol.STATUS_OK:
            self._config.osc_clock_sample_divisor = div_int, div_frac

        return status, None

    def osc_set_clock_update(self) -> tuple[int, None]:
        """
        Set clock params update.

        :return: The device response status
        :rtype: tuple[int, None]
        """
        self._logger.debug(f"osc_set_clock_update payload: {None}")
        return self.send_with_command(protocol.Command.OSC_CLOCK_UPDATE, payload=None)

    def osc_set_clock_simple(self, nut_clk: int, mult: int, phase: int) -> tuple[int, None]:
        """
        Set clock simple config.

        :param nut_clk: Nut clk.
        :type nut_clk: int
        :param mult: Mult.
        :type mult: int
        :param phase: Phase.
        :type phase: int
        :return: The device response status
        :rtype: tuple[int, None]
        """
        if not 1 <= nut_clk <= 32:
            raise ValueError("nut_clk must be between 1 and 32")
        if nut_clk * mult > 32:
            raise ValueError("nut_clk * mult must be less than 32")
        payload = struct.pack(">BBI", nut_clk, mult, phase * 1000)
        self._logger.debug(f"osc_set_clock_simple payload: {payload.hex()}")
        status, res = self.send_with_command(protocol.Command.OSC_CLOCK_SIMPLE, payload=payload)
        if status == protocol.STATUS_OK:
            self._config.osc_clock_simple = nut_clk, mult, phase

        return status, None

    def osc_set_sample_phase(self, phase: int) -> tuple[int, None]:
        """
        Set sample phase.

        :param phase: Sample phase.
        :type phase: int
        :return: The device response status
        :rtype: tuple[int, None]
        """
        payload = struct.pack(">I", phase)
        self._logger.debug(f"osc_set_sample_phase payload: {payload.hex()}")
        status, res = self.send_with_command(protocol.Command.OSC_CLOCK_SAMPLE_PHASE, payload=payload)
        if status == protocol.STATUS_OK:
            self._config.osc_sample_phase = phase

        return status, None

    def nut_power_off(self) -> tuple[int, None]:
        return self._nut_power(False)

    def nut_power_on(self) -> tuple[int, None]:
        return self._nut_power(True)

    def nut_set_enable(self, enable: int | bool) -> tuple[int, None]:
        return self._nut_power(enable)

    def _nut_power(self, enable: int | bool) -> tuple[int, None]:
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
        self._logger.debug(f"cracker_nut_enable payload: {payload.hex()}")
        status, res = self.send_with_command(protocol.Command.NUT_ENABLE, payload=payload)
        if status == protocol.STATUS_OK:
            self._config.nut_enable = enable

        return status, None

    def nut_set_voltage(self, voltage: int) -> tuple[int, None]:
        """
        Set nut voltage.

        :param voltage: Nut voltage, in milli volts (mV).
        :type voltage: int
        :return: The device response status
        :rtype: tuple[int, None]
        """
        payload = struct.pack(">I", voltage)
        self._logger.debug(f"cracker_nut_voltage payload: {payload.hex()}")
        status, res = self.send_with_command(protocol.Command.NUT_VOLTAGE, payload=payload)
        if status == protocol.STATUS_OK:
            self._config.nut_voltage = voltage

        return status, None

    def nut_set_voltage_raw(self, voltage: int) -> tuple[int, None]:
        """
        Set nut raw voltage.

        :param voltage: Nut voltage, in milli volts (mV).
        :type voltage: int
        :return: The device response status
        :rtype: tuple[int, None]
        """
        payload = struct.pack(">B", voltage)
        self._logger.debug(f"cracker_nut_voltage payload: {payload.hex()}")
        status, res = self.send_with_command(protocol.Command.NUT_VOLTAGE_RAW, payload=payload)
        if status == protocol.STATUS_OK:
            self._config.nut_voltage_raw = voltage

        return status, None

    def nut_set_clock(self, clock: int) -> tuple[int, None]:
        """
        Set nut clock.

        :param clock: The clock of the nut in kHz
        :type clock: int
        :return: The device response status
        :rtype: tuple[int, None]
        """
        payload = struct.pack(">I", clock)
        self._logger.debug(f"cracker_nut_clock payload: {payload.hex()}")
        status, res = self.send_with_command(protocol.Command.NUT_CLOCK, payload=payload)
        if status == protocol.STATUS_OK:
            self._config.nut_clock = clock

        return status, None

    def nut_set_interface(self, interface: int) -> tuple[int, None]:
        """
        Set nut interface.

        :param interface: Nut interface.
        :type interface: int
        :return: The device response status
        :rtype: tuple[int, None]
        """
        payload = struct.pack(">I", interface)
        self._logger.debug(f"cracker_nut_interface payload: {payload.hex()}")
        status, res = self.send_with_command(protocol.Command.NUT_INTERFACE, payload=payload)
        if status == protocol.STATUS_OK:
            self._config.nut_interface = interface

        return status, None

    def nut_set_timeout(self, timeout: int) -> tuple[int, None]:
        """
        Set nut timeout.

        :param timeout: Nut timeout.
        :type timeout: int
        :return: The device response status
        :rtype: tuple[int, None]
        """
        payload = struct.pack(">I", timeout)
        self._logger.debug(f"cracker_nut_timeout payload: {payload.hex()}")
        status, res = self.send_with_command(protocol.Command.NUT_TIMEOUT, payload=payload)
        if status == protocol.STATUS_OK:
            self._config.nut_timeout = timeout

        return status, None

    def set_clock_nut_divisor(self, div: int) -> tuple[int, None]:
        """
        Set nut divisor.

        :param div: Nut divisor.
        :type div: int
        :return: The device response status
        :rtype: tuple[int, None]
        """
        payload = struct.pack(">B", div)
        self._logger.debug(f"set_clock_nut_divisor payload: {payload.hex()}")
        status, res = self.send_with_command(protocol.Command.OSC_CLOCK_NUT_DIVISOR, payload=payload)
        if status == protocol.STATUS_OK:
            self._config.osc_clock_divisor = div

        return status, None

    def spi_enable(self, enable: bool):
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
            self.get_current_config().cracker_uart_enable = enable
        return status, res

    def spi_reset(self) -> tuple[int, None]:
        """
        Reset the SPI hardware.

        :return: The device response status.
        :rtype: tuple[int, None]
        """
        payload = None
        self._logger.debug(f"cracker_spi_reset payload: {payload}")
        return self.send_with_command(protocol.Command.CRACKER_SPI_RESET)

    def spi_config(
        self,
        speed: int = 10_000,
        cpol: serial.SpiCpol = serial.SpiCpol.SPI_CPOL_LOW,
        cpha: serial.SpiCpha = serial.SpiCpha.SPI_CPHA_LOW,
    ) -> tuple[int, None]:
        """
        Config the SPI.

        :param speed: SPI speed.
        :type speed: int
        :param cpol: Clock polarity.
        :type cpol: serial.SpiCpol
        :param cpha: Clock phase.
        :type cpha: serial.SpiCpha
        :return: The device response status.
        :rtype: tuple[int, None]
        """

        # System clock is 100e6
        # Clock divider is 2
        # psc max is 65535
        psc = 100e6 / 2 / speed
        if psc > 65535 or psc < 2:
            return protocol.STATUS_COMMAND_UNSUPPORTED, None

        if not psc.is_integer():
            _psc = psc
            psc = round(psc)
            if psc > 65535 or psc < 2:
                return protocol.STATUS_COMMAND_UNSUPPORTED, None
            self._logger.warning(
                f"The speed: [{speed}] cannot calculate an integer Prescaler, " f"so the integer value is set to {psc}."
            )

        payload = struct.pack(">HBB", int(psc), cpol.value, cpha.value)
        self._logger.debug(f"cracker_spi_config payload: {payload.hex()}")
        status, res = self.send_with_command(protocol.Command.CRACKER_SPI_CONFIG, payload=payload)
        if status == protocol.STATUS_OK:
            self.get_current_config().cracker_i2c_config = {
                "speed": speed,
                "cpol": cpol,
                "cpha": cpha,
            }
        return status, res

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

    def i2c_enable(self, enable: bool):
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
            self.get_current_config().cracker_uart_enable = enable
        return status, res

    def i2c_reset(self) -> tuple[int, None]:
        """
        Reset the I2C.

        :return: The device response status.
        :rtype: tuple[int, None]
        """
        payload = None
        self._logger.debug(f"cracker_i2c_reset payload: {payload}")
        return self.send_with_command(protocol.Command.CRACKER_I2C_RESET)

    def i2c_config(
        self,
        dev_addr: int = 0x00,
        speed: serial.I2cSpeed = serial.I2cSpeed.STANDARD_100K,
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

        payload = struct.pack(">BB", dev_addr, speed.value)
        self._logger.debug(f"cracker_i2c_config payload: {payload.hex()}")
        status, res = self.send_with_command(protocol.Command.CRACKER_I2C_CONFIG, payload=payload)
        if status == protocol.STATUS_OK:
            self.get_current_config().cracker_i2c_config = {
                "dev_addr": dev_addr,
                "speed": speed,
            }
        return status, res

    def _i2c_transceive(
        self,
        addr: str | int,
        tx_data: bytes | str | None,
        speed: int,
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

        :param addr: I2C device address, 7-bit length.
        :type addr: str | int
        :param tx_data: The data to be sent.
        :type tx_data: bytes | str | None
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
        :return: The device response status and the data received from the I2C device.
                 Return None if an exception is caught.
        :rtype: tuple[int, bytes | None]
        """
        if isinstance(addr, str):
            addr = int(addr, 16)

        if addr > (1 << 7) - 1:
            raise ValueError("Illegal address")

        if isinstance(tx_data, str):
            tx_data = bytes.fromhex(tx_data)

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

        if tx_data is not None:
            payload += tx_data
        status, res = self.send_with_command(protocol.Command.CRACKER_I2C_TRANSCEIVE, payload=payload)
        if status != protocol.STATUS_OK:
            self._logger.error(f"Receive status code error [{status}]")
            return status, None
        else:
            return status, res

    def i2c_transmit(self, addr: str | int, tx_data: bytes | str, is_trigger: bool = False) -> tuple[int, None]:
        """
        Send data through the I2C protocol.

        :param addr: I2C device address, 7-bit length.
        :type addr: str | int
        :param tx_data: The data to be sent.
        :type tx_data: str | bytes
        :param is_trigger: Whether the transmit trigger is enabled.
        """
        transfer_rw = (0, 0, 0, 0, 0, 0, 0, 0)
        transfer_lens = (len(tx_data), 0, 0, 0, 0, 0, 0, 0)
        status, _ = self._i2c_transceive(
            addr,
            tx_data,
            speed=0,
            combined_transfer_count_1=1,
            combined_transfer_count_2=0,
            transfer_rw=transfer_rw,
            transfer_lens=transfer_lens,
            is_delay=False,
            delay=0,
            is_trigger=is_trigger,
        )
        return status, None

    def i2c_receive(self, addr: str | int, rx_count, is_trigger: bool = False) -> tuple[int, bytes | None]:
        """
        Receive data through the I2C protocol.

        :param addr: I2C device address, 7-bit length.
        :type addr: str | int
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
            addr,
            tx_data=None,
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
        self, addr: str | int, tx_data: bytes | str, delay: int, rx_count: int, is_trigger: bool = False
    ) -> tuple[int, bytes | None]:
        """
        Send and receive data with delay through the I2C protocol.

        :param addr: I2C device address, 7-bit length.
        :type addr: str | int
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
        transfer_rw = (0, 0, 0, 0, 1, 1, 1, 1)
        transfer_lens = (len(tx_data), 0, 0, 0, rx_count, 0, 0, 0)
        return self._i2c_transceive(
            addr,
            tx_data,
            speed=0,
            combined_transfer_count_1=1,
            combined_transfer_count_2=1,
            transfer_rw=transfer_rw,
            transfer_lens=transfer_lens,
            is_delay=True,
            delay=delay,
            is_trigger=is_trigger,
        )

    def i2c_transceive(self, addr, tx_data, rx_count, is_trigger: bool = False) -> tuple[int, bytes | None]:
        """
        Send and receive data without delay through the I2C protocol.

        :param addr: I2C device address, 7-bit length.
        :type addr: str | int
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
        transfer_rw = (0, 0, 0, 0, 1, 1, 1, 1)
        transfer_lens = (len(tx_data), 0, 0, 0, rx_count, 0, 0, 0)
        return self._i2c_transceive(
            addr,
            tx_data,
            speed=0,
            combined_transfer_count_1=1,
            combined_transfer_count_2=1,
            transfer_rw=transfer_rw,
            transfer_lens=transfer_lens,
            is_delay=False,
            delay=0,
            is_trigger=is_trigger,
        )

    def uart_enable(self, enable: bool) -> tuple[int, None]:
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
            self.get_current_config().cracker_uart_enable = enable
        return status, res

    def uart_reset(self) -> tuple[int, None]:
        """
        Reset the UART hardware.

        :return: The device response status.
        :rtype: tuple[int, None]
        """
        payload = None
        self._logger.debug(f"cracker_uart_reset payload: {payload}")
        return self.send_with_command(protocol.Command.CRACKER_UART_RESET)

    def uart_config(
        self,
        baudrate: serial.Baudrate = serial.Baudrate.BAUDRATE_115200,
        bytesize: serial.Bytesize = serial.Bytesize.EIGHTBITS,
        parity: serial.Parity = serial.Parity.PARITY_NONE,
        stopbits: serial.Stopbits = serial.Stopbits.STOPBITS_ONE,
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

        payload = struct.pack(">BBBI", stopbits.value, parity.value, bytesize.value, baudrate.value)
        self._logger.debug(f"cracker_uart_config payload: {payload.hex()}")
        status, res = self.send_with_command(protocol.Command.CRACKER_UART_CONFIG, payload=payload)
        if status == protocol.STATUS_OK:
            self.get_current_config().cracker_uart_config = {
                "baudrate": baudrate,
                "bytesize": bytesize,
                "parity": parity,
                "stopbits": stopbits,
            }
        return status, res

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

    def uart_receive_fifo_dump(self) -> tuple[int, bytes | None]:
        """
        Read all the remaining data from the UART receive FIFO.

        :return: The device response status and all the remaining unread bytes.
        :rtype: tuple[int, bytes | None]
        """
        payload = None
        self._logger.debug(f"cracker_uart_receive_fifo_dump payload: {payload}")
        return self.send_with_command(protocol.Command.CRACKER_UART_CRACKER_UART_RECEIVE_FIFO_DUMP)

    def uart_receive_fifo_clear(self) -> tuple[int, bytes | None]:
        """
        Clear all the remaining data in the UART receive FIFO.

        :return: The device response status and all the remaining unread bytes.
        :rtype: tuple[int, bytes | None]
        """
        payload = None
        self._logger.debug(f"cracker_uart_receive_fifo_dump payload: {payload}")
        return self.send_with_command(protocol.Command.CRACKER_UART_CRACKER_UART_RECEIVE_CLEAR)

    def cracker_serial_baud(self, baud: int) -> tuple[int, bytes | None]:
        payload = struct.pack(">I", baud)
        self._logger.debug(f"cracker_serial_baud payload: {payload.hex()}")
        status, res = self.send_with_command(protocol.Command.CRACKER_SERIAL_BAUD, payload=payload)
        if status != protocol.STATUS_OK:
            return status, None
        else:
            return status, res

    def cracker_serial_width(self, width: int) -> tuple[int, bytes | None]:
        payload = struct.pack(">B", width)
        self._logger.debug(f"cracker_serial_width payload: {payload.hex()}")
        status, res = self.send_with_command(protocol.Command.CRACKER_SERIAL_WIDTH, payload=payload)
        if status != protocol.STATUS_OK:
            self._logger.error(f"Receive status code error [{status}]")
            return status, None
        else:
            return status, res

    def cracker_serial_stop(self, stop: int) -> tuple[int, bytes | None]:
        payload = struct.pack(">B", stop)
        self._logger.debug(f"cracker_serial_stop payload: {payload.hex()}")
        status, res = self.send_with_command(protocol.Command.CRACKER_SERIAL_STOP, payload=payload)
        if status != protocol.STATUS_OK:
            self._logger.error(f"Receive status code error [{status}]")
            return status, None
        else:
            return status, res

    def cracker_serial_odd_eve(self, odd_eve: int) -> tuple[int, bytes | None]:
        payload = struct.pack(">B", odd_eve)
        self._logger.debug(f"cracker_serial_odd_eve payload: {payload.hex()}")
        status, res = self.send_with_command(protocol.Command.CRACKER_SERIAL_ODD_EVE, payload=payload)
        if status != protocol.STATUS_OK:
            self._logger.error(f"Receive status code error [{status}]")
            return status, None
        else:
            return status, res

    def cracker_serial_data(self, expect_len: int, data: bytes | str) -> tuple[int, bytes | None]:
        if isinstance(data, str):
            data = bytes.fromhex(data)
        payload = struct.pack(">I", expect_len)
        payload += data
        self._logger.debug(f"cracker_serial_data payload: {payload.hex()}")
        status, res = self.send_with_command(protocol.Command.CRACKER_SERIAL_DATA, payload=payload)
        if status != protocol.STATUS_OK:
            self._logger.error(f"Receive status code error [{status}]")
            return status, None
        else:
            return status, res

    # def cracker_spi_cpol(self, cpol: int) -> tuple[int, bytes | None]:
    #     payload = struct.pack(">B", cpol)
    #     self._logger.debug(f"cracker_spi_cpol payload: {payload.hex()}")
    #     status, res = self.send_with_command(protocol.Command.CRACKER_SPI_CPOL, payload=payload)
    #     if status != protocol.STATUS_OK:
    #         self._logger.error(f"Receive status code error [{status}]")
    #         return status, None
    #     else:
    #         return status, res
    #
    # def cracker_spi_cpha(self, cpha: int) -> tuple[int, bytes | None]:
    #     payload = struct.pack(">B", cpha)
    #     self._logger.debug(f"cracker_spi_cpha payload: {payload.hex()}")
    #     status, res = self.send_with_command(protocol.Command.CRACKER_SPI_CPHA, payload=payload)
    #     if status != protocol.STATUS_OK:
    #         self._logger.error(f"Receive status code error [{status}]")
    #         return status, None
    #     else:
    #         return status, res
    #
    # def cracker_spi_data_len(self, length: int) -> tuple[int, bytes | None]:
    #     payload = struct.pack(">B", length)
    #     self._logger.debug(f"cracker_spi_data_len payload: {payload.hex()}")
    #     status, res = self.send_with_command(protocol.Command.CRACKER_SPI_DATA_LEN, payload=payload)
    #     if status != protocol.STATUS_OK:
    #         self._logger.error(f"Receive status code error [{status}]")
    #         return status, None
    #     else:
    #         return status, res
    #
    # def cracker_spi_freq(self, freq: int) -> tuple[int, bytes | None]:
    #     payload = struct.pack(">B", freq)
    #     self._logger.debug(f"cracker_spi_freq payload: {payload.hex()}")
    #     status, res = self.send_with_command(protocol.Command.CRACKER_SPI_FREQ, payload=payload)
    #     if status != protocol.STATUS_OK:
    #         self._logger.error(f"Receive status code error [{status}]")
    #         return status, None
    #     else:
    #         return status, res
    #
    # def cracker_spi_timeout(self, timeout: int) -> tuple[int, bytes | None]:
    #     payload = struct.pack(">B", timeout)
    #     self._logger.debug(f"cracker_spi_timeout payload: {payload.hex()}")
    #     status, res = self.send_with_command(protocol.Command.CRACKER_SPI_TIMEOUT, payload=payload)
    #     if status != protocol.STATUS_OK:
    #         self._logger.error(f"Receive status code error [{status}]")
    #         return status, None
    #     else:
    #         return status, res
    #
    # def cracker_i2c_freq(self, freq: int) -> tuple[int, bytes | None]:
    #     payload = struct.pack(">B", freq)
    #     self._logger.debug(f"cracker_i2c_freq payload: {payload.hex()}")
    #     status, res = self.send_with_command(protocol.Command.CRACKER_I2C_FREQ, payload=payload)
    #     if status != protocol.STATUS_OK:
    #         self._logger.error(f"Receive status code error [{status}]")
    #         return status, None
    #     else:
    #         return status, res
    #
    # def cracker_i2c_timeout(self, timeout: int) -> tuple[int, bytes | None]:
    #     payload = struct.pack(">B", timeout)
    #     self._logger.debug(f"cracker_i2c_timeout payload: {payload.hex()}")
    #     status, res = self.send_with_command(protocol.Command.CRACKER_I2C_TIMEOUT, payload=payload)
    #     if status != protocol.STATUS_OK:
    #         self._logger.error(f"Receive status code error [{status}]")
    #         return status, None
    #     else:
    #         return status, res
    #
    # def cracker_i2c_data(self, expect_len: int, data: bytes) -> tuple[int, bytes | None]:
    #     payload = struct.pack(">I", expect_len)
    #     payload += data
    #     self._logger.debug(f"cracker_i2c_data payload: {payload.hex()}")
    #     status, res = self.send_with_command(protocol.Command.CRACKER_I2C_TRANSCEIVE, payload=payload)
    #     if status != protocol.STATUS_OK:
    #         self._logger.error(f"Receive status code error [{status}]")
    #         return status, None
    #     else:
    #         return status, res
    #
    # def cracker_can_freq(self, freq: int) -> tuple[int, bytes | None]:
    #     payload = struct.pack(">B", freq)
    #     self._logger.debug(f"cracker_can_freq payload: {payload.hex()}")
    #     status, res = self.send_with_command(protocol.Command.CRACKER_CAN_FREQ, payload=payload)
    #     if status != protocol.STATUS_OK:
    #         self._logger.error(f"Receive status code error [{status}]")
    #         return status, None
    #     else:
    #         return status, res
    #
    # def cracker_can_timeout(self, timeout: int) -> tuple[int, bytes | None]:
    #     payload = struct.pack(">B", timeout)
    #     self._logger.debug(f"cracker_can_timeout payload: {payload.hex()}")
    #     status, res = self.send_with_command(protocol.Command.CRACKER_CAN_TIMEOUT, payload=payload)
    #     if status != protocol.STATUS_OK:
    #         self._logger.error(f"Receive status code error [{status}]")
    #         return status, None
    #     else:
    #         return status, res
    #
    # def cracker_can_data(self, expect_len: int, data: bytes):
    #     payload = struct.pack(">I", expect_len)
    #     payload += data
    #     self._logger.debug(f"cracker_can_data payload: {payload.hex()}")
    #     status, res = self.send_with_command(protocol.Command.CRACKER_CA_DATA, payload=payload)
    #     if status != protocol.STATUS_OK:
    #         self._logger.error(f"Receive status code error [{status}]")
    #         return None
    #     else:
    #         return res
