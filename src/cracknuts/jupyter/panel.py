# Copyright 2024 CrackNuts. All rights reserved.

import typing

from anywidget import AnyWidget


class MsgHandlerPanelWidget(AnyWidget):
    def __init__(self, *args, **kwargs):
        super().__init__(**{})
        self._msg_handlers: dict[str, list[typing.Callable[[dict[str, typing.Any]], None]]] = {}
        self.on_msg(self._msg_handle)

    def _msg_handle(self, widget, content: dict[str, typing.Any], buffers):
        source = content.get("source")
        event = content.get("event")
        args: dict = content.get("args")
        key = self._get_msg_handler_key(source, event)
        if key in self._msg_handlers:
            for handler in self._msg_handlers[key]:
                handler(args)

    @staticmethod
    def _get_msg_handler_key(source, event):
        return source + "_" + event

    def reg_msg_handler(self, source, event, handler: typing.Callable[[dict[str, typing.Any]], None]):
        key = self._get_msg_handler_key(source, event)
        if key not in self._msg_handlers:
            self._msg_handlers[key] = []
        self._msg_handlers[key].append(handler)
