# Copyright 2024 CrackNuts. All rights reserved.

import struct

import numpy as np

from cracknuts.cracker import protocol
from cracknuts.cracker.cracker import AbsCnpCracker, Commands, Config


class CrackerS1(AbsCnpCracker):
    def __init__(self, *args, **kwargs) -> None:
        super().__init__(*args, **kwargs)
        self._default_config = Config(
            nut_voltage=3500,
            osc_analog_channel_enable={1: True, 2: False},
            osc_sample_len=1024,
        )

    def get_default_config(self) -> Config:
        return self._default_config

    def get_id(self) -> str | None:
        _, res = self.send_and_receive(protocol.build_send_message(Commands.GET_ID))
        return res.decode("ascii") if res is not None else None

    def get_name(self) -> str | None:
        _, res = self.send_and_receive(protocol.build_send_message(Commands.GET_NAME))
        return res.decode("ascii") if res is not None else None

    def get_version(self) -> str | None:
        _, res = self.send_and_receive(protocol.build_send_message(Commands.GET_VERSION))
        return res.decode("ascii") if res is not None else None

    def cracker_read_register(self, base_address: int, offset: int) -> tuple[int, bytes | None]:
        payload = struct.pack(">II", base_address, offset)
        self._logger.debug(f"cracker_read_register payload: {payload.hex()}")
        return self.send_with_command(Commands.CRACKER_READ_REGISTER, payload=payload)

    def cracker_write_register(
        self, base_address: int, offset: int, data: bytes | int | str
    ) -> tuple[int, bytes | None]:
        if isinstance(data, str):
            if data.startswith("0x") or data.startswith("0X"):
                data = data[2:]
            data = bytes.fromhex(data)
        if isinstance(data, int):
            data = data.to_bytes()
        payload = struct.pack(">III", base_address, offset) + data
        self._logger.debug(f"cracker_write_register payload: {payload.hex()}")
        return self.send_with_command(Commands.CRACKER_WRITE_REGISTER, payload=payload)

    def osc_set_analog_channel_enable(self, enable: dict[int, bool]):
        self._channel_enable = enable
        mask = 0
        if enable.get(0):
            mask |= 1
        if enable.get(1):
            mask |= 1 << 1
        if enable.get(2):
            mask |= 1 << 2
        if enable.get(3):
            mask |= 1 << 3
        if enable.get(4):
            mask |= 1 << 4
        if enable.get(5):
            mask |= 1 << 5
        if enable.get(6):
            mask |= 1 << 6
        if enable.get(7):
            mask |= 1 << 7
        if enable.get(8):
            mask |= 1 << 8
        payload = struct.pack(">I", mask)
        self._logger.debug(f"Scrat analog_channel_enable payload: {payload.hex()}")
        return self.send_with_command(Commands.OSC_ANALOG_CHANNEL_ENABLE, payload=payload)

    def osc_set_analog_coupling(self, coupling: dict[int, int]):
        enable = 0
        if coupling.get(0):
            enable |= 1
        if coupling.get(1):
            enable |= 1 << 1
        if coupling.get(2):
            enable |= 1 << 2
        if coupling.get(3):
            enable |= 1 << 3
        if coupling.get(4):
            enable |= 1 << 4
        if coupling.get(5):
            enable |= 1 << 5
        if coupling.get(6):
            enable |= 1 << 6
        if coupling.get(7):
            enable |= 1 << 7
        if coupling.get(8):
            enable |= 1 << 8

        payload = struct.pack(">I", enable)
        self._logger.debug(f"scrat_analog_coupling payload: {payload.hex()}")

        return self.send_with_command(Commands.OSC_ANALOG_COUPLING, payload=payload)

    def osc_set_analog_voltage(self, channel: int, voltage: int):
        payload = struct.pack(">BI", channel, voltage)
        self._logger.debug(f"scrat_analog_coupling payload: {payload.hex()}")
        return self.send_with_command(Commands.OSC_ANALOG_VOLTAGE, payload=payload)

    def osc_set_analog_bias_voltage(self, channel: int, voltage: int):
        payload = struct.pack(">BI", channel, voltage)
        self._logger.debug(f"scrat_analog_bias_voltage payload: {payload.hex()}")
        return self.send_with_command(Commands.OSC_ANALOG_BIAS_VOLTAGE, payload=payload)

    def osc_set_digital_channel_enable(self, enable: dict[int, bool]):
        mask = 0
        if enable.get(0):
            mask |= 1
        if enable.get(1):
            mask |= 1 << 1
        if enable.get(2):
            mask |= 1 << 2
        if enable.get(3):
            mask |= 1 << 3
        if enable.get(4):
            mask |= 1 << 4
        if enable.get(5):
            mask |= 1 << 5
        if enable.get(6):
            mask |= 1 << 6
        if enable.get(7):
            mask |= 1 << 7
        if enable.get(8):
            mask |= 1 << 8
        payload = struct.pack(">I", mask)
        self._logger.debug(f"scrat_digital_channel_enable payload: {payload.hex()}")
        return self.send_with_command(Commands.OSC_DIGITAL_CHANNEL_ENABLE, payload=payload)

    def osc_set_digital_voltage(self, voltage: int):
        payload = struct.pack(">I", voltage)
        self._logger.debug(f"scrat_digital_voltage payload: {payload.hex()}")
        return self.send_with_command(Commands.OSC_DIGITAL_VOLTAGE, payload=payload)

    def osc_set_trigger_mode(self, source: int, stop: int):
        payload = struct.pack(">II", source, stop)
        self._logger.debug(f"scrat_trigger_mode payload: {payload.hex()}")
        return self.send_with_command(Commands.OSC_TRIGGER_MODE, payload=payload)

    def osc_set_analog_trigger_source(self, channel: int):
        payload = struct.pack(">B", channel)
        self._logger.debug(f"scrat_analog_trigger_source payload: {payload.hex()}")
        return self.send_with_command(Commands.OSC_ANALOG_TRIGGER_SOURCE, payload=payload)

    def osc_set_digital_trigger_source(self, channel: int):
        payload = struct.pack(">B", channel)
        self._logger.debug(f"scrat_digital_trigger_source payload: {payload.hex()}")
        return self.send_with_command(Commands.OSC_DIGITAL_TRIGGER_SOURCE, payload=payload)

    def osc_set_analog_trigger_voltage(self, voltage: int):
        payload = struct.pack(">I", voltage)
        self._logger.debug(f"scrat_analog_trigger_voltage payload: {payload.hex()}")
        return self.send_with_command(Commands.OSC_ANALOG_TRIGGER_VOLTAGE, payload=payload)

    def osc_set_sample_delay(self, delay: int):
        payload = struct.pack(">i", delay)
        self._logger.debug(f"osc_sample_delay payload: {payload.hex()}")
        return self.send_with_command(Commands.OSC_SAMPLE_DELAY, payload=payload)

    def osc_set_sample_len(self, length: int):
        payload = struct.pack(">I", length)
        self._logger.debug(f"osc_sample_len payload: {payload.hex()}")
        return self.send_with_command(Commands.OSC_SAMPLE_LENGTH, payload=payload)

    def osc_single(self):
        payload = None
        self._logger.debug("scrat_sample_len payload: %s", payload)
        return self.send_with_command(Commands.OSC_SINGLE, payload=payload)

    def osc_is_triggered(self):
        payload = None
        self._logger.debug(f"scrat_is_triggered payload: {payload}")
        return self.send_with_command(Commands.OSC_IS_TRIGGERED, payload=payload)

    def osc_get_analog_wave(self, channel: int, offset: int, sample_count: int) -> tuple[int, np.ndarray]:
        payload = struct.pack(">BII", channel, offset, sample_count)
        self._logger.debug(f"scrat_get_analog_wave payload: {payload.hex()}")
        status, wave_bytes = self.send_with_command(Commands.OSC_GET_ANALOG_WAVES, payload=payload)
        self._logger.debug(f"scrat_get_analog_wave wave_bytes: {wave_bytes.hex() if wave_bytes is not None else None}")
        if wave_bytes is None:
            return status, np.array([])
        else:
            wave = struct.unpack(f"{sample_count}h", wave_bytes)
            return status, np.array(wave, dtype=np.int16)

    def osc_get_digital_wave(self, channel: int, offset: int, sample_count: int):
        payload = struct.pack(">BII", channel, offset, sample_count)
        self._logger.debug(f"scrat_get_digital_wave payload: {payload.hex()}")
        status, wave_bytes = self.send_with_command(Commands.OSC_GET_ANALOG_WAVES, payload=payload)
        if status > protocol.STATUS_ERROR or wave_bytes is None:
            return status, np.array([])
        else:
            wave = struct.unpack(f">{sample_count}I", wave_bytes)
            return status, np.array(wave, dtype=np.int16)

    def osc_set_analog_gain(self, channel: int, gain: int):
        payload = struct.pack(">BB", channel, gain)
        self._logger.debug(f"scrat_analog_gain payload: {payload.hex()}")
        return self.send_with_command(Commands.OSC_ANALOG_GAIN, payload=payload)

    def osc_set_analog_gain_raw(self, channel: int, gain: int):
        payload = struct.pack(">BB", channel, gain)
        self._logger.debug(f"scrat_analog_gain payload: {payload.hex()}")
        return self.send_with_command(Commands.OSC_ANALOG_GAIN_RAW, payload=payload)

    def nut_enable(self, enable: int):
        payload = struct.pack(">B", enable)
        self._logger.debug(f"cracker_nut_enable payload: {payload.hex()}")
        return self.send_with_command(Commands.NUT_ENABLE, payload=payload)

    def nut_voltage(self, voltage):
        payload = struct.pack(">I", voltage)
        self._logger.debug(f"cracker_nut_voltage payload: {payload.hex()}")
        return self.send_with_command(Commands.NUT_VOLTAGE, payload=payload)

    def nut_voltage_raw(self, voltage: int):
        payload = struct.pack(">B", voltage)
        self._logger.debug(f"cracker_nut_voltage payload: {payload.hex()}")
        return self.send_with_command(Commands.NUT_VOLTAGE_RAW, payload=payload)

    def nut_clock(self, clock: int):
        payload = struct.pack(">I", clock)
        self._logger.debug(f"cracker_nut_clock payload: {payload.hex()}")
        return self.send_with_command(Commands.NUT_CLOCK, payload=payload)

    def nut_interface(self, interface: dict[int, bool]):  # type: ignore
        mask: int = 0
        if interface.get(0):
            mask |= 1
        if interface.get(1):
            mask |= 1 << 1
        if interface.get(2):
            mask |= 1 << 2
        if interface.get(3):
            mask |= 1 << 3

        payload = struct.pack(">I", mask)
        self._logger.debug(f"cracker_nut_interface payload: {payload.hex()}")
        return self.send_with_command(Commands.NUT_INTERFACE, payload=payload)

    def nut_timeout(self, timeout: int):
        payload = struct.pack(">I", timeout)
        self._logger.debug(f"cracker_nut_timeout payload: {payload.hex()}")
        return self.send_with_command(Commands.NUT_TIMEOUT, payload=payload)

    def cracker_serial_baud(self, baud: int):
        payload = struct.pack(">I", baud)
        self._logger.debug(f"cracker_serial_baud payload: {payload.hex()}")
        return self.send_with_command(Commands.CRACKER_SERIAL_BAUD, payload=payload)

    def cracker_serial_width(self, width: int):
        payload = struct.pack(">B", width)
        self._logger.debug(f"cracker_serial_width payload: {payload.hex()}")
        return self.send_with_command(Commands.CRACKER_SERIAL_WIDTH, payload=payload)

    def cracker_serial_stop(self, stop: int):
        payload = struct.pack(">B", stop)
        self._logger.debug(f"cracker_serial_stop payload: {payload.hex()}")
        return self.send_with_command(Commands.CRACKER_SERIAL_STOP, payload=payload)

    def cracker_serial_odd_eve(self, odd_eve: int):
        payload = struct.pack(">B", odd_eve)
        self._logger.debug(f"cracker_serial_odd_eve payload: {payload.hex()}")
        return self.send_with_command(Commands.CRACKER_SERIAL_ODD_EVE, payload=payload)

    def cracker_serial_data(self, expect_len: int, data: bytes):
        payload = struct.pack(">I", expect_len)
        payload += data
        self._logger.debug(f"cracker_serial_data payload: {payload.hex()}")
        return self.send_with_command(Commands.CRACKER_SERIAL_DATA, payload=payload)

    def cracker_spi_cpol(self, cpol: int):
        payload = struct.pack(">B", cpol)
        self._logger.debug(f"cracker_spi_cpol payload: {payload.hex()}")
        return self.send_with_command(Commands.CRACKER_SPI_CPOL, payload=payload)

    def cracker_spi_cpha(self, cpha: int):
        payload = struct.pack(">B", cpha)
        self._logger.debug(f"cracker_spi_cpha payload: {payload.hex()}")
        return self.send_with_command(Commands.CRACKER_SPI_CPHA, payload=payload)

    def cracker_spi_data_len(self, length: int):
        payload = struct.pack(">B", length)
        self._logger.debug(f"cracker_spi_data_len payload: {payload.hex()}")
        return self.send_with_command(Commands.CRACKER_SPI_DATA_LEN, payload=payload)

    def cracker_spi_freq(self, freq: int):
        payload = struct.pack(">B", freq)
        self._logger.debug(f"cracker_spi_freq payload: {payload.hex()}")
        return self.send_with_command(Commands.CRACKER_SPI_FREQ, payload=payload)

    def cracker_spi_timeout(self, timeout: int):
        payload = struct.pack(">B", timeout)
        self._logger.debug(f"cracker_spi_timeout payload: {payload.hex()}")
        return self.send_with_command(Commands.CRACKER_SPI_TIMEOUT, payload=payload)

    def cracker_spi_data(self, expect_len: int, data: bytes):
        payload = struct.pack(">I", expect_len)
        payload += data
        self._logger.debug(f"cracker_spi_data payload: {payload.hex()}")
        return self.send_with_command(Commands.CRACKER_SPI_DATA, payload=payload)

    def cracker_i2c_freq(self, freq: int):
        payload = struct.pack(">B", freq)
        self._logger.debug(f"cracker_i2c_freq payload: {payload.hex()}")
        return self.send_with_command(Commands.CRACKER_I2C_FREQ, payload=payload)

    def cracker_i2c_timeout(self, timeout: int):
        payload = struct.pack(">B", timeout)
        self._logger.debug(f"cracker_i2c_timeout payload: {payload.hex()}")
        return self.send_with_command(Commands.CRACKER_I2C_TIMEOUT, payload=payload)

    def cracker_i2c_data(self, expect_len: int, data: bytes):
        payload = struct.pack(">I", expect_len)
        payload += data
        self._logger.debug(f"cracker_i2c_data payload: {payload.hex()}")
        return self.send_with_command(Commands.CRACKER_I2C_DATA, payload=payload)

    def cracker_can_freq(self, freq: int):
        payload = struct.pack(">B", freq)
        self._logger.debug(f"cracker_can_freq payload: {payload.hex()}")
        return self.send_with_command(Commands.CRACKER_CAN_FREQ, payload=payload)

    def cracker_can_timeout(self, timeout: int):
        payload = struct.pack(">B", timeout)
        self._logger.debug(f"cracker_can_timeout payload: {payload.hex()}")
        return self.send_with_command(Commands.CRACKER_CAN_TIMEOUT, payload=payload)

    def cracker_can_data(self, expect_len: int, data: bytes):
        payload = struct.pack(">I", expect_len)
        payload += data
        self._logger.debug(f"cracker_can_data payload: {payload.hex()}")
        return self.send_with_command(Commands.CRACKER_CA_DATA, payload=payload)

    def osc_force(self):
        payload = None
        self._logger.debug(f"scrat_force payload: {payload}")
        return self.send_with_command(Commands.OSC_FORCE, payload=payload)

    def osc_set_clock_base_freq_mul_div(self, mult_int: int, mult_fra: int, div: int):
        payload = struct.pack(">BHB", mult_int, mult_fra, div)
        self._logger.debug(f"osc_set_clock_base_freq_mul_div payload: {payload.hex()}")
        return self.send_with_command(Commands.OSC_CLOCK_BASE_FREQ_MUL_DIV, payload=payload)

    def osc_set_sample_divisor(self, div_int: int, div_frac: int):
        payload = struct.pack(">BH", div_int, div_frac)
        self._logger.debug(f"osc_set_sample_divisor payload: {payload.hex()}")
        return self.send_with_command(Commands.OSC_CLOCK_SAMPLE_DIVISOR, payload=payload)

    def osc_set_clock_update(self) -> tuple[int, bytes | None]:
        self._logger.debug(f"osc_set_clock_update payload: {None}")
        return self.send_with_command(Commands.OSC_CLOCK_UPDATE, payload=None)

    def osc_set_clock_simple(self, nut_clk: int, mult: int, phase: int) -> tuple[int, bytes | None]:
        if not 1 <= nut_clk <= 32:
            raise ValueError("nut_clk must be between 1 and 32")
        if nut_clk * mult > 32:
            raise ValueError("nut_clk * mult must be less than 32")
        payload = struct.pack(">BBI", nut_clk, mult, phase * 1000)
        self._logger.debug(f"osc_set_clock_simple payload: {payload.hex()}")
        return self.send_with_command(Commands.OSC_CLOCK_SIMPLE, payload=payload)

    def osc_set_sample_phase(self, phase: int):
        payload = struct.pack(">I", phase)
        self._logger.debug(f"osc_set_sample_phase payload: {payload.hex()}")
        return self.send_with_command(Commands.OSC_CLOCK_SAMPLE_PHASE, payload=payload)

    def set_clock_nut_divisor(self, div: int):
        payload = struct.pack(">B", div)
        self._logger.debug(f"set_clock_nut_divisor payload: {payload.hex()}")
        return self.send_with_command(Commands.OSC_CLOCK_NUT_DIVISOR, payload=payload)

    # def osc_set_sample_clock(self, clock: int):
    #     # payload = struct.pack(">I", clock)
    #     # self._logger.debug(f"scrat_sample_clock payload: {payload.hex()}")
    #     # return self.send_with_command(Commands.OSC_SAMPLE_CLOCK, payload=payload)
    #     ...
    #
    # def osc_set_sample_phase(self, phase: int):
    #     # payload = struct.pack(">I", phase)
    #     # self._logger.debug(f"scrat_sample_phase payload: {payload.hex()}")
    #     # return self.send_with_command(Commands.OSC_SAMPLE_PHASE, payload=payload)
    #     ...
