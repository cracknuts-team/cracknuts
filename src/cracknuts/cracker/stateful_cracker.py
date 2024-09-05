import numpy as np

from cracknuts.cracker.cracker import Cracker, Config


class StatefulCracker(Cracker):
    def __init__(self, cracker: Cracker):
        self._cracker = cracker
        self._config: Config = self._cracker.get_default_config()

    def get_current_config(self) -> Config:
        return self._config

    def sync_config_to_cracker(self):
        """
        Sync config to cracker.
        To prevent configuration inconsistencies between the host and the device,
        so all configuration information needs to be written to the device.
        User should call this function before get data from device.
        """
        self._cracker.cracker_nut_voltage(self._config.cracker_nut_voltage)
        self._cracker.cracker_nut_clock(self._config.cracker_nut_clock)
        self._cracker.cracker_nut_enable(self._config.cracker_nut_enable)

        self._cracker.scrat_analog_channel_enable(self._config.scrat_analog_channel_enable)
        # todo need complete...

    def set_addr(self, ip, port) -> None:
        self._cracker.set_addr(ip, port)

    def set_uri(self, uri: str) -> None:
        self._cracker.set_uri(uri)

    def get_uri(self):
        self._cracker.get_uri()

    def connect(self):
        self._cracker.connect()

    def disconnect(self):
        self._cracker.disconnect()

    def reconnect(self):
        self._cracker.reconnect()

    def get_connection_status(self) -> bool:
        return self._cracker.get_connection_status()

    def send_and_receive(self, message) -> None | bytes:
        return self._cracker.send_and_receive(message)

    def send_with_command(self, command: int | bytes, payload: str | bytes = None):
        self._cracker.send_with_command(command, payload)

    def echo(self, payload: str) -> str:
        return self._cracker.echo(payload)

    def echo_hex(self, payload: str) -> str:
        return self._cracker.echo_hex(payload)

    def get_id(self) -> str:
        return self._cracker.get_id()

    def get_name(self) -> str:
        return self._cracker.get_name()

    def scrat_analog_channel_enable(self, enable: dict[int, bool]):
        self._cracker.scrat_analog_channel_enable(enable)
        self._config.scrat_analog_channel_enable = enable

    def scrat_analog_coupling(self, coupling: dict[int, int]):
        self._cracker.scrat_analog_coupling(coupling)

    def scrat_analog_voltage(self, channel: int, voltage: int):
        self._cracker.scrat_analog_voltage(channel, voltage)

    def scrat_analog_bias_voltage(self, channel: int, voltage: int):
        self._cracker.scrat_analog_bias_voltage(channel, voltage)

    def scrat_digital_channel_enable(self, enable: dict[int, bool]):
        self._cracker.scrat_digital_channel_enable(enable)

    def scrat_digital_voltage(self, voltage: int):
        self._cracker.scrat_digital_voltage(voltage)

    def scrat_trigger_mode(self, source: int, stop: int):
        self._cracker.scrat_trigger_mode(source, stop)

    def scrat_analog_trigger_source(self, channel: int):
        self._cracker.scrat_analog_trigger_source(channel)

    def scrat_digital_trigger_source(self, channel: int):
        self._cracker.scrat_digital_trigger_source(channel)

    def scrat_analog_trigger_voltage(self, voltage: int):
        self._cracker.scrat_analog_trigger_voltage(voltage)

    def scrat_trigger_delay(self, delay: int):
        self._cracker.scrat_trigger_delay(delay)

    def scrat_sample_len(self, length: int):
        self._cracker.scrat_sample_len(length)
        self._config.scrat_sample_len = length

    def scrat_arm(self):
        self._cracker.scrat_arm()

    def scrat_is_triggered(self):
        return self._cracker.scrat_is_triggered()

    def scrat_get_analog_wave(self, channel: int, offset: int, sample_count: int) -> np.ndarray:
        return self._cracker.scrat_get_analog_wave(channel, offset, sample_count)

    def scrat_get_digital_wave(self, channel: int, offset: int, sample_count: int):
        self._cracker.scrat_get_digital_wave(channel, offset, sample_count)

    def scrat_analog_gain(self, gain: int):
        self._cracker.scrat_analog_gain(gain)

    def cracker_nut_enable(self, enable: int):
        self._cracker.cracker_nut_enable(enable)
        self._config.cracker_nut_enable = enable

    def cracker_nut_voltage(self, voltage: int):
        self._cracker.cracker_nut_voltage(voltage)
        self._config.cracker_nut_voltage = voltage

    def cracker_nut_clock(self, clock: int):
        self._cracker.cracker_nut_clock(clock)
        self._config.cracker_nut_clock = clock

    def cracker_nut_interface(self, interface: dict[int, bool]):
        self._cracker.cracker_nut_interface(interface)

    def cracker_nut_timeout(self, timeout: int):
        self._cracker.cracker_nut_timeout(timeout)

    def cracker_serial_baud(self, baud: int):
        self._cracker.cracker_serial_baud(baud)

    def cracker_serial_width(self, width: int):
        self._cracker.cracker_serial_width(width)

    def cracker_serial_stop(self, stop: int):
        self._cracker.cracker_serial_stop(stop)

    def cracker_serial_odd_eve(self, odd_eve: int):
        self._cracker.cracker_serial_odd_eve(odd_eve)

    def cracker_serial_data(self, expect_len: int, data: bytes):
        self._cracker.cracker_serial_data(expect_len, data)

    def cracker_spi_cpol(self, cpol: int):
        self._cracker.cracker_spi_cpol(cpol)

    def cracker_spi_cpha(self, cpha: int):
        self._cracker.cracker_spi_cpha(cpha)

    def cracker_spi_data_len(self, cpha: int):
        self._cracker.cracker_spi_data_len(cpha)

    def cracker_spi_freq(self, freq: int):
        self._cracker.cracker_spi_freq(freq)

    def cracker_spi_timeout(self, timeout: int):
        self._cracker.cracker_spi_timeout(timeout)

    def cracker_spi_data(self, expect_len: int, data: bytes):
        self._cracker.cracker_spi_data(expect_len, data)

    def cracker_i2c_freq(self, freq: int):
        self._cracker.cracker_i2c_freq(freq)

    def cracker_i2c_timeout(self, timeout: int):
        self._cracker.cracker_i2c_timeout(timeout)

    def cracker_i2c_data(self, expect_len: int, data: bytes):
        self._cracker.cracker_i2c_data(expect_len, data)

    def cracker_can_freq(self, freq: int):
        self._cracker.cracker_can_freq(freq)

    def cracker_can_timeout(self, timeout: int):
        self._cracker.cracker_can_timeout(timeout)

    def cracker_can_data(self, expect_len: int, data: bytes):
        self._cracker.cracker_can_data(expect_len, data)
