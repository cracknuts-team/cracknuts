import logging

from cracknuts.cracker.basic_cracker import BasicCracker
from cracknuts.logger import set_level

basic_device = BasicCracker(server_address=('192.168.0.13', 8080))


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


def test_scrat_analog_channel_enable():
    assert basic_device.scrat_analog_channel_enable({1: True}) is None


def test_scrat_analog_coupling():
    assert basic_device.scrat_analog_coupling({1: 1}) is None


def test_scrat_analog_voltage():
    assert basic_device.scrat_analog_voltage(1, 1) is None


def test_scrat_analog_bias_voltage():
    assert basic_device.scrat_analog_bias_voltage(1, 1) is None


def test_scrat_analog_gain():
    assert basic_device.scrat_analog_gain(1) is None


def test_scrat_digital_channel_enable():
    assert basic_device.scrat_digital_channel_enable({1: True}) is None


def test_scrat_digital_voltage():
    assert basic_device.scrat_digital_voltage(1) is None


def test_scrat_trigger_mode():
    assert basic_device.scrat_trigger_mode(1, 1) is None


def test_scrat_analog_trigger_source():
    assert basic_device.scrat_analog_trigger_source(1) is None


def test_scrat_digital_trigger_source():
    assert basic_device.scrat_digital_trigger_source(1) is None


def test_scrat_analog_trigger_voltage():
    assert basic_device.scrat_analog_trigger_voltage(1) is None


def test_scrat_trigger_delay():
    assert basic_device.scrat_trigger_delay(1) is None


def test_scrat_sample_len():
    assert basic_device.scrat_sample_len(1) is None


def test_scrat_arm():
    assert basic_device.scrat_arm() is None


def test_scrat_is_triggered():
    assert basic_device.scrat_is_triggered() is None


def test_scrat_get_analog_wave():
    assert basic_device.scrat_get_analog_wave(1, 0, 100) is not None


def test_scrat_get_digital_wave():
    assert basic_device.scrat_get_digital_wave(1, 1, 1) is not None


def test_cracker_nut_enable():
    assert basic_device.cracker_nut_enable(1) is None


def test_cracker_nut_disable():
    assert basic_device.cracker_nut_enable(0) is None


def test_cracker_nut_voltage():
    assert basic_device.cracker_nut_voltage(3300) is None


def test_cracker_nut_interface():
    assert basic_device.cracker_nut_interface({0: True}) is None


def test_cracker_nut_timeout():
    assert basic_device.cracker_nut_timeout(0) is None


def test_cracker_serial_baud():
    assert basic_device.cracker_serial_baud(0) is None


def test_cracker_serial_width():
    assert basic_device.cracker_serial_width(0) is None


def test_cracker_serial_stop():
    assert basic_device.cracker_serial_stop(0) is None


def test_cracker_serial_odd_eve():
    assert basic_device.cracker_serial_odd_eve(0) is None


def test_cracker_set_key():
    d = '01 00 00 00 00 00 00 10 00 11 22 33 44 55 66 77 88 99 aa bb cc dd ee ff'
    d = d.replace(' ', '')
    d = bytes.fromhex(d)
    print(d)
    r = basic_device.cracker_serial_data(len(d), d)
    assert r is not None


def test_cracker_encrypt():
    d = '01 02 00 00 00 00 00 10 00 11 22 33 44 55 66 77 88 99 aa bb cc dd ee ff'
    d = d.replace(' ', '')
    d = bytes.fromhex(d)
    for i in range(1000):
        r = basic_device.cracker_serial_data(len(d), d)
        assert r is not None


### failed: timeout
def test_cracker_spi_cpol():
    assert basic_device.cracker_spi_cpol(1) is None


### failed: timeout
def test_cracker_spi_cpha():
    assert basic_device.cracker_spi_cpha(1) is None


### failed: timeout
def test_cracker_spi_data_len():
    assert basic_device.cracker_spi_data_len(1) is None


### failed: timeout
def test_cracker_spi_freq():
    assert basic_device.cracker_spi_freq(1) is None


### failed: timeout
def test_cracker_spi_timeout():
    assert basic_device.cracker_spi_timeout(1) is None


### failed: timeout
def test_cracker_spi_data():
    assert basic_device.cracker_spi_data(1, b'aa') is not None


### failed: timeout
def test_cracker_i2c_freq():
    assert basic_device.cracker_i2c_freq(1) is None


### failed: timeout
def test_cracker_i2c_timeout():
    assert basic_device.cracker_i2c_timeout(1) is None


### failed: timeout
def test_cracker_i2c_data():
    assert basic_device.cracker_i2c_data(1, b'bb') is not None


### failed: timeout
def test_cracker_ican_freq():
    assert basic_device.cracker_can_freq(1) is None


### failed: timeout
def test_cracker_can_timeout():
    assert basic_device.cracker_can_timeout(1) is None


### failed: timeout
def test_cracker_ican_data():
    assert basic_device.cracker_can_data(1, b'bb') is not None


def test_cracker_scrat_is_triggered():
    assert basic_device.scrat_is_triggered() is None


def test_multiple_echo():
    print(basic_device.get_id())
    print(basic_device.get_name())
    basic_device.disconnect()


if __name__ == '__main__':
    setup_function()
    # test_cracker_nut_interface()
    test_cracker_nut_enable()
    # test_cracker_nut_voltage()