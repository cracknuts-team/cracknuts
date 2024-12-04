# Copyright 2024 CrackNuts. All rights reserved.

__version__ = "0.3.0"

from collections.abc import Callable

from cracknuts.acquisition import Acquisition
from cracknuts.cracker.basic_cracker import CrackerS1
from cracknuts.cracker.cracker import Cracker
from cracknuts.cracker.stateful_cracker import StatefulCracker
from cracknuts.jupyter import (
    display_cracknuts_panel,
    display_acquisition_panel,
    display_cracker_panel,
    display_trace_monitor_panel,
)

try:
    from IPython.display import display
except ImportError:
    display = None


def version():
    return __version__


def new_cracker(address: tuple | str | None = None, module: type | None = None):
    return _Cracker(address, module)


def new_acquisition(
    cracker: Cracker, init: Callable[[Cracker], None] | None = None, do: Callable[[Cracker], None] | None = None
) -> Acquisition:
    return _Acquisition(cracker, init, do)


def new_trace_monitor(acq: Acquisition):
    return display_trace_monitor_panel(acq)


def new_cracknuts(acq: Acquisition):
    return _CrackNuts(acq)


class _Cracker(StatefulCracker):
    def __init__(self, address: tuple | str | None = None, module: type | None = None):
        if module is None:
            module = CrackerS1
        super().__init__(module(address))

    def __getattribute__(self, name):
        if name in ["_ipython_display_"]:
            return object.__getattribute__(self, name)
        else:
            return super().__getattribute__(name)

    if display is not None:

        def _ipython_display_(self):
            display(display_cracker_panel(self))


class _Acquisition(Acquisition):
    def __init__(self, cracker: Cracker, init: Callable[[Cracker], None], do: Callable[[Cracker], None]):
        if not isinstance(cracker, StatefulCracker):
            cracker = StatefulCracker(cracker)
        super().__init__(cracker)
        self._init = init
        self._do = do

    def init(self):
        if self._init is not None:
            return self._init()

    def do(self):
        if self._do is not None:
            return self._do(self.cracker)

    if display is not None:

        def _ipython_display_(self):
            display(display_acquisition_panel(self))


class _CrackNuts:
    def __init__(self, acq: Acquisition):
        self._acq = acq

    if display is not None:

        def _ipython_display_(self):
            display(display_cracknuts_panel(self._acq))
