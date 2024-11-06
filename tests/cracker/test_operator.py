import logging

from cracknuts.cracker.operator import Operator
from cracknuts.logger import set_level

# operator = Operator('192.168.0.10', 9760)
operator = Operator('localhost', 9760)


def setup_function():
    set_level(logging.INFO, operator)
    operator.connect()


def test_get_status():
    status = operator.get_status()
    print(status)
    assert isinstance(status, bool)


def test_start_server():
    status = operator.start_server()
    print(status)
    assert isinstance(status, bool)


def test_stop_server():
    status = operator.stop_server()
    print(status)
    assert isinstance(status, bool)


def test_update_server():
    with open("D:\\work\\ahcc\\90.project\\cracknuts\\bin\\server", mode="rb") as f:
        status = operator.update_server(f.read())
        print(status)
        assert isinstance(status, bool)


def test_update_bitstream():
    with open("D:\\project\\cracknuts_jupyter\\Nuts\.bin\\bitstream-cracker_s1_v0.2-0.0.2.bit.bin", mode="rb") as f:
        status = operator.update_bitstream(f.read())
        print(status)
        assert isinstance(status, bool)


def test_get_model():
    hardware_model = operator.get_hardware_model()
    print(hardware_model)
    assert isinstance(hardware_model, str)


def test_get_sn():
    sn = operator.get_sn()
    print(sn)
    assert isinstance(sn, str)


def test_get_ip():
    ip = operator.get_ip()
    print(ip)
    assert isinstance(ip, tuple)


def test_set_ip():
    success = operator.set_ip("192.168.0.10", "255.255.255.0", "192.168.0.1")
    print(success)
    assert isinstance(success, bool)
