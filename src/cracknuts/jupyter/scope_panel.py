# Copyright 2024 CrackNuts. All rights reserved.

import pathlib
import threading
import time
import typing

import numpy as np
import traitlets
import cracknuts.logger as logger
from cracknuts.acquisition.acquisition import Acquisition
from cracknuts.jupyter.panel import MsgHandlerPanelWidget
from cracknuts.scope.scope_acquisition import ScopeAcquisition


class ScopePanelWidget(MsgHandlerPanelWidget):
    _esm = pathlib.Path(__file__).parent / "static" / "ScopePanelWidget.js"
    _css = ""

    series_data = traitlets.Dict({}).tag(sync=True)

    custom_y_range: dict[str, tuple[int, int]] = traitlets.Dict({"1": (0, 0), "2": (0, 0)}).tag(sync=True)
    y_range: dict[int, tuple[int, int]] = traitlets.Dict({1: (None, None), 2: (None, None)}).tag(sync=True)
    combine_y_range = traitlets.Bool(False).tag(sync=True)

    scope_status = traitlets.Int(0).tag(sync=True)
    monitor_status = traitlets.Bool(False).tag(sync=True)
    lock_scope_operation = traitlets.Bool(False).tag(sync=True)

    def __init__(self, *args: typing.Any, **kwargs: typing.Any) -> None:
        super().__init__(*args, **kwargs)
        self._logger = logger
        if not hasattr(self, "acquisition"):
            self._acquisition: Acquisition | None = None
            if "acquisition" in kwargs and isinstance(kwargs["acquisition"], Acquisition):
                self._acquisition = kwargs["acquisition"]
            if self._acquisition is None:
                raise ValueError("acquisition is required")

        # 0 means scope_acquisition is effective, 1 means acquisition is effective,
        # and by default, scope_acquisition is effective.
        self._effect_acq = 0
        self._scope_acquisition = ScopeAcquisition(self._acquisition.cracker)
        self._acquisition.on_status_changed(self._change_acquisition_source)
        self._scope_acquisition.on_status_changed(self._change_scope_acquisition_status)
        self._monitor_period = 0.1

    def _change_acquisition_source(self, status: int) -> None:
        # Listen the acquisition thread status change and update scope monitor status.
        if status == 0:
            self.lock_scope_operation = False
        else:
            self._effect_acq = 1
            self.lock_scope_operation = True
            self.scope_status = 0
            if not self.monitor_status:
                self.start_monitor()

    def _change_scope_acquisition_status(self, status: int) -> None:
        # Only listen the stop change from scope acquisition thread, and sync status to ui.
        if status == 0 and self._effect_acq == 0:
            self.scope_status = status

    def _update_status(self, status: int) -> None:
        self.scope_status = status

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

    @traitlets.observe("scope_status")
    def scope_status_changed(self, change) -> None:
        self.run(change.get("new"))

    @traitlets.observe("monitor_status")
    def monitor_status_changed(self, change) -> None:
        if change.get("new"):
            self.start_monitor()

    def run(self, status: int) -> None:
        if not self.lock_scope_operation:
            self._scope_acquisition.run(status)
            self._effect_acq = 0
            if not self.monitor_status:
                self.start_monitor()

    def _monitor(self) -> None:
        while self.monitor_status:
            if self._effect_acq == 0:
                wave = self._scope_acquisition.get_last_wave()
                if not self._scope_acquisition.is_running():
                    self.monitor_status = False
            else:
                if self._scope_acquisition.is_running():
                    self._scope_acquisition.stop()
                wave = self._acquisition.get_last_wave()
                if not self._acquisition.is_running():
                    self.monitor_status = False
            self.update(wave)
            time.sleep(self._monitor_period)

    def start_monitor(self) -> None:
        self.monitor_status = True
        threading.Thread(target=self._monitor).start()

    def stop_monitor(self) -> None:
        self.monitor_status = False
