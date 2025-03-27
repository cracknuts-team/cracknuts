# Copyright 2024 CrackNuts. All rights reserved.

from typing import Any
from cracknuts import logger


class ConfigProxy:
    def __init__(self, config: Any, widget: Any):
        self._config = config
        self._widget = widget
        self._logger = logger.get_logger(self)

    def __setattr__(self, name, value):
        if name in ("_config", "_widget"):
            object.__setattr__(self, name, value)
            return
        config = object.__getattribute__(self, "_config")
        widget = object.__getattribute__(self, "_widget")

        setattr(config, name, value)

        if name in dir(widget):
            setattr(widget, name, value)
        else:
            self._logger.error(f"Failed to sync configuration to widget: the widget has no attribute named '{name}'.")

    def __getattribute__(self, name):
        if name in ("_config", "_widget", "_logger"):
            return super().__getattribute__(name)
        else:
            config = super().__getattribute__("_config")
            return getattr(config, name)

    def __str__(self):
        return self._config.__str__()

    def __repr__(self):
        return self._config.__repr__()


_logger = logger.get_logger("observe_interceptor")


def observe_interceptor(func, signal="_observe"):
    def wrapper(self, *args, **kwargs):
        _logger.error(f"observe_interceptor is exec  {func}.... {getattr(self, signal)}")
        if getattr(self, signal):
            return func(self, *args, **kwargs)

    return wrapper
