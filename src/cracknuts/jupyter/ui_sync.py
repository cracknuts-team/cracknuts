# Copyright 2024 CrackNuts. All rights reserved.

from typing import Any


class ConfigProxy:
    def __init__(self, config: Any, widget: Any):
        self._config = config
        self._widget = widget
        self._listener_dict = {}

    def __setattr__(self, name, value):
        if name in ("_config", "_widget", "_listener_dict"):
            object.__setattr__(self, name, value)
            return
        config = object.__getattribute__(self, "_config")
        widget = object.__getattribute__(self, "_widget")

        setattr(config, name, value)

        if hasattr(type(widget), name) and isinstance(getattr(type(widget), name), property):
            prop = getattr(type(widget), name)
            if prop.fset:
                prop.fset(widget, value)
        elif name in dir(widget):
            setattr(widget, name, value)

    def __getattribute__(self, name):
        if name in ("_config", "_widget", "_listener_dict", "bind"):
            return super().__getattribute__(name)
        else:
            config = super().__getattribute__("_config")
            return getattr(config, name)

    def __str__(self):
        return self._config.__str__()

    def __repr__(self):
        return self._config.__repr__()


def observe_interceptor(func, signal="_observe"):
    def wrapper(self, *args, **kwargs):
        if getattr(self, signal):
            return func(self, *args, **kwargs)

    return wrapper
