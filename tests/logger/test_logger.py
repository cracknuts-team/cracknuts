import logging

from cracknuts import logger


def test_get_logger():
    import cracknuts
    from cracknuts.logger import default_logger, get_logger
    print(',,,,,,',default_logger().name)
    assert default_logger().name == 'cracknuts'
    assert get_logger("test_get_logger").name == "test_get_logger"
    assert get_logger(cracknuts.logger).name == 'cracknuts.logger'

    class LoggerTest:
        def __init__(self):
            ...

    assert get_logger(LoggerTest).name == 'test_logger.LoggerTest'


def test_logger_print():
    _logger = logger.get_logger("test_logger_print", level=logging.DEBUG)
    _logger.setLevel(logging.WARNING)
    _logger.error("test %s", (1,2))
