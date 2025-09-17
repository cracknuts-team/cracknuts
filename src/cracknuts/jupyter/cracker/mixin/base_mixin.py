import typing
from abc import ABC, abstractmethod


class BaseMixin(ABC):
    @abstractmethod
    def reg_msg_handler(self, source, event, handler: typing.Callable[[dict[str, typing.Any]], None]): ...

    @abstractmethod
    def send(self, content, buffers=None): ...
