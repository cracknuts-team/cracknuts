# Copyright 2024 CrackNuts. All rights reserved.

"""
这是一个示例模块，展示了如何编写模块级别的文档字符串。

这个模块提供了几个函数，用于处理文件和目录的操作。它展示了如何使用Python的标准库来完成常见的文件系统任务。

Functions:
- list_files(directory): 列出指定目录下的所有文件。
- create_directory(path): 创建一个新的目录。
- delete_directory(path): 删除一个目录及其内容。

Dependencies:
- os
- sys

Example Usage:
>>> import mymodule
>>> files = mymodule.list_files('/path/to/directory')
>>> print(files)
['file1.txt', 'file2.txt']
"""

import logging
from types import ModuleType

_LOG_LEVEL = logging.WARNING
_LOG_FORMATTER = logging.Formatter("[%(levelname)s] %(asctime)s %(module)s.%(funcName)s:%(lineno)d %(message)s")
_LOGGERS: dict[str, logging.Logger] = {}


def set_level(
    level: str | int = logging.WARNING,
    logger: str | type | ModuleType | object | None = None,
) -> None:
    """
    Set logging level.
    :param level: the logging level to set.
    :param logger: the logger to use.
    """
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
