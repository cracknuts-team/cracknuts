# Copyright 2024 CrackNuts. All rights reserved.

import struct

from cracknuts.cracker import protocol
from cracknuts.cracker.cracker_basic import ConfigBasic, CrackerBasic


class ConfigS1(ConfigBasic):
    def __init__(self):
        super().__init__()
        self.int_dict_fields = (
            "osc_analog_channel_enable",
            "osc_analog_coupling",
            "osc_analog_voltage",
            "osc_analog_bias_voltage",
            "osc_analog_gain",
            "osc_analog_gain_raw",
        )

        self.nut_enable = False
        self.nut_voltage = 3500
        self.nut_clock = 65000

        self.osc_analog_channel_enable = {1: False, 2: True}
        self.osc_analog_gain = {1: 50, 2: 50}
        self.osc_sample_len = 1024
        self.osc_sample_delay = 0
        self.osc_sample_rate = 65000
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

        self.nut_voltage_raw: int | None = None
        self.nut_interface: int | None = None
        self.nut_timeout: int | None = None


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

    def cracker_read_register(self, base_address: int, offset: int) -> bytes | None:
        """
        Read register.

        :param base_address: Base address of the register.
        :type base_address: int
        :param offset: Offset of the register.
        :type offset: int
        :return: The value read from the register or None if an exception is raised.
        """
        payload = struct.pack(">II", base_address, offset)
        self._logger.debug(f"cracker_read_register payload: {payload.hex()}")
        status, res = self.send_with_command(protocol.Command.CRACKER_READ_REGISTER, payload=payload)
        if status != protocol.STATUS_OK:
            self._logger.error(f"Receive status code error [{status}]")
            return None
        else:
            return res

    def cracker_write_register(self, base_address: int, offset: int, data: bytes | int | str) -> None:
        """
        Write register.

        :param base_address: Base address of the register.
        :type base_address: int
        :param offset: Offset of the register.
        :type offset: int
        :param data: Data to write.
        :return: None
        """
        if isinstance(data, str):
            if data.startswith("0x") or data.startswith("0X"):
                data = data[2:]
            data = bytes.fromhex(data)
        if isinstance(data, int):
            data = struct.pack(">I", data)
        payload = struct.pack(">II", base_address, offset) + data
        self._logger.debug(f"cracker_write_register payload: {payload.hex()}")
        status, res = self.send_with_command(protocol.Command.CRACKER_WRITE_REGISTER, payload=payload)
        if status != protocol.STATUS_OK:
            self._logger.error(f"Receive status code error [{status}]")

    def osc_set_analog_channel_enable(self, channel: int, enable: bool) -> None:
        """
        Set analog channel enable.

        :param channel: Channel to enable.
        :type channel: int
        :param enable: Enable or disable.
        :type enable: bool
        :return: None
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
        if status != protocol.STATUS_OK:
            self._logger.error(f"Receive status code error [{status}]")
        else:
            self._config.osc_analog_channel_enable = final_enable

    def osc_set_analog_coupling(self, channel: int, coupling: int) -> None:
        """
        Set analog coupling.

        :param channel: Channel to enable.
        :type channel: int
        :param coupling: 1 for DC and 0 for AC.
        :type coupling: int
        :return: None
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
        if status != protocol.STATUS_OK:
            self._logger.error(f"Receive status code error [{status}]")
        else:
            self._config.osc_analog_coupling = final_coupling

    def osc_set_analog_voltage(self, channel: int, voltage: int) -> None:
        """
        Set analog voltage.

        :param channel: Channel to enable.
        :type channel: int
        :param voltage: Voltage to set. unit: mV.
        :type voltage: int
        :return: None
        """
        payload = struct.pack(">BI", channel, voltage)
        self._logger.debug(f"scrat_analog_coupling payload: {payload.hex()}")
        status, res = self.send_with_command(protocol.Command.OSC_ANALOG_VOLTAGE, payload=payload)
        if status != protocol.STATUS_OK:
            self._logger.error(f"Receive status code error [{status}]")
        else:
            self._config.osc_analog_voltage[channel] = voltage

    def osc_set_analog_bias_voltage(self, channel: int, voltage: int):
        """
        Set analog bias voltage.

        :param channel: Channel to enable.
        :type channel: int
        :param voltage: Voltage to set. unit: mV.
        :type voltage: int
        :return: None
        """
        payload = struct.pack(">BI", channel, voltage)
        self._logger.debug(f"scrat_analog_bias_voltage payload: {payload.hex()}")
        status, res = self.send_with_command(protocol.Command.OSC_ANALOG_BIAS_VOLTAGE, payload=payload)
        if status != protocol.STATUS_OK:
            self._logger.error(f"Receive status code error [{status}]")
        else:
            self._config.osc_analog_bias_voltage[channel] = voltage

    def osc_set_digital_channel_enable(self, channel: int, enable: bool) -> None:
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
        if status != protocol.STATUS_OK:
            self._logger.error(f"Receive status code error [{status}]")
        else:
            self._config.osc_digital_channel_enable = final_enable

    def osc_set_digital_voltage(self, voltage: int):
        payload = struct.pack(">I", voltage)
        self._logger.debug(f"scrat_digital_voltage payload: {payload.hex()}")
        status, res = self.send_with_command(protocol.Command.OSC_DIGITAL_VOLTAGE, payload=payload)
        if status != protocol.STATUS_OK:
            self._logger.error(f"Receive status code error [{status}]")
        else:
            self._config.osc_digital_voltage = voltage

    def osc_set_trigger_mode(self, mode: int) -> None:
        """
        Set trigger mode.

        :param mode: Trigger mode. Trigger mode: 0 for edge, 1 for wave.
        :type mode: int
        :return: None
        """
        payload = struct.pack(">B", mode)
        self._logger.debug(f"osc_set_trigger_mode payload: {payload.hex()}")
        status, res = self.send_with_command(protocol.Command.OSC_TRIGGER_MODE, payload=payload)
        if status != protocol.STATUS_OK:
            self._logger.error(f"Receive status code error [{status}]")
        else:
            self._config.osc_trigger_mode = mode

    def osc_set_analog_trigger_source(self, source: int | str) -> None:
        """
        Set trigger source.

        :param source: Trigger source: 'N', 'A', 'B', 'P', or 0, 1, 2, 3
                       represent Nut, Channel A, Channel B, and Protocol, respectively.
        :type source: int | str
        :return: None
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
        if status != protocol.STATUS_OK:
            self._logger.error(f"Receive status code error [{status}]")
        else:
            self._config.osc_analog_trigger_source = source

    def osc_set_digital_trigger_source(self, channel: int):
        payload = struct.pack(">B", channel)
        self._logger.debug(f"scrat_digital_trigger_source payload: {payload.hex()}")
        status, res = self.send_with_command(protocol.Command.OSC_DIGITAL_TRIGGER_SOURCE, payload=payload)
        if status != protocol.STATUS_OK:
            self._logger.error(f"Receive status code error [{status}]")
        else:
            self._config.osc_digital_trigger_source = channel

    def osc_set_trigger_edge(self, edge: int | str) -> None:
        """
        Set trigger edge.

        :param edge: Trigger edge. 'up', 'down', 'either' or 0, 1, 2 represent up, down, either, respectively.
        :type edge: int
        :return: None
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
        if status != protocol.STATUS_OK:
            self._logger.error(f"Receive status code error [{status}]")
        else:
            self._config.osc_analog_trigger_edge = edge

    def osc_set_trigger_edge_level(self, edge_level: int) -> None:
        """
        Set trigger edge level.

        :param edge_level: Edge level.
        :type edge_level: int
        :return: None
        """
        payload = struct.pack(">H", edge_level)
        self._logger.debug(f"scrat_analog_trigger_edge_level payload: {payload.hex()}")
        status, res = self.send_with_command(protocol.Command.OSC_TRIGGER_EDGE_LEVEL, payload=payload)
        if status != protocol.STATUS_OK:
            self._logger.error(f"Receive status code error [{status}]")
        else:
            self._config.osc_analog_trigger_edge_level = edge_level

    def osc_set_analog_trigger_voltage(self, voltage: int):
        payload = struct.pack(">I", voltage)
        self._logger.debug(f"scrat_analog_trigger_voltage payload: {payload.hex()}")
        status, res = self.send_with_command(protocol.Command.OSC_ANALOG_TRIGGER_VOLTAGE, payload=payload)
        if status != protocol.STATUS_OK:
            self._logger.error(f"Receive status code error [{status}]")
        else:
            self._config.osc_analog_trigger_voltage = voltage

    def osc_set_sample_delay(self, delay: int):
        payload = struct.pack(">i", delay)
        self._logger.debug(f"osc_sample_delay payload: {payload.hex()}")
        status, res = self.send_with_command(protocol.Command.OSC_SAMPLE_DELAY, payload=payload)
        if status != protocol.STATUS_OK:
            self._logger.error(f"Receive status code error [{status}]")
        else:
            self._config.osc_sample_delay = delay

    def osc_set_sample_len(self, length: int) -> None:
        """
        Set sample length.

        :param length: Sample length.
        :type length: int
        :return: None
        """
        payload = struct.pack(">I", length)
        self._logger.debug(f"osc_set_sample_len payload: {payload.hex()}")
        status, res = self.send_with_command(protocol.Command.OSC_SAMPLE_LENGTH, payload=payload)
        if status != protocol.STATUS_OK:
            self._logger.error(f"Receive status code error [{status}]")
        else:
            self._config.osc_sample_len = length

    def osc_set_sample_rate(self, rate: int) -> None:
        """
        Set osc sample rate

        :param rate: The sample rate in kHz, one of (65000, 48000, 24000, 12000, 8000, 4000)
        :type rate: int
        :return: None
        """
        payload = struct.pack(">I", rate)
        self._logger.debug(f"osc_set_sample_rate payload: {payload.hex()}")
        status, res = self.send_with_command(protocol.Command.OSC_SAMPLE_RATE, payload=payload)
        if status != protocol.STATUS_OK:
            self._logger.error(f"Receive status code error [{status}]")
        else:
            self._config.osc_sample_rate = rate

    def osc_set_analog_gain(self, channel: int, gain: int):
        payload = struct.pack(">BB", channel, gain)
        self._logger.debug(f"scrat_analog_gain payload: {payload.hex()}")
        status, res = self.send_with_command(protocol.Command.OSC_ANALOG_GAIN, payload=payload)
        if status != protocol.STATUS_OK:
            self._logger.error(f"Receive status code error [{status}]")
        else:
            self._config.osc_analog_gain[channel] = gain

    def osc_set_analog_gain_raw(self, channel: int, gain: int):
        payload = struct.pack(">BB", channel, gain)
        self._logger.debug(f"scrat_analog_gain payload: {payload.hex()}")
        status, res = self.send_with_command(protocol.Command.OSC_ANALOG_GAIN_RAW, payload=payload)
        if status != protocol.STATUS_OK:
            self._logger.error(f"Receive status code error [{status}]")
        else:
            self._config.osc_analog_gain_raw[channel] = gain

    def osc_force(self):
        payload = None
        self._logger.debug(f"scrat_force payload: {payload}")
        status, res = self.send_with_command(protocol.Command.OSC_FORCE, payload=payload)
        if status != protocol.STATUS_OK:
            self._logger.error(f"Receive status code error [{status}]")

    def osc_set_clock_base_freq_mul_div(self, mult_int: int, mult_fra: int, div: int):
        payload = struct.pack(">BHB", mult_int, mult_fra, div)
        self._logger.debug(f"osc_set_clock_base_freq_mul_div payload: {payload.hex()}")
        status, res = self.send_with_command(protocol.Command.OSC_CLOCK_BASE_FREQ_MUL_DIV, payload=payload)
        if status != protocol.STATUS_OK:
            self._logger.error(f"Receive status code error [{status}]")
        else:
            self._config.osc_clock_base_freq_mul_div = mult_int, mult_fra, div

    def osc_set_sample_divisor(self, div_int: int, div_frac: int):
        payload = struct.pack(">BH", div_int, div_frac)
        self._logger.debug(f"osc_set_sample_divisor payload: {payload.hex()}")
        status, res = self.send_with_command(protocol.Command.OSC_CLOCK_SAMPLE_DIVISOR, payload=payload)
        if status != protocol.STATUS_OK:
            self._logger.error(f"Receive status code error [{status}]")
        else:
            self._config.osc_clock_sample_divisor = div_int, div_frac

    def osc_set_clock_update(self):
        self._logger.debug(f"osc_set_clock_update payload: {None}")
        status, res = self.send_with_command(protocol.Command.OSC_CLOCK_UPDATE, payload=None)
        if status != protocol.STATUS_OK:
            self._logger.error(f"Receive status code error [{status}]")

    def osc_set_clock_simple(self, nut_clk: int, mult: int, phase: int):
        if not 1 <= nut_clk <= 32:
            raise ValueError("nut_clk must be between 1 and 32")
        if nut_clk * mult > 32:
            raise ValueError("nut_clk * mult must be less than 32")
        payload = struct.pack(">BBI", nut_clk, mult, phase * 1000)
        self._logger.debug(f"osc_set_clock_simple payload: {payload.hex()}")
        status, res = self.send_with_command(protocol.Command.OSC_CLOCK_SIMPLE, payload=payload)
        if status != protocol.STATUS_OK:
            self._logger.error(f"Receive status code error [{status}]")
        else:
            self._config.osc_clock_simple = nut_clk, mult, phase

    def osc_set_sample_phase(self, phase: int) -> None:
        """
        Set sample phase.

        :param phase: Sample phase.
        :type phase: int
        :return: None
        """
        payload = struct.pack(">I", phase)
        self._logger.debug(f"osc_set_sample_phase payload: {payload.hex()}")
        status, res = self.send_with_command(protocol.Command.OSC_CLOCK_SAMPLE_PHASE, payload=payload)
        if status != protocol.STATUS_OK:
            self._logger.error(f"Receive status code error [{status}]")
        else:
            self._config.osc_sample_phase = phase

    def nut_set_enable(self, enable: int | bool) -> None:
        """
        Set nut enable.

        :param enable: Enable or disable. 0 for disable, 1 for enable if specified as a integer.
        :type enable: int | bool
        :return: None
        """
        if isinstance(enable, bool):
            enable = 1 if enable else 0
        payload = struct.pack(">B", enable)
        self._logger.debug(f"cracker_nut_enable payload: {payload.hex()}")
        status, res = self.send_with_command(protocol.Command.NUT_ENABLE, payload=payload)
        if status != protocol.STATUS_OK:
            self._logger.error(f"Receive status code error [{status}]")
        else:
            self._config.nut_enable = enable

    def nut_set_voltage(self, voltage: int) -> None:
        """
        Set nut voltage.

        :param voltage: Nut voltage, in milli volts (mV).
        :type voltage: int
        :return: None
        """
        payload = struct.pack(">I", voltage)
        self._logger.debug(f"cracker_nut_voltage payload: {payload.hex()}")
        status, res = self.send_with_command(protocol.Command.NUT_VOLTAGE, payload=payload)
        if status != protocol.STATUS_OK:
            self._logger.error(f"Receive status code error [{status}]")
        else:
            self._config.nut_voltage = voltage

    def nut_set_voltage_raw(self, voltage: int) -> None:
        """
        Set nut raw voltage.

        :param voltage: Nut voltage, in milli volts (mV).
        :type voltage: int
        :return: None
        """
        payload = struct.pack(">B", voltage)
        self._logger.debug(f"cracker_nut_voltage payload: {payload.hex()}")
        status, res = self.send_with_command(protocol.Command.NUT_VOLTAGE_RAW, payload=payload)
        if status != protocol.STATUS_OK:
            self._logger.error(f"Receive status code error [{status}]")
        else:
            self._config.nut_voltage_raw = voltage

    def nut_set_clock(self, clock: int) -> None:
        """
        Set nut clock.

        :param clock: The clock of the nut in kHz
        :type clock: int
        :return: None
        """
        payload = struct.pack(">I", clock)
        self._logger.debug(f"cracker_nut_clock payload: {payload.hex()}")
        status, res = self.send_with_command(protocol.Command.NUT_CLOCK, payload=payload)
        if status != protocol.STATUS_OK:
            self._logger.error(f"Receive status code error [{status}]")
        else:
            self._config.nut_clock = clock

    def nut_set_interface(self, interface: int):
        payload = struct.pack(">I", interface)
        self._logger.debug(f"cracker_nut_interface payload: {payload.hex()}")
        status, res = self.send_with_command(protocol.Command.NUT_INTERFACE, payload=payload)
        if status != protocol.STATUS_OK:
            self._logger.error(f"Receive status code error [{status}]")
        else:
            self._config.nut_interface = interface

    def nut_set_timeout(self, timeout: int):
        payload = struct.pack(">I", timeout)
        self._logger.debug(f"cracker_nut_timeout payload: {payload.hex()}")
        status, res = self.send_with_command(protocol.Command.NUT_TIMEOUT, payload=payload)
        if status != protocol.STATUS_OK:
            self._logger.error(f"Receive status code error [{status}]")
        else:
            self._config.nut_timeout = timeout

    def set_clock_nut_divisor(self, div: int):
        payload = struct.pack(">B", div)
        self._logger.debug(f"set_clock_nut_divisor payload: {payload.hex()}")
        status, res = self.send_with_command(protocol.Command.OSC_CLOCK_NUT_DIVISOR, payload=payload)
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
        status, res = self.send_with_command(protocol.Command.SPI_TRANSCEIVE, payload=payload)
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
        status, res = self.send_with_command(protocol.Command.CRACKER_I2C_TRANSCEIVE, payload=payload)
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
        status, res = self.send_with_command(protocol.Command.CRACKER_SERIAL_BAUD, payload=payload)
        if status != protocol.STATUS_OK:
            self._logger.error(f"Receive status code error [{status}]")
            return None
        else:
            return res

    def cracker_serial_width(self, width: int):
        payload = struct.pack(">B", width)
        self._logger.debug(f"cracker_serial_width payload: {payload.hex()}")
        status, res = self.send_with_command(protocol.Command.CRACKER_SERIAL_WIDTH, payload=payload)
        if status != protocol.STATUS_OK:
            self._logger.error(f"Receive status code error [{status}]")
            return None
        else:
            return res

    def cracker_serial_stop(self, stop: int):
        payload = struct.pack(">B", stop)
        self._logger.debug(f"cracker_serial_stop payload: {payload.hex()}")
        status, res = self.send_with_command(protocol.Command.CRACKER_SERIAL_STOP, payload=payload)
        if status != protocol.STATUS_OK:
            self._logger.error(f"Receive status code error [{status}]")
            return None
        else:
            return res

    def cracker_serial_odd_eve(self, odd_eve: int):
        payload = struct.pack(">B", odd_eve)
        self._logger.debug(f"cracker_serial_odd_eve payload: {payload.hex()}")
        status, res = self.send_with_command(protocol.Command.CRACKER_SERIAL_ODD_EVE, payload=payload)
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
        status, res = self.send_with_command(protocol.Command.CRACKER_SERIAL_DATA, payload=payload)
        if status != protocol.STATUS_OK:
            self._logger.error(f"Receive status code error [{status}]")
            return None
        else:
            return res

    def cracker_spi_cpol(self, cpol: int):
        payload = struct.pack(">B", cpol)
        self._logger.debug(f"cracker_spi_cpol payload: {payload.hex()}")
        status, res = self.send_with_command(protocol.Command.CRACKER_SPI_CPOL, payload=payload)
        if status != protocol.STATUS_OK:
            self._logger.error(f"Receive status code error [{status}]")
            return None
        else:
            return res

    def cracker_spi_cpha(self, cpha: int):
        payload = struct.pack(">B", cpha)
        self._logger.debug(f"cracker_spi_cpha payload: {payload.hex()}")
        status, res = self.send_with_command(protocol.Command.CRACKER_SPI_CPHA, payload=payload)
        if status != protocol.STATUS_OK:
            self._logger.error(f"Receive status code error [{status}]")
            return None
        else:
            return res

    def cracker_spi_data_len(self, length: int):
        payload = struct.pack(">B", length)
        self._logger.debug(f"cracker_spi_data_len payload: {payload.hex()}")
        status, res = self.send_with_command(protocol.Command.CRACKER_SPI_DATA_LEN, payload=payload)
        if status != protocol.STATUS_OK:
            self._logger.error(f"Receive status code error [{status}]")
            return None
        else:
            return res

    def cracker_spi_freq(self, freq: int):
        payload = struct.pack(">B", freq)
        self._logger.debug(f"cracker_spi_freq payload: {payload.hex()}")
        status, res = self.send_with_command(protocol.Command.CRACKER_SPI_FREQ, payload=payload)
        if status != protocol.STATUS_OK:
            self._logger.error(f"Receive status code error [{status}]")
            return None
        else:
            return res

    def cracker_spi_timeout(self, timeout: int):
        payload = struct.pack(">B", timeout)
        self._logger.debug(f"cracker_spi_timeout payload: {payload.hex()}")
        status, res = self.send_with_command(protocol.Command.CRACKER_SPI_TIMEOUT, payload=payload)
        if status != protocol.STATUS_OK:
            self._logger.error(f"Receive status code error [{status}]")
            return None
        else:
            return res

    def cracker_i2c_freq(self, freq: int):
        payload = struct.pack(">B", freq)
        self._logger.debug(f"cracker_i2c_freq payload: {payload.hex()}")
        status, res = self.send_with_command(protocol.Command.CRACKER_I2C_FREQ, payload=payload)
        if status != protocol.STATUS_OK:
            self._logger.error(f"Receive status code error [{status}]")
            return None
        else:
            return res

    def cracker_i2c_timeout(self, timeout: int):
        payload = struct.pack(">B", timeout)
        self._logger.debug(f"cracker_i2c_timeout payload: {payload.hex()}")
        status, res = self.send_with_command(protocol.Command.CRACKER_I2C_TIMEOUT, payload=payload)
        if status != protocol.STATUS_OK:
            self._logger.error(f"Receive status code error [{status}]")
            return None
        else:
            return res

    def cracker_i2c_data(self, expect_len: int, data: bytes):
        payload = struct.pack(">I", expect_len)
        payload += data
        self._logger.debug(f"cracker_i2c_data payload: {payload.hex()}")
        status, res = self.send_with_command(protocol.Command.CRACKER_I2C_TRANSCEIVE, payload=payload)
        if status != protocol.STATUS_OK:
            self._logger.error(f"Receive status code error [{status}]")
            return None
        else:
            return res

    def cracker_can_freq(self, freq: int):
        payload = struct.pack(">B", freq)
        self._logger.debug(f"cracker_can_freq payload: {payload.hex()}")
        status, res = self.send_with_command(protocol.Command.CRACKER_CAN_FREQ, payload=payload)
        if status != protocol.STATUS_OK:
            self._logger.error(f"Receive status code error [{status}]")
            return None
        else:
            return res

    def cracker_can_timeout(self, timeout: int):
        payload = struct.pack(">B", timeout)
        self._logger.debug(f"cracker_can_timeout payload: {payload.hex()}")
        status, res = self.send_with_command(protocol.Command.CRACKER_CAN_TIMEOUT, payload=payload)
        if status != protocol.STATUS_OK:
            self._logger.error(f"Receive status code error [{status}]")
            return None
        else:
            return res

    def cracker_can_data(self, expect_len: int, data: bytes):
        payload = struct.pack(">I", expect_len)
        payload += data
        self._logger.debug(f"cracker_can_data payload: {payload.hex()}")
        status, res = self.send_with_command(protocol.Command.CRACKER_CA_DATA, payload=payload)
        if status != protocol.STATUS_OK:
            self._logger.error(f"Receive status code error [{status}]")
            return None
        else:
            return res
