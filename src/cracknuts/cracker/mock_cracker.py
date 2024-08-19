import typing

import numpy as np

from cracknuts.cracker.cracker import AbsCracker


class MockCracker(AbsCracker):

    def __init__(self, server_address=None):
        super().__init__(server_address)

    def connect(self):
        return self

    def get_connection_status(self) -> bool:
        return True

    def disconnect(self):
        return self

    def send_with_command(self, command: int | bytes, payload: str | bytes = None):
        ...

    def echo(self, payload: str) -> str:
        return super().echo(payload)

    def echo_hex(self, payload: str) -> str:
        return super().echo_hex(payload)

    def get_id(self) -> str:
        return '0001'

    def get_name(self) -> str:
        return 'mock cracker'

    def scrat_analog_channel_enable(self, enable: typing.Dict[int, bool]):
        pass

    def scrat_analog_coupling(self, coupling: typing.Dict[int, int]):
        pass

    def scrat_analog_voltage(self, channel: int, voltage: int):
        pass

    def scrat_analog_bias_voltage(self, channel: int, voltage: int):
        pass

    def scrat_digital_channel_enable(self, enable: typing.Dict[int, bool]):
        pass

    def scrat_digital_voltage(self, voltage: int):
        pass

    def scrat_trigger_mode(self, source: int, stop: int):
        pass

    def scrat_analog_trigger_source(self, channel: int):
        pass

    def scrat_digital_trigger_source(self, channel: int):
        pass

    def scrat_analog_trigger_voltage(self, voltage: int):
        pass

    def scrat_trigger_delay(self, delay: int):
        pass

    def scrat_sample_len(self, length: int):
        pass

    def scrat_arm(self):
        pass

    def scrat_is_triggered(self):
        return True

    def scrat_get_analog_wave(self, channel: int, offset: int, sample_count: int) -> np.ndarray:
        return np.array([np.random.randint(1, 100) for i in range(sample_count)])

    def scrat_get_digital_wave(self, channel: int, offset: int, sample_count: int):
        pass

    def scrat_analog_gain(self, gain: int):
        pass

    def cracker_nut_enable(self, enable: int):
        pass

    def cracker_nut_voltage(self, voltage: int):
        pass

    def cracker_nut_interface(self, interface: typing.Dict[int, bool]):
        pass

    def cracker_nut_timeout(self, timeout: int):
        pass

    def cracker_serial_baud(self, baud: int):
        pass

    def cracker_serial_width(self, width: int):
        pass

    def cracker_serial_stop(self, stop: int):
        pass

    def cracker_serial_odd_eve(self, odd_eve: int):
        pass

    def cracker_serial_data(self, expect_len: int, data: bytes):
        pass

    def cracker_spi_cpol(self, cpol: int):
        pass

    def cracker_spi_cpha(self, cpha: int):
        pass

    def cracker_spi_data_len(self, cpha: int):
        pass

    def cracker_spi_freq(self, freq: int):
        pass

    def cracker_spi_timeout(self, timeout: int):
        pass

    def cracker_spi_data(self, expect_len: int, data: bytes):
        pass

    def cracker_i2c_freq(self, freq: int):
        pass

    def cracker_i2c_timeout(self, timeout: int):
        pass

    def cracker_i2c_data(self, expect_len: int, data: bytes):
        pass

    def cracker_can_freq(self, freq: int):
        pass

    def cracker_can_timeout(self, timeout: int):
        pass

    def cracker_can_data(self, expect_len: int, data: bytes):
        pass
