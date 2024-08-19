import typing

import numpy as np

from cracknuts.cracker.cracker import Cracker


class StatefulCracker(Cracker):

    def __init__(self, cracker: Cracker):
        self._cracker = cracker
        self._config: typing.Dict[str, typing.Any] = {}

    def get_config_scrat_enable_channels(self) -> typing.List[int]:
        enable_channel: dict[int, bool] = self._config.get('scart_enable_channel')
        if enable_channel is None:
            return [1]  # default 1 channel
        return [k for k, v in enable_channel.items() if v]
    
    def get_config_scrat_offset(self) -> int:
        # todo how to set offset 
        return 0
    
    def get_config_scrat_sample_count(self):
        if self._config.get('scart_sample_count') is None:
            return 512
        else:
            return self._config.get('scart_sample_count')

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

    def scrat_analog_channel_enable(self, enable: typing.Dict[int, bool]):
        # todo 同步配置信息
        self._config['scart_enable_channel'] = enable
        self._cracker.scrat_analog_channel_enable(enable)

    def scrat_analog_coupling(self, coupling: typing.Dict[int, int]):
        self._cracker.scrat_analog_coupling(coupling)

    def scrat_analog_voltage(self, channel: int, voltage: int):
        self._cracker.scrat_analog_voltage(channel, voltage)

    def scrat_analog_bias_voltage(self, channel: int, voltage: int):
        self._cracker.scrat_analog_bias_voltage(channel, voltage)

    def scrat_digital_channel_enable(self, enable: typing.Dict[int, bool]):
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
        self._config['scart_sample_len'] = length

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

    def cracker_nut_voltage(self, voltage: int):
        self._cracker.cracker_nut_voltage(voltage)

    def cracker_nut_interface(self, interface: typing.Dict[int, bool]):
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
