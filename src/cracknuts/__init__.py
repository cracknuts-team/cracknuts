# Copyright 2024 CrackNuts. All rights reserved.

__version__ = "0.7.4"

import sys
import typing
from collections.abc import Callable

from cracknuts import jupyter
from cracknuts.acquisition import Acquisition, AcquisitionBuilder
from cracknuts.cracker.cracker_basic import CrackerBasic
from cracknuts.cracker.cracker_g1 import CrackerG1
from cracknuts.cracker.cracker_s1 import CrackerS1

try:
    from IPython.display import display

    if "ipykernel" not in sys.modules:
        display = None
except ImportError:
    display = None


def version():
    return __version__


CRACKER = typing.TypeVar("CRACKER", bound=CrackerBasic)


def new_cracker(
    address: tuple | str | None = None,
    bin_server_path: str | None = None,
    bin_bitstream_path: str | None = None,
    operator_port: int = None,
    model: type[CRACKER] | str | None = None,
) -> CRACKER:
    kwargs = {
        "address": address,
        "bin_server_path": bin_server_path,
        "bin_bitstream_path": bin_bitstream_path,
        "operator_port": operator_port,
    }
    if model is None:
        model = CrackerS1
    else:
        if isinstance(model, str):
            if model.lower() == "s1":
                model = CrackerS1
            elif model.lower() == "g1":
                model = CrackerG1
            else:
                raise ValueError(f"Unknown cracker model: {model}")
    return model(**kwargs)


def new_acquisition(
    cracker: CrackerBasic,
    init: Callable[[CrackerBasic], None] | None = None,
    do: Callable[[CrackerBasic], None] | None = None,
) -> Acquisition:
    return AcquisitionBuilder().cracker(cracker).init(init).do(do).build()


if display is not None:

    def panel(acq: Acquisition):
        return jupyter.display_cracknuts_panel(acq)


if display is not None:

    def panel_cracker(cracker: CrackerBasic):
        return jupyter.display_cracker_panel(cracker)


if display is not None:

    def panel_scope(acq: Acquisition):
        return jupyter.display_scope_panel(acq)


if display is not None:

    def panel_acquisition(acq: Acquisition):
        return jupyter.display_acquisition_panel(acq)


if display is not None:

    def panel_trace():
        return jupyter.display_trace_panel()
