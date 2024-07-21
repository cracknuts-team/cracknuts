"""
Basic device
"""
import struct
import typing

from crackernut.cracker import protocol
from crackernut.cracker.abs_cracker import AbsCracker, Commands
import crackernut.logger as logger


class BasicCracker(AbsCracker):

    def __init__(self, server_address):
        super().__init__(server_address)
        self._command_get_id = 1
        self._command_get_name = 2
        self.__logger = logger.get_logger(BasicCracker.__module__)

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
        self._logger.debug('Scrat analog_chanel_enable payload: %s', format(payload, '08b'))

        return self.send_with_command(Commands.SCRAT_ANALOG_CHANNEL_ENABLE, payload.to_bytes(1, byteorder='big'))

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
        self._logger.debug('scrat_analog_coupling payload: %s', format(payload, '08b'))

        return self.send_with_command(Commands.SCRAT_ANALOG_COUPLING, struct.pack('>I', payload))

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

