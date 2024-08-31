import struct
import typing

import numpy as np

from cracknuts.cracker import protocol
from cracknuts.cracker.cracker import AbsCnpCracker, Commands


class DefaultConfig:
    uri: str = 'cnp://192.168.0.1:9981'
    scart_enable_channel: typing.Dict[int, bool] = {1: True, 2: False}
    scart_sample_len: int = 1024
    cracker_nut_voltage: int = 3500


class CrackerS1(AbsCnpCracker):

    def get_id(self):
        return self.send_and_receive(protocol.build_send_message(Commands.GET_ID)).decode('ascii')

    def get_name(self):
        return self.send_and_receive(protocol.build_send_message(Commands.GET_NAME)).decode('ascii')

    def scrat_analog_channel_enable(self, enable: typing.Dict[int, bool]):
        self._channel_enable = enable
        payload = 0
        if enable.get(0):
            payload |= 1
        if enable.get(1):
            payload |= 1 << 1
        if enable.get(2):
            payload |= 1 << 2
        if enable.get(3):
            payload |= 1 << 3
        if enable.get(4):
            payload |= 1 << 4
        if enable.get(5):
            payload |= 1 << 5
        if enable.get(6):
            payload |= 1 << 6
        if enable.get(7):
            payload |= 1 << 7
        if enable.get(8):
            payload |= 1 << 8
        payload = struct.pack('>I', payload)
        self._logger.debug('Scrat analog_chanel_enable payload: %s', payload.hex())
        return self.send_with_command(Commands.SCRAT_ANALOG_CHANNEL_ENABLE, payload)

    def scrat_analog_coupling(self, coupling: typing.Dict[int, int]):
        payload = 0
        if coupling.get(0):
            payload |= 1
        if coupling.get(1):
            payload |= 1 << 1
        if coupling.get(2):
            payload |= 1 << 2
        if coupling.get(3):
            payload |= 1 << 3
        if coupling.get(4):
            payload |= 1 << 4
        if coupling.get(5):
            payload |= 1 << 5
        if coupling.get(6):
            payload |= 1 << 6
        if coupling.get(7):
            payload |= 1 << 7
        if coupling.get(8):
            payload |= 1 << 8

        payload = struct.pack('>I', payload)
        self._logger.debug('scrat_analog_coupling payload: %s', payload.hex())

        return self.send_with_command(Commands.SCRAT_ANALOG_COUPLING, payload)

    def scrat_analog_voltage(self, channel: int, voltage: int):
        payload = struct.pack('>BI', channel, voltage)
        self._logger.debug('scrat_analog_coupling payload: %s', payload.hex())
        return self.send_with_command(Commands.SCRAT_ANALOG_VOLTAGE, payload)

    def scrat_analog_bias_voltage(self, channel: int, voltage: int):
        payload = struct.pack('>BI', channel, voltage)
        self._logger.debug('scrat_analog_bias_voltage payload: %s', payload.hex())
        return self.send_with_command(Commands.SCRAT_ANALOG_BIAS_VOLTAGE, payload)

    def scrat_digital_channel_enable(self, enable: typing.Dict[int, bool]):
        payload = 0
        if enable.get(0):
            payload |= 1
        if enable.get(1):
            payload |= 1 << 1
        if enable.get(2):
            payload |= 1 << 2
        if enable.get(3):
            payload |= 1 << 3
        if enable.get(4):
            payload |= 1 << 4
        if enable.get(5):
            payload |= 1 << 5
        if enable.get(6):
            payload |= 1 << 6
        if enable.get(7):
            payload |= 1 << 7
        if enable.get(8):
            payload |= 1 << 8
        payload = struct.pack('>I', payload)
        self._logger.debug('scrat_digital_channel_enable payload: %s', payload.hex())
        return self.send_with_command(Commands.SCRAT_DIGITAL_CHANNEL_ENABLE, payload)

    def scrat_digital_voltage(self, voltage: int):
        payload = struct.pack('>I', voltage)
        self._logger.debug('scrat_digital_voltage payload: %s', payload.hex())
        return self.send_with_command(Commands.SCRAT_DIGITAL_VOLTAGE, payload)

    def scrat_trigger_mode(self, source: int, stop: int):
        payload = struct.pack('>II', source, stop)
        self._logger.debug('scrat_trigger_mode payload: %s', payload.hex())
        return self.send_with_command(Commands.SCRAT_TRIGGER_MODE, payload)

    def scrat_analog_trigger_source(self, channel: int):
        payload = struct.pack('>B', channel)
        self._logger.debug('scrat_analog_trigger_source payload: %s', payload.hex())
        return self.send_with_command(Commands.SCRAT_ANALOG_TRIGGER_SOURCE, payload)

    def scrat_digital_trigger_source(self, channel: int):
        payload = struct.pack('>B', channel)
        self._logger.debug('scrat_digital_trigger_source payload: %s', payload.hex())
        return self.send_with_command(Commands.SCRAT_DIGITAL_TRIGGER_SOURCE, payload)

    def scrat_analog_trigger_voltage(self, voltage: int):
        payload = struct.pack('>I', voltage)
        self._logger.debug('scrat_analog_trigger_voltage payload: %s', payload.hex())
        return self.send_with_command(Commands.SCRAT_ANALOG_TRIGGER_VOLTAGE, payload)

    def scrat_trigger_delay(self, delay: int):
        payload = struct.pack('>I', delay)
        self._logger.debug('scrat_trigger_delay payload: %s', payload.hex())
        return self.send_with_command(Commands.SCRAT_TRIGGER_DELAY, payload)

    def scrat_sample_len(self, length: int):
        payload = struct.pack('>I', length)
        self._logger.debug('scrat_sample_len payload: %s', payload.hex())
        return self.send_with_command(Commands.SCRAT_SAMPLE_LENGTH, payload)

    def scrat_arm(self):
        payload = None
        self._logger.debug('scrat_sample_len payload: %s', payload)
        return self.send_with_command(Commands.SCRAT_ARM, payload)

    def scrat_is_triggered(self):
        payload = None
        self._logger.debug('scrat_is_triggered payload: %s', payload)
        return self.send_with_command(Commands.SCRAT_IS_TRIGGERED, payload)

    def scrat_get_analog_wave(self, channel: int, offset: int, sample_count: int):
        payload = struct.pack('>BII', channel, offset, sample_count)
        self._logger.debug('scrat_get_analog_wave payload: %s', payload.hex())
        wave_bytes = self.send_with_command(Commands.SCRAT_GET_ANALOG_WAVES, payload)
        self._logger.debug('scrat_get_analog_wave wave_bytes: %s', wave_bytes.hex())
        if wave_bytes is None:
            return np.array([[]])
        else:
            wave = struct.unpack(f'>{sample_count}H', wave_bytes)
            return np.array(wave, dtype=np.int32)

    def scrat_get_digital_wave(self, channel: int, offset: int, sample_count: int):
        payload = struct.pack('>BII', channel, offset, sample_count)
        self._logger.debug('scrat_get_digital_wave payload: %s', payload.hex())
        wave_bytes = self.send_with_command(Commands.SCRAT_GET_ANALOG_WAVES, payload)
        wave = struct.unpack(f'>{sample_count}I', wave_bytes)
        return np.array(wave, dtype=np.int32)

    def scrat_analog_gain(self, gain):
        payload = struct.pack('>B', gain)
        self._logger.debug('scrat_analog_gain payload: %s', payload.hex())
        return self.send_with_command(Commands.SCRAT_ANALOG_GAIN, payload)

    def cracker_nut_enable(self, enable: int):
        payload = struct.pack('>B', enable)
        self._logger.debug('cracker_nut_enable payload: %s', payload.hex())
        return self.send_with_command(Commands.CRACKER_NUT_ENABLE, payload)

    def cracker_nut_voltage(self, voltage):
        payload = struct.pack('>I', voltage)
        self._logger.debug('cracker_nut_voltage payload: %s', payload.hex())
        return self.send_with_command(Commands.CRACKER_NUT_VOLTAGE, payload)

    def cracker_nut_interface(self, interface: typing.Dict[int, bool]):
        payload = 0
        if interface.get(0):
            payload |= 1
        if interface.get(1):
            payload |= 1 << 1
        if interface.get(2):
            payload |= 1 << 2
        if interface.get(3):
            payload |= 1 << 3

        payload = struct.pack('>I', payload)
        self._logger.debug('cracker_nut_interface payload: %s', payload.hex())
        print(self._logger.name)
        return self.send_with_command(Commands.CRACKER_NUT_INTERFACE, payload)

    def cracker_nut_timeout(self, timeout: int):
        payload = struct.pack('>I', timeout)
        self._logger.debug('cracker_nut_timeout payload: %s', payload.hex())
        return self.send_with_command(Commands.CRACKER_NUT_TIMEOUT, payload)

    def cracker_serial_baud(self, baud: int):
        payload = struct.pack('>I', baud)
        self._logger.debug('cracker_serial_baud payload: %s', payload.hex())
        return self.send_with_command(Commands.CRACKER_SERIAL_BAUD, payload)

    def cracker_serial_width(self, width: int):
        payload = struct.pack('>B', width)
        self._logger.debug('cracker_serial_width payload: %s', payload.hex())
        return self.send_with_command(Commands.CRACKER_SERIAL_WIDTH, payload)

    def cracker_serial_stop(self, stop: int):
        payload = struct.pack('>B', stop)
        self._logger.debug('cracker_serial_stop payload: %s', payload.hex())
        return self.send_with_command(Commands.CRACKER_SERIAL_STOP, payload)

    def cracker_serial_odd_eve(self, odd_eve: int):
        payload = struct.pack('>B', odd_eve)
        self._logger.debug('cracker_serial_odd_eve payload: %s', payload.hex())
        return self.send_with_command(Commands.CRACKER_SERIAL_ODD_EVE, payload)

    def cracker_serial_data(self, expect_len: int, data: bytes):
        payload = struct.pack('>I', expect_len)
        payload += data
        self._logger.debug('cracker_serial_data payload: %s', payload.hex())
        return self.send_with_command(Commands.CRACKER_SERIAL_DATA, payload)

    def cracker_spi_cpol(self, cpol: int):
        payload = struct.pack('>B', cpol)
        self._logger.debug('cracker_spi_cpol payload: %s', payload.hex())
        return self.send_with_command(Commands.CRACKER_SPI_CPOL, payload)

    def cracker_spi_cpha(self, cpha: int):
        payload = struct.pack('>B', cpha)
        self._logger.debug('cracker_spi_cpha payload: %s', payload.hex())
        return self.send_with_command(Commands.CRACKER_SPI_CPHA, payload)

    def cracker_spi_data_len(self, length: int):
        payload = struct.pack('>B', length)
        self._logger.debug('cracker_spi_data_len payload: %s', payload.hex())
        return self.send_with_command(Commands.CRACKER_SPI_DATA_LEN, payload)

    def cracker_spi_freq(self, freq: int):
        payload = struct.pack('>B', freq)
        self._logger.debug('cracker_spi_freq payload: %s', payload.hex())
        return self.send_with_command(Commands.CRACKER_SPI_FREQ, payload)

    def cracker_spi_timeout(self, timeout: int):
        payload = struct.pack('>B', timeout)
        self._logger.debug('cracker_spi_timeout payload: %s', payload.hex())
        return self.send_with_command(Commands.CRACKER_SPI_TIMEOUT, payload)

    def cracker_spi_data(self, expect_len: int, data: bytes):
        payload = struct.pack('>I', expect_len)
        payload += data
        self._logger.debug('cracker_spi_data payload: %s', payload.hex())
        return self.send_with_command(Commands.CRACKER_SPI_DATA, payload)

    def cracker_i2c_freq(self, freq: int):
        payload = struct.pack('>B', freq)
        self._logger.debug('cracker_i2c_freq payload: %s', payload.hex())
        return self.send_with_command(Commands.CRACKER_I2C_FREQ, payload)

    def cracker_i2c_timeout(self, timeout: int):
        payload = struct.pack('>B', timeout)
        self._logger.debug('cracker_i2c_timeout payload: %s', payload.hex())
        return self.send_with_command(Commands.CRACKER_I2C_TIMEOUT, payload)

    def cracker_i2c_data(self, expect_len: int, data: bytes):
        payload = struct.pack('>I', expect_len)
        payload += data
        self._logger.debug('cracker_i2c_data payload: %s', payload.hex())
        return self.send_with_command(Commands.CRACKER_I2C_DATA, payload)

    def cracker_can_freq(self, freq: int):
        payload = struct.pack('>B', freq)
        self._logger.debug('cracker_can_freq payload: %s', payload.hex())
        return self.send_with_command(Commands.CRACKER_CAN_FREQ, payload)

    def cracker_can_timeout(self, timeout: int):
        payload = struct.pack('>B', timeout)
        self._logger.debug('cracker_can_timeout payload: %s', payload.hex())
        return self.send_with_command(Commands.CRACKER_CAN_TIMEOUT, payload)

    def cracker_can_data(self, expect_len: int, data: bytes):
        payload = struct.pack('>I', expect_len)
        payload += data
        self._logger.debug('cracker_can_data payload: %s', payload.hex())
        return self.send_with_command(Commands.CRACKER_CA_DATA, payload)
