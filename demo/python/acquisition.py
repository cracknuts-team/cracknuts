import logging
import time

from cracknuts import logger
from cracknuts.acquisition.acquisition import Acquisition, AcquisitionBuilder
from cracknuts.cracker.cracker import AbsCnpCracker
from cracknuts.cracker.basic_cracker import CrackerS1

cracker = CrackerS1()
logger.set_level(logging.DEBUG, cracker)

# 11 为效果好的板子
cracker.set_addr('192.168.0.13', 8080)
cracker.connect()


def init(c: AbsCnpCracker):
    c.nut_voltage(3300)
    time.sleep(1)
    c.nut_enable(1)
    time.sleep(2)

    # set_key = '01 00 00 00 00 00 00 10 00 11 22 33 44 55 66 77 88 99 aa bb cc dd ee ff'
    l = 6
    set_key = '02 00 00 00 00 00 00 08 88 99 AA BB CC DD EE FF'
    set_key = set_key.replace(' ', '')
    set_key = bytes.fromhex(set_key)
    c.cracker_serial_data(l, set_key)


def do(c: AbsCnpCracker):
    # enc
    # d = '01 02 00 00 00 00 00 10 00 11 22 33 44 55 66 77 88 99 aa bb cc dd ee ff'
    # l = '00 00 00 00 00 10 62 F6 79 BE 2B F0 D9 31 64 1E 03 9C A3 40 1B B2'
    # l = len(l.split(' '))
    # l = 22
    d = '02 02 00 00 00 00 00 08 88 99 AA BB CC DD EE FF'
    # l = '00 00 00 00 00 08 97 9F FF 9B 97 0C A6 A4'
    # l = len(l.split(' '))
    l = 14
    d = d.replace(' ', '')
    d = bytes.fromhex(d)
    c.cracker_serial_data(l, d)


acq = Acquisition.builder().cracker(cracker).init(init).do(do).build()

# acq.test(1000)
# acq.wait()

acq.run_sync(50000)
