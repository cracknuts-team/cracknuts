# Copyright 2024 CrackNuts. All rights reserved.

__version__ = "0.20.0-beta.2"

import sys

from cracknuts import logger
from cracknuts.jupyter import show_panel
from cracknuts.cracker import new_cracker, cracker_s1, cracker_g1
from cracknuts.acquisition import simple_acq, simple_glitch_acq
from cracknuts.trace import load_trace_dataset


_logger = logger.get_logger("cracknuts")

try:
    from IPython.display import display as _ipython_display

    if "ipykernel" not in sys.modules:
        _ipython_display = None
except ImportError as e:
    _logger.error(f"ImportError: {e.args}")
    _ipython_display = None


def version():
    return __version__


__all__ = [
    "new_cracker",
    "cracker_s1",
    "cracker_g1",
    "simple_acq",
    "simple_glitch_acq",
    "show_panel",
    "load_trace_dataset",
    "version",
]
