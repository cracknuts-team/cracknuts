from nutcracker.cracker.basic_cracker import BasicCracker


def test_echo():
    basic_device = BasicCracker(server_address=('127.0.0.1', 12345))
    basic_device.connect()
    assert basic_device.echo('11223344') == '11223344'


def test_send_with_command():
    basic_device = BasicCracker(server_address=('127.0.0.1', 12345))
    basic_device.connect()
    assert basic_device.send_with_command(0x01, '11223344').hex() == '11223344'


def test_multiple_echo():
    basic_device = BasicCracker(server_address=('127.0.0.1', 12345))
    basic_device.connect()
    print('====', basic_device.echo('11223344'))
    print('++++', basic_device.echo('556677'))
    basic_device.disconnect()


def test_scrat_analog_gain():
    basic_device = BasicCracker(server_address=('127.0.0.1', 12345))
    basic_device.connect()
    basic_device.scrat_analog_voltage(1, 12)
