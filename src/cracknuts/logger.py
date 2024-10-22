# Copyright 2024 CrackNuts. All rights reserved.

import logging
from types import ModuleType


_LOG_LEVEL = logging.WARNING
_LOG_FORMATTER = logging.Formatter("[%(levelname)s] %(asctime)s %(module)s.%(funcName)s:%(lineno)d %(message)s")
_LOGGERS: dict[str, logging.Logger] = {}


def set_level(
    level: str | int = logging.WARNING,
    logger: str | type | ModuleType | object | None = None,
) -> None:
    global _LOG_LEVEL
    if isinstance(level, str):
        level = level.upper()
        if level == "DEBUG":
            _LOG_LEVEL = logging.DEBUG
        elif level == "INFO":
            _LOG_LEVEL = logging.INFO
        elif level == "WARN":
            _LOG_LEVEL = logging.WARNING
        elif level == "ERROR":
            _LOG_LEVEL = logging.ERROR
        elif level == "CRITICAL":
            _LOG_LEVEL = logging.CRITICAL
        else:
            raise ValueError(f"Unrecognized log level {level}.")
    elif level not in [
        logging.DEBUG,
        logging.INFO,
        logging.WARNING,
        logging.ERROR,
        logging.CRITICAL,
    ]:
        raise ValueError(f"Unrecognized log level {level}.")
    else:
        _LOG_LEVEL = level

    _logger = None

    if logger:
        if isinstance(logger, ModuleType):
            logger = logger.__name__
        elif isinstance(logger, type):
            logger = logger.__module__ + "." + logger.__name__
        elif isinstance(logger, str):
            logger = logger
        else:
            logger = logger.__class__.__module__ + "." + logger.__class__.__name__

        _logger = _LOGGERS.get(logger)

    if not _logger:
        for _logger in _LOGGERS.values():
            _logger.setLevel(_LOG_LEVEL)
    else:
        _logger.setLevel(_LOG_LEVEL)


def get_logger(name: str | type | object | ModuleType, level: int | None = None) -> logging.Logger:
    if isinstance(name, ModuleType):
        name = name.__name__
    elif isinstance(name, type):
        name = name.__module__ + "." + name.__name__
    elif isinstance(name, str):
        name = name
    else:
        name = name.__class__.__module__ + "." + name.__class__.__name__

    if name in _LOGGERS:
        return _LOGGERS[name]

    logger = logging.getLogger(name)
    if level is None:
        logger.setLevel(_LOG_LEVEL)
    else:
        logger.setLevel(level)
    stream_handler = logging.StreamHandler()
    stream_handler.setFormatter(_LOG_FORMATTER)
    logger.addHandler(stream_handler)
    _LOGGERS[name] = logger
    logger.propagate = False
    return logger


def default_logger() -> logging.Logger:
    return get_logger("cracknuts")
