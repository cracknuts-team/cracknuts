# Copyright 2024 CrackNuts. All rights reserved.

import pathlib
import threading
import time
import typing

import numpy as np
import traitlets

from cracknuts.acquisition.acquisition import Acquisition
from cracknuts.jupyter.panel import MsgHandlerPanelWidget


class ScopePanelWidget(MsgHandlerPanelWidget):
    _esm = pathlib.Path(__file__).parent / "static" / "ScopePanelWidget.js"
    _css = ""

    series_data = traitlets.Dict({}).tag(sync=True)

    # custom_range_model = traitlets.Bool(False).tag(sync=True)
    custom_y_range: dict[str, tuple[int, int]] = traitlets.Dict({"1": (0, 0), "2": (0, 0)}).tag(sync=True)
    y_range: dict[int, tuple[int, int]] = traitlets.Dict({1: (None, None), 2: (None, None)}).tag(sync=True)
    combine_y_range = traitlets.Bool(False).tag(sync=True)

    monitor_status = traitlets.Bool(False).tag(sync=True)
    monitor_period = traitlets.Float(0.1).tag(sync=True)

    def __init__(self, *args: typing.Any, **kwargs: typing.Any) -> None:
        super().__init__(*args, **kwargs)

        if not hasattr(self, "acquisition"):
            self.acquisition: Acquisition | None = None
            if "acquisition" in kwargs and isinstance(kwargs["acquisition"], Acquisition):
                self.acquisition = kwargs["acquisition"]
            if self.acquisition is None:
                raise ValueError("acquisition is required")

        self._trace_update_stop_flag = True

    def update(self, series_data: dict[int, np.ndarray]) -> None:
        (
            mn1,
            mx1,
        ) = None, None
        (
            mn2,
            mx2,
        ) = None, None

        if 1 in series_data.keys():
            c1 = series_data[1]
            mn1, mx1 = np.min(c1), np.max(c1)
        if 2 in series_data.keys():
            c2 = series_data[2]
            mn2, mx2 = np.min(c2), np.max(c2)

        self.y_range = {1: (mn1, mx1), 2: (mn2, mx2)}

        self.series_data = {k: v.tolist() for k, v in series_data.items()}

    @traitlets.observe("monitor_status")
    def monitor(self, change) -> None:
        if change.get("new"):
            self.start_monitor()

    def _monitor(self) -> None:
        while self.monitor_status:
            self.update(self.acquisition.get_last_wave())
            time.sleep(self.monitor_period)

    def start_monitor(self) -> None:
        self.monitor_status = True
        threading.Thread(target=self._monitor).start()

    def stop_monitor(self) -> None:
        self.monitor_status = False
