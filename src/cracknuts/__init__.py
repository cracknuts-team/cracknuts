# Copyright 2024 CrackNuts. All rights reserved.

__version__ = "0.5.1"

import sys
import typing
from collections.abc import Callable

from cracknuts.acquisition import Acquisition
from cracknuts.cracker.cracker import CommonCracker, CommonConfig
from cracknuts.cracker.cracker_s1 import CrackerS1
from cracknuts import jupyter

try:
    from IPython.display import display

    if "ipykernel" not in sys.modules:
        display = None
except ImportError:
    display = None


T = typing.TypeVar("T", bound=CommonConfig)


def version():
    return __version__


def new_cracker(
    address: tuple | str | None = None,
    bin_server_path: str | None = None,
    bin_bitstream_path: str | None = None,
    operator_port: int = None,
    module: type[T] | None = None,
):
    kwargs = {
        "address": address,
        "bin_server_path": bin_server_path,
        "bin_bitstream_path": bin_bitstream_path,
        "operator_port": operator_port,
    }
    return _Cracker(module, **kwargs)


def new_acquisition(
    cracker: CommonCracker,
    init: Callable[[CommonCracker], None] | None = None,
    do: Callable[[CommonCracker], None] | None = None,
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


class _Cracker(CommonCracker[T]):
    def get_default_config(self) -> T:
        return self._cracker.get_default_config()

    def __init__(self, module: type[T] | None = None, **kwargs):
        if module is None:
            module = CrackerS1
        self._cracker = module()
        super().__init__(**kwargs)

    if display is not None:

        def _ipython_display_(self):
            display(jupyter.display_cracker_panel(self))


class _Acquisition(Acquisition):
    def __init__(
        self, cracker: CommonCracker, init: Callable[[CommonCracker], None], do: Callable[[CommonCracker], None]
    ):
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


class _CrackNuts:
    def __init__(self):
        self._cracker = None
        self._acquisition = None

    def cracker(self, address: tuple | str | None = None, module: type[T] | None = None) -> "_CrackNuts":
        self._cracker = _Cracker(address, module)
        return self

    def acquisition(
        self, init: Callable[[CommonCracker], None] | None = None, do: Callable[[CommonCracker], None] | None = None
    ) -> "_CrackNuts":
        self._acquisition = _Acquisition(self._cracker, init, do)
        return self
