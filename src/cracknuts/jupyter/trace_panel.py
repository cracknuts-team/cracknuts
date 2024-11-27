# Copyright 2024 CrackNuts. All rights reserved.

import pathlib
import threading
import time
import typing

import numpy as np
import traitlets
from cracknuts.acquisition.acquisition import Acquisition

from cracknuts.jupyter.panel import MsgHandlerPanelWidget


class TraceMonitorPanelWidget(MsgHandlerPanelWidget):
    _esm = pathlib.Path(__file__).parent / "static" / "TraceMonitorPanelWidget.js"
    _css = ""

    series_data = traitlets.Dict({1: [0 for _ in range(1000)]}).tag(sync=True)

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
