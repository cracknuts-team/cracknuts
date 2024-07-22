import logging

from nutcracker.cracker.basic_cracker import BasicCracker
from nutcracker.logger import set_level

basic_device = BasicCracker(server_address=('192.168.0.10', 8080))


def setup_function():
    set_level(logging.DEBUG, basic_device)
    basic_device.connect()


def test_echo():
    assert basic_device.echo('11223344') == '11223344'


def test_send_with_command():
    assert basic_device.send_with_command(0x01, '11223344').hex() == '11223344'


def test_get_id():
    assert basic_device.get_id() is not None


def test_get_name():
    assert basic_device.get_name() is not None


def test_cracker_nut_voltage():
    assert basic_device.cracker_nut_voltage(1) is None


def test_cracker_nut_interface():
    assert basic_device.cracker_nut_interface({0: True}) is None


def test_multiple_echo():
    print('====', basic_device.echo('11223344'))
    print('++++', basic_device.echo('556677'))
    basic_device.disconnect()


def test_scrat_analog_gain():
    assert basic_device.scrat_analog_voltage(1, 12) is None


if __name__ == '__main__':
    setup_function()
    test_cracker_nut_interface()
