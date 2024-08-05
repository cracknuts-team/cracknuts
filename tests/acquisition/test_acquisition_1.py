import logging
import time

from cracknuts import logger
from cracknuts.acquisition.acquisitiontemplate import AcquisitionTemplate
from cracknuts.cracker.basic_cracker import BasicCracker


class MyAcquisitionTemplate(AcquisitionTemplate):
    def init(self):
        self._logger.debug('Set voltage...')
        self.cracker.cracker_nut_voltage(3300)
        time.sleep(1)
        self._logger.debug('Set enable...')
        self.cracker.cracker_nut_enable(1)
        time.sleep(2)
        self._logger.debug('Set key...')
        # set_key = '01 00 00 00 00 00 00 10 00 11 22 33 44 55 66 77 88 99 aa bb cc dd ee ff'
        l = 6
        set_key = '02 00 00 00 00 00 00 08 88 99 AA BB CC DD EE FF'
        set_key = set_key.replace(' ', '')
        set_key = bytes.fromhex(set_key)
        self.cracker.cracker_serial_data(l, set_key)

    def do(self):
        # enc
        self._logger.debug('Set encrypt...')
        # d = '01 02 00 00 00 00 00 10 00 11 22 33 44 55 66 77 88 99 aa bb cc dd ee ff'
        # l = '00 00 00 00 00 10 62 F6 79 BE 2B F0 D9 31 64 1E 03 9C A3 40 1B B2'
        # l = len(l.split(' '))
        d = '02 02 00 00 00 00 00 08 88 99 AA BB CC DD EE FF'
        l = '00 00 00 00 00 08 97 9F FF 9B 97 0C A6 A4'
        l = len(l.split(' '))
        d = d.replace(' ', '')
        d = bytes.fromhex(d)
        self.cracker.cracker_serial_data(l, d)


if __name__ == '__main__':
    cracker = BasicCracker()
    logger.set_level(logging.WARNING, cracker)
    cracker.set_addr('192.168.0.12', 8080)
    cracker.connect()
    if cracker.get_connection_status():
        acq = MyAcquisitionTemplate(cracker)
        logger.set_level(logging.WARNING, acq)
        acq.run_sync(5000)

