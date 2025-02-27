import logging
import threading
import time

import pytest

import cracknuts.mock as mock
from cracknuts.cracker.cracker_s1 import CrackerS1

device = CrackerS1(address=('localhost', 9761))


@pytest.fixture(scope='module')
def mock_cracker():
    def start_mock_cracker():
        mock.start(logging_level=logging.WARNING)
    mock_thread = threading.Thread(target=start_mock_cracker)
    mock_thread.daemon = True
    mock_thread.start()
    time.sleep(0.5)
    yield


def setup_function(mock_cracker):
    # set_level(logging.INFO, device)
    device.connect(update_bin=False)


def test_nut_voltage(mock_cracker):
    s, _ = device.nut_voltage("3.3")
    assert s == 0 and device.get_current_config().nut_voltage == 3.3
    s, _ = device.nut_voltage("3.3v")
    assert s == 0 and device.get_current_config().nut_voltage == 3.3
    s, _ = device.nut_voltage("3300mV")
    assert s == 0 and device.get_current_config().nut_voltage == 3.3
    s, _ = device.nut_voltage("3.3")
    assert s == 0 and device.get_current_config().nut_voltage == 3.3
