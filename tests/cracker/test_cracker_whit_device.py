import pytest

from cracknuts import CrackerS1
from cracknuts import logger


@pytest.fixture(scope='module')
def cracker_s1():
    device = CrackerS1(address=('192.168.0.10', 9761))
    logger.set_level("debug", device)
    device.connect(update_bin=True)
    yield device
    device.disconnect()


def test_get_current_config(cracker_s1):
    print(cracker_s1.get_id())
    print(cracker_s1.get_current_config())