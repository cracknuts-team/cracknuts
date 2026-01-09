# Copyright 2024 CrackNuts. All rights reserved.

__version__ = "0.20.0-alpha.7"

import sys

from cracknuts import logger
from cracknuts.jupyter import show_panel
from cracknuts.cracker import cracker_s1, cracker_g1
from cracknuts.acquisition import simple_acq, simple_glitch_acq


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
    "cracker_s1",
    "cracker_g1",
    "simple_acq",
    "simple_glitch_acq",
    "show_panel",
    "version",
]
