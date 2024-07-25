"""
Basic device
"""
import struct
import typing

from nutcracker.cracker import protocol
from nutcracker.cracker.abs_cracker import AbsCracker, Commands
import nutcracker.logger as logger


class BasicCracker(AbsCracker):

    def get_id(self):
        return self.send_and_receive(protocol.build_send_message(Commands.GET_ID)).decode('ascii')

    def get_name(self):
        return self.send_and_receive(protocol.build_send_message(Commands.GET_NAME)).decode('ascii')

    def scrat_analog_channel_enable(self, enable: typing.Dict[int, bool]):
        payload = 0
        if enable[0]:
            payload |= 1
        if enable[1]:
            payload |= 1 << 1
        if enable[2]:
            payload |= 1 << 2
        if enable[3]:
            payload |= 1 << 3
        if enable[4]:
            payload |= 1 << 4
        if enable[5]:
            payload |= 1 << 5
        if enable[6]:
            payload |= 1 << 6
        if enable[7]:
            payload |= 1 << 7
        if enable[8]:
            payload |= 1 << 8
        payload = struct.pack('>I', payload)
        self._logger.debug('Scrat analog_chanel_enable payload: %s', payload.hex())
        return self.send_with_command(Commands.SCRAT_ANALOG_CHANNEL_ENABLE, payload)

    def scrat_analog_coupling(self, coupling: typing.Dict[int, int]):
        payload = 0
        if coupling[0]:
            payload |= 1
        if coupling[1]:
            payload |= 1 << 1
        if coupling[2]:
            payload |= 1 << 2
        if coupling[3]:
            payload |= 1 << 3
        if coupling[4]:
            payload |= 1 << 4
        if coupling[5]:
            payload |= 1 << 5
        if coupling[6]:
            payload |= 1 << 6
        if coupling[7]:
            payload |= 1 << 7
        if coupling[8]:
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

    def scrat_analog_gain(self):
        super().scrat_analog_gain()

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
        super().cracker_nut_timeout(timeout)

