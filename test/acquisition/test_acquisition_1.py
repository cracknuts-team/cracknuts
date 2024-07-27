import logging
import time

from nutcracker import logger
from nutcracker.acquisition.acquisition import Acquisition
from nutcracker.cracker.basic_cracker import BasicCracker


class MyAcquisition(Acquisition):
    def init(self):
        self._logger.debug('Set voltage...')
        self._cracker.cracker_nut_voltage(3300)
        time.sleep(1)
        self._logger.debug('Set enable...')
        self._cracker.cracker_nut_enable(1)
        time.sleep(2)
        self._logger.debug('Set key...')
        set_key = '01 00 00 00 00 00 00 10 00 11 22 33 44 55 66 77 88 99 aa bb cc dd ee ff'
        set_key = set_key.replace(' ', '')
        set_key = bytes.fromhex(set_key)
        self._cracker.cracker_serial_data(len(set_key), set_key)

    def do(self):
        self._logger.debug('Set encrypt...')
        d = '01 02 00 00 00 00 00 10 00 11 22 33 44 55 66 77 88 99 aa bb cc dd ee ff'
        d = d.replace(' ', '')
        d = bytes.fromhex(d)
        self._cracker.cracker_serial_data(len(d), d)


if __name__ == '__main__':
    cracker = BasicCracker()
    logger.set_level(logging.DEBUG, cracker)
    cracker.set_addr('192.168.0.10', 8080)
    cracker.connect()

    acq = MyAcquisition(cracker)
    logger.set_level(logging.DEBUG, acq)

    acq.run_sync(1000)

