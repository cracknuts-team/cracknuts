import logging
import time

from nutcracker import logger
from nutcracker.acquisition.acquisition import Acquisition

acq = Acquisition(None)


def setup_functions():
    logger.set_level(logging.INFO, acq)


def test_acquisition_test_mode():
    acq.on_wave_loaded(lambda waves: print(waves.shape))
    acq.test()
    time.sleep(1)
    print('acq', acq.get_last_wave().shape)
    acq.stop()


if __name__ == '__main__':
    setup_functions()
    test_acquisition_test_mode()
