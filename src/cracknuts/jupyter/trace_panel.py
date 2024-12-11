# Copyright 2024 CrackNuts. All rights reserved.
import math
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

        # if self.custom_range_model:
        #     self.y_range = {
        #         1: (self.custom_y_range["1"][0], self.custom_y_range["1"][1], None),
        #         2: (self.custom_y_range["2"][0], self.custom_y_range["2"][1], None)
        #     }
        # else:
        if 1 in series_data.keys():
            c1 = series_data[1]
            mn1, mx1 = np.min(c1), np.max(c1)
        if 2 in series_data.keys():
            c2 = series_data[2]
            mn2, mx2 = np.min(c2), np.max(c2)
            #
            # if self.combine_y_range:
            #     if mn1 is not None and mx1 is not None and mn2 is not None and mx2 is not None:
            #         mn = min(mn1, mn2)
            #         mx = max(mx1, mx2)
            #     elif mn1 is None and mx1 is None and mn2 is not None and mx2 is not None:
            #         mn, mx = mn2, mx2
            #     elif mn1 is not None and mx1 is not None and mn2 is None and mx2 is None:
            #         mn, mx = mn1, mx1
            #     else:
            #         mn, mx = None, None
            #     if mn is not None and mx is not None:
            #         mn, mx, interval = self._calculate_y_axis_ticks(mn, mx)
            #         mn1, mn2 = mn, mn
            #         mx1, mx2 = mx, mx
            # else:
            #     if 1 in series_data.keys():
            #         mn1, mx1, interval1 = self._calculate_y_axis_ticks(mn1, mx1)
            #
            #     if 2 in series_data.keys():
            #         mn2, mx2, interval2 = self._calculate_y_axis_ticks(mn2, mx2)

            # self.y_range = {1: (mn1, mx1, interval1), 2: (mn2, mx2, interval2)}
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

    @staticmethod
    def _calculate_y_axis_ticks(start: float, end: float, num_ticks: int = 4):
        """
        Calculate Y-axis tick marks for a range [start, end] with `num_ticks` ticks.
        The ticks are made as regular as possible (e.g., multiples of 1, 2, 5, 10).

        Args:
            start (float): Starting value of the range.
            end (float): Ending value of the range.
            num_ticks (int): Number of ticks to generate (default is 6).
        """
        if start >= end:
            return None, None, None

        # Calculate raw range and rough interval
        raw_range = end - start
        rough_interval = raw_range / (num_ticks - 1)

        # Find the nearest "nice" interval (1, 2, 5, 10, etc.)
        scale = 10 ** math.floor(math.log10(rough_interval))
        candidates = [1, 2, 5, 10]
        nice_interval = min(candidates, key=lambda x: abs(rough_interval - x * scale)) * scale

        # Adjust start and end to aligned integer values
        adjusted_start = math.floor(start / nice_interval) * nice_interval
        if adjusted_start - start < nice_interval / 3:
            adjusted_start -= nice_interval

        adjusted_end = math.ceil(end / nice_interval) * nice_interval

        # Generate ticks
        ticks = []
        current = adjusted_start
        while current <= adjusted_end:
            ticks.append(int(round(current)))  # Ensure all values are integers
            current += nice_interval

        if current - adjusted_end < nice_interval * 1.333:
            current = adjusted_end + nice_interval
            adjusted_end = current
            ticks.append(int(round(current)))

        return adjusted_start, adjusted_end, nice_interval
