# Copyright 2024 CrackNuts. All rights reserved.

import pathlib
import typing

import numpy as np
from cracknuts.trace.trace import TraceDataset, NumpyTraceDataset
from traitlets import traitlets

from cracknuts.jupyter.panel import MsgHandlerPanelWidget


class TracePanelWidget(MsgHandlerPanelWidget):
    _esm = pathlib.Path(__file__).parent / "static" / "TracePanelWidget.js"
    _css = ""

    trace_series_list: list[dict] = traitlets.List([])

    _DEFAULT_SHOW_INDEX_THRESHOLD = 3

    def __init__(self, *args: typing.Any, **kwargs: typing.Any) -> None:
        super().__init__(*args, **kwargs)
        self._emphasis = kwargs.get("emphasis", False)
        self._trace_dataset: TraceDataset | None = None
        self.show_trace: ShowTrace = ShowTrace(self._show_trace)
        self._auto_sync = False

    def _repr_mimebundle_(self, **kwargs: dict) -> tuple[dict, dict] | None:
        self.send_state("trace_series_list")
        self._auto_sync = True
        return super()._repr_mimebundle_(**kwargs)

    def set_emphasis(self, value: bool) -> None:
        if self._emphasis != value:
            self._emphasis = value
            self.trace_series_list = [{**series, "emphasis": not value} for series in self.trace_series_list]
            if self._auto_sync:
                self.send_state("trace_series_list")

    def set_numpy_data(self, trace: np.ndarray, data: np.ndarray = None) -> None:
        ds = NumpyTraceDataset.load_from_numpy_array(trace, data)
        self.set_trace_dataset(ds)

    def _show_trace(self, channel_slice, trace_slice):
        channel_indexes, trace_indexes, traces, data = self._trace_dataset.trace_data_with_indices[
            channel_slice, trace_slice
        ]

        trace_series_list = []

        for c, channel_index in enumerate(channel_indexes):
            for t, trace_index in enumerate(trace_indexes):
                trace_series_list.append(
                    {
                        "name": str(channel_index) + "-" + str(trace_index),
                        "data": traces[c, t],
                        "emphasis": not self._emphasis,
                    }
                )
        self.trace_series_list = trace_series_list
        if self._auto_sync:
            self.send_state("trace_series_list")

    def show_default_trace(self):
        trace_count = self._trace_dataset.trace_count
        self._show_trace(
            0,
            slice(
                0,
                trace_count if trace_count < self._DEFAULT_SHOW_INDEX_THRESHOLD else self._DEFAULT_SHOW_INDEX_THRESHOLD,
            ),
        )

    def show_all_trace(self):
        self._show_trace(slice(0, self._trace_dataset.channel_count), slice(0, self._trace_dataset.trace_count))

    def highlight(self, *indexes: int) -> None:
        self._emphasis = False
        x = [
            {**series, "emphasis": True, "color": "red" if i in indexes else "gray", "z": 100 if i in indexes else 1}
            for i, series in enumerate(self.trace_series_list)
        ]
        self.trace_series_list = x
        if self._auto_sync:
            self.send_state("trace_series_list")

    def set_numpy_data_highlight(self, trace: np.ndarray, data: np.ndarray = None, highlight_indexes=None):
        if highlight_indexes is None:
            highlight_indexes = []
        ds = NumpyTraceDataset.load_from_numpy_array(trace, data)
        self._trace_dataset = ds
        trace_series_list = []

        for t, trace_index in enumerate(range(ds.trace_count)):
            if t not in highlight_indexes:
                trace_series_list.append(
                    {
                        "name": str(0) + "-" + str(trace_index),
                        "data": trace[t],
                        "emphasis": not self._emphasis,
                        "color": "gray",
                    }
                )
        for t, trace_index in enumerate(range(ds.trace_count)):
            if t in highlight_indexes:
                trace_series_list.append(
                    {
                        "name": str(0) + "-" + str(trace_index),
                        "data": trace[t],
                        "emphasis": not self._emphasis,
                        "color": "red",
                        "z": 100,
                    }
                )
        self.trace_series_list = trace_series_list
        if self._auto_sync:
            self.send_state("trace_series_list")

    def set_trace_dataset(
        self, trace_dataset: TraceDataset, show_all_trace=False, channel_slice=None, trace_slice=None
    ) -> None:
        self._trace_dataset = trace_dataset
        if show_all_trace:
            self.show_all_trace()
        elif channel_slice is not None and trace_slice is not None:
            self._show_trace(channel_slice, trace_slice)
        else:
            self.show_default_trace()

    def open_trace_data_set_file(self, trace_dataset: TraceDataset) -> TraceDataset: ...

    def open_numpy_file(self, path: str): ...

    def open_zarr(self, path: str): ...


class ShowTrace:
    def __init__(self, func_show_trace):
        self._func_trace = func_show_trace

    def __getitem__(self, item):
        return self._func_trace(item[0], item[1])
