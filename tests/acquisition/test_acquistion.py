import logging
import time

from cracknuts import logger
from cracknuts.acquisition.acquisition import Acquisition
from cracknuts.cracker.basic_cracker import BasicCracker
from cracknuts.cracker.mock_cracker import MockCracker
from cracknuts.cracker.stateful_cracker import StatefulCracker

cracker = MockCracker()

acq = Acquisition.builder().cracker(StatefulCracker(cracker)).init(lambda _: None).do(lambda _:None).build()


def setup_functions():
    logger.set_level(logging.DEBUG, acq)
    logger.set_level(logging.DEBUG, cracker)


def test_acquisition_test_mode():
    # acq.on_wave_loaded(lambda waves: print(waves.shape))
    acq.run(1000)
    time.sleep(100000)
    # print('acq', acq.get_last_wave().shape)
    acq.stop()


if __name__ == '__main__':
    setup_functions()
    test_acquisition_test_mode()
