# Copyright 2024 CrackNuts. All rights reserved.

from enum import Enum
from typing import Any
from cracknuts import logger


class ConfigProxy:
    def __init__(self, config: Any, widget: Any):
        self._config = config
        self._widget = widget
        self._logger = logger.get_logger(self)

    def __setattr__(self, name, value):
        if name.startswith("_"):
            object.__setattr__(self, name, value)
            return
        config = object.__getattribute__(self, "_config")
        widget = object.__getattribute__(self, "_widget")

        setattr(config, name, value)

        if name in dir(widget):
            if isinstance(value, Enum):
                value = value.value
            if name == "nut_i2c_dev_addr":
                value = str(value)
            widget.observe = False
            setattr(widget, name, value)
            widget.observe = True
        else:
            self._logger.warning(f"Failed to sync configuration to widget: the widget has no attribute named '{name}'.")

    def __getattribute__(self, name):
        if name.startswith("_"):
            return super().__getattribute__(name)
        else:
            config = super().__getattribute__("_config")
            return getattr(config, name)

    def __str__(self):
        return self._config.__str__()

    def __repr__(self):
        return self._config.__repr__()


def observe_interceptor(func, signal="observe"):
    def wrapper(self, *args, **kwargs):
        if getattr(self, signal):
            return func(self, *args, **kwargs)

    return wrapper
