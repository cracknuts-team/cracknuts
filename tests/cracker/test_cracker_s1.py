import logging
import struct
import threading
import time

import pytest

import cracknuts.mock as mock
from cracknuts.cracker.cracker_s1 import CrackerS1
from cracknuts.cracker.protocol import Command

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


def get_result_by_command(command):
    _, r = device.send_with_command(0xFFFF, payload=struct.pack('>I', command))
    return r


def setup_function(mock_cracker):
    # set_level(logging.INFO, device)
    device.connect(update_bin=False)


def test_nut_voltage(mock_cracker):
    s, _ = device.nut_voltage("3.3")
    assert s == 0 and device.get_current_config().nut_voltage == 3.3
    assert get_result_by_command(Command.NUT_VOLTAGE) == struct.pack('>I', 3300)

    s, _ = device.nut_voltage("3.4v")
    assert s == 0 and device.get_current_config().nut_voltage == 3.4
    assert get_result_by_command(Command.NUT_VOLTAGE) == struct.pack('>I', 3400)

    s, _ = device.nut_voltage("3500mV")
    assert s == 0 and device.get_current_config().nut_voltage == 3.5
    assert get_result_by_command(Command.NUT_VOLTAGE) == struct.pack('>I', 3500)

    s, _ = device.nut_voltage("3.6")
    assert s == 0 and device.get_current_config().nut_voltage == 3.6
    assert get_result_by_command(Command.NUT_VOLTAGE) == struct.pack('>I', 3600)
