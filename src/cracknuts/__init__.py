# Copyright 2024 CrackNuts. All rights reserved.

__version__ = "0.3.1"

from collections.abc import Callable

from cracknuts.acquisition import Acquisition
from cracknuts.cracker.basic_cracker import CrackerS1
from cracknuts.cracker.cracker import Cracker
from cracknuts.cracker.stateful_cracker import StatefulCracker
from cracknuts import jupyter

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


if display is not None:

    def monitor_panel(acq: Acquisition):
        return jupyter.display_trace_monitor_panel(acq)


if display is not None:

    def panel(acq: Acquisition):
        return jupyter.display_cracknuts_panel(acq)


if display is not None:

    def trace_analysis_panel():
        return jupyter.display_trace_analysis_panel()


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
            display(jupyter.display_cracker_panel(self))


class _Acquisition(Acquisition):
    def __init__(self, cracker: Cracker, init: Callable[[Cracker], None], do: Callable[[Cracker], None]):
        if not isinstance(cracker, StatefulCracker):
            cracker = StatefulCracker(cracker)
        super().__init__(cracker)
        self._init = init
        self._do = do

    def init(self):
        if self._init is not None:
            return self._init(self.cracker)

    def do(self):
        if self._do is not None:
            return self._do(self.cracker)

    if display is not None:

        def _ipython_display_(self):
            display(jupyter.display_acquisition_panel(self))
