import logging
import time

from cracknuts import logger
from cracknuts.acquisition.acquisition import Acquisition
from cracknuts.mock.mock_cracker import MockCracker
from cracknuts.cracker.stateful_cracker import StatefulCracker

cracker = MockCracker()

acq = Acquisition.builder().cracker(StatefulCracker(cracker)).init(lambda _: None).do(lambda _: None).build()


def setup_functions():
    logger.set_level(logging.DEBUG, acq)
    logger.set_level(logging.DEBUG, cracker)


def test_acquisition_run_mode():
    trace_count = 0

    def count_plus(_):
        nonlocal trace_count
        trace_count += 1

    acq.on_wave_loaded(count_plus)
    acq.run(100)
    while acq.get_status() != Acquisition.STATUS_STOPPED:
        time.sleep(0.1)

    assert trace_count == 100


if __name__ == '__main__':
    setup_functions()
    test_acquisition_run_mode()
