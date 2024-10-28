import logging

from cracknuts.cracker.operator import Operator
from cracknuts.logger import set_level

operator = Operator('127.0.0.1', 9760)


def setup_function():
    set_level(logging.DEBUG, operator)
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
