"""
Basic device
"""

from crackernut.cracker import protocol
from crackernut.cracker.abs_cracker import AbsCracker
import crackernut.logger as logger


class BasicCracker(AbsCracker):

    def __init__(self, server_address):
        super().__init__(server_address)
        self._command_get_id = 1
        self._command_get_name = 2
        self.__logger = logger.get_logger(BasicCracker.__module__)

    def get_id(self):
        return self.send_and_receive(protocol.build_send_message(self._command_get_id)).decode('ascii')

    def get_name(self):
        return self.send_and_receive(protocol.build_send_message(self._command_get_name)).decode('ascii')
