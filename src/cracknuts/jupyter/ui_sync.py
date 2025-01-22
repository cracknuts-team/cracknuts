# Copyright 2024 CrackNuts. All rights reserved.

from typing import Any
from collections.abc import Callable


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
        listener_dict = object.__getattribute__(self, "_listener_dict")
        widget = object.__getattribute__(self, "_widget")

        setattr(config, name, value)

        if name in listener_dict:
            setattr(widget, name, listener_dict[name](value))
        elif name in dir(widget):
            setattr(widget, name, value)

    def __getattribute__(self, name):
        if name in ("_config", "_widget", "_listener_dict", "bind"):
            return super().__getattribute__(name)
        else:
            config = super().__getattribute__("_config")
            return getattr(config, name)

    def bind(self, config_attr: str, widget_attr: str = None, formatter: Callable[[Any], Any] = None):
        def listener(v):
            self._observe = False
            self._widget.__setattr__(widget_attr, v if formatter is None else formatter(v))
            self._observe = True

        self._listener_dict[config_attr] = listener

    def __str__(self):
        return self._config.__str__()

    def __repr__(self):
        return self._config.__repr__()


def observe_interceptor(func, signal="_observe"):
    def wrapper(self, *args, **kwargs):
        if getattr(self, signal):
            return func(self, *args, **kwargs)

    return wrapper
