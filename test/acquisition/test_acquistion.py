import logging
import time

from nutcracker import logger
from nutcracker.acquisition.acquisition import Acquisition
from nutcracker.cracker.basic_cracker import BasicCracker

cracker = BasicCracker()
cracker.set_addr('192.168.0.10', 8080)
cracker.connect()

acq = Acquisition(cracker)


def setup_functions():
    logger.set_level(logging.DEBUG, acq)
    logger.set_level(logging.DEBUG, cracker)


def test_acquisition_test_mode():
    # acq.on_wave_loaded(lambda waves: print(waves.shape))
    acq.test()
    time.sleep(100000)
    # print('acq', acq.get_last_wave().shape)
    acq.stop()


if __name__ == '__main__':
    setup_functions()
    test_acquisition_test_mode()
