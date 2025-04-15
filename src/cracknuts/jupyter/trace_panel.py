# Copyright 2024 CrackNuts. All rights reserved.

import pathlib
import typing
from dataclasses import dataclass, field

import numpy as np
from numpy import ndarray

from cracknuts.trace.trace import TraceDataset, NumpyTraceDataset
from traitlets import traitlets

from cracknuts.jupyter.panel import MsgHandlerPanelWidget


@dataclass
class _TraceSeriesData:
    name: str
    data: ndarray
    color: None | str
    channel_index: int
    trace_index: int

    def to_dict(self) -> dict:
        return {
            "name": self.name,
            "data": self.data,
            "color": self.color,
            "channel_index": self.channel_index,
            "trace_index": self.trace_index,
        }


@dataclass
class _TraceSeries:
    series_data_list: list[_TraceSeriesData] = field(default_factory=list)
    x_data: np.ndarray = np.empty(0)
    percent_range: list = field(default_factory=lambda: [0, 100])

    def to_dict(self) -> dict:
        return {
            "seriesDataList": [s.to_dict() for s in self.series_data_list],
            "xData": self.x_data,
            "percentRange": self.percent_range,
        }


class TracePanelWidget(MsgHandlerPanelWidget):
    _esm = pathlib.Path(__file__).parent / "static" / "TracePanelWidget.js"
    _css = pathlib.Path(__file__).parent / "static" / "TracePanelWidget.css"

    chart_size: dict[str, int] = traitlets.Dict({"width": 0, "height": 0}).tag(sync=True)

    trace_series = traitlets.Dict(_TraceSeries().to_dict()).tag(sync=True)

    range_start = traitlets.Float(0).tag(sync=True)
    range_end = traitlets.Float(100).tag(sync=True)

    selected_range = traitlets.Tuple((0, 0)).tag(sync=True)
    percent_range = traitlets.Tuple((0, 100)).tag(sync=True)

    _DEFAULT_SHOW_INDEX_THRESHOLD = 3

    def __init__(self, *args: typing.Any, **kwargs: typing.Any) -> None:
        super().__init__(*args, **kwargs)
        self._emphasis = kwargs.get("emphasis", False)
        self._trace_dataset: TraceDataset | None = None
        self.show_trace: ShowTrace = ShowTrace(self._show_trace)
        self._auto_sync = False
        self._trace_series: _TraceSeries | None = None
        self._trace_cache_channel_indices: ndarray | None = None
        self._trace_cache_trace_indices: ndarray | None = None
        self._trace_cache_traces: ndarray | None = None
        self._trace_cache_x_indices: ndarray | None = None
        self._trace_cache_x_range_start: int | None = None
        self._trace_cache_x_range_end: int | None = None
        self._trace_cache_trace_highlight_indices: dict[int, list[int]] | None = None

        self._trace_series_color_background = "gray"
        self._trace_series_color_highlight = "red"

    def _repr_mimebundle_(self, **kwargs: dict) -> tuple[dict, dict] | None:
        self.send_state("trace_series")
        self._auto_sync = True
        return super()._repr_mimebundle_(**kwargs)

    def set_emphasis(self, value: bool) -> None:
        ...
        # if self._emphasis != value:
        #     self._emphasis = value
        #     self.trace_series_list = [{**series, "emphasis": not value} for series in self.trace_series_list]
        #     if self._auto_sync:
        #         self.send_state("trace_series_list")

    def set_numpy_data(self, trace: np.ndarray, data: np.ndarray = None) -> None:
        ds = NumpyTraceDataset.load_from_numpy_array(trace, data)
        self.set_trace_dataset(ds)

    def _show_trace(self, channel_slice, trace_slice, display_range: tuple[int, int] = None):
        channel_indexes, trace_indices, traces, data = self._trace_dataset.trace_data_with_indices[
            channel_slice, trace_slice
        ]

        self._trace_cache_channel_indices = channel_indexes
        self._trace_cache_trace_indices = trace_indices
        self._trace_cache_traces = traces

        if display_range is None:
            self._trace_cache_x_indices = [0, self._trace_dataset.sample_count - 1]
        else:
            self._trace_cache_x_indices = display_range

        [start, end] = self._trace_cache_x_indices

        trace_series = self._get_trace_series_by_index_range(start, end)

        self._trace_series = trace_series | {
            "percentRange": [
                start / (self._trace_dataset.sample_count - 1) * 100,
                end / (self._trace_dataset.sample_count - 1) * 100,
            ],
        }
        if self._auto_sync:
            self._trace_series_send_state()

    def _trace_series_send_state(self):
        self.trace_series = self._trace_series.to_dict()

    def _get_by_range(self, trace: np.ndarray, start, end):
        pixel = self.chart_size["width"]
        if pixel is None or pixel == 0:
            pixel = 1920
        x_idx, y_data = self._down_sample(trace, start, end, pixel)
        # if d > 0:
        #     print(d, y_data.shape)
        return x_idx, y_data

    @staticmethod
    def _down_sample(value: np.ndarray, mn, mx, down_count) -> tuple[np.ndarray, np.ndarray]:
        mn = max(0, mn)
        mx = min(value.shape[0], mx)

        _value = value[mn:mx]
        _index = np.arange(mn, mx).astype(np.int32)

        ds = int(max(1, int(mx - mn) / down_count))

        if ds == 1:
            return _index, _value
        sample_count = int((mx - mn) // ds)

        down_index = np.empty((sample_count, 2), dtype=np.int32)
        down_index[:] = _index[: sample_count * ds : ds, np.newaxis]

        _value = _value[: sample_count * ds].reshape((sample_count, ds))
        down_value = np.empty((sample_count, 2))
        down_value[:, 0] = _value.max(axis=1)
        down_value[:, 1] = _value.min(axis=1)

        return down_index.reshape(sample_count * 2), down_value.reshape(sample_count * 2)

    def change_range(self, start: int, end: int):
        if self._trace_cache_x_indices is not None:
            start, end = self._trace_cache_x_indices[start], self._trace_cache_x_indices[end]

        trace_series = self._get_trace_series_by_index_range(start, end)

        self.trace_series = trace_series | {
            "percentRange": [
                start / (self._trace_dataset.sample_count - 1) * 100,
                end / (self._trace_dataset.sample_count - 1) * 100,
            ],
        }
        if self._auto_sync:
            self.send_state("trace_series")

    def change_percent_range(self, percent_start: float, percent_end: float):
        start = round((self._trace_dataset.sample_count - 1) * percent_start / 100)
        end = round((self._trace_dataset.sample_count - 1) * percent_end / 100)

        trace_series = self._get_trace_series_by_index_range(start, end)

        self.trace_series = trace_series | {
            "percentRange": [percent_start, percent_end],
        }
        if self._auto_sync:
            self.send_state("trace_series")

    def _get_trace_series_by_index_range(self, start: int, end: int) -> _TraceSeries:
        series_data_list = []

        x_idx = None
        for c, channel_index in enumerate(self._trace_cache_channel_indices):
            for t, trace_index in enumerate(self._trace_cache_trace_indices):
                x_idx, y_data = self._get_by_range(self._trace_cache_traces[c, t, :], start, end)
                series_data_list.append(
                    _TraceSeriesData(
                        name=str(channel_index) + "-" + str(trace_index),
                        data=y_data,
                        color=self._trace_series_color_background,
                        trace_index=t,
                        channel_index=c,
                    )
                )

        self._trace_cache_x_indices = x_idx

        return _TraceSeries(series_data_list=series_data_list, x_data=x_idx)

    def _get_highlight_color(self, channel_index: int, trace_index: int) -> None | str:
        if self._trace_cache_trace_highlight_indices is None:
            return None
        else:
            if channel_index in self._trace_cache_trace_highlight_indices:
                trace_indices = self._trace_cache_trace_indices[channel_index]
                if trace_index in trace_indices:
                    return self._trace_series_color_highlight
                else:
                    return self._trace_series_color_background
            else:
                return self._trace_series_color_background

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

    def highlight(self, indices: dict[int, list : [int]] | list[int]) -> None:
        if isinstance(indices, list):
            indices = {0: indices}
        self._trace_series_color_highlight = indices
        for series in self.trace_series["seriesDataList"]:
            series["color"] = self._get_highlight_color(series["name"], series["xData"])

    def set_numpy_data_highlight(self, trace: np.ndarray, data: np.ndarray = None, highlight_indexes=None):
        ...
        # if highlight_indexes is None:
        #     highlight_indexes = []
        # ds = NumpyTraceDataset.load_from_numpy_array(trace, data)
        # self._trace_dataset = ds
        # trace_series_list = []
        #
        # for t, trace_index in enumerate(range(ds.trace_count)):
        #     if t not in highlight_indexes:
        #         trace_series_list.append(
        #             {
        #                 "name": str(0) + "-" + str(trace_index),
        #                 "data": trace[t],
        #                 "emphasis": not self._emphasis,
        #                 "color": "gray",
        #             }
        #         )
        # for t, trace_index in enumerate(range(ds.trace_count)):
        #     if t in highlight_indexes:
        #         trace_series_list.append(
        #             {
        #                 "name": str(0) + "-" + str(trace_index),
        #                 "data": trace[t],
        #                 "emphasis": not self._emphasis,
        #                 "color": "red",
        #                 "z": 100,
        #             }
        #         )
        # self.trace_series_list = trace_series_list
        # if self._auto_sync:
        #     self.send_state("trace_series_list")

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

    @traitlets.observe("selected_range")
    def selected_range_changed(self, change) -> None:
        if change.get("new") is not None:
            s, e = change.get("new")
            self.change_range(s, e)

    @traitlets.observe("percent_range")
    def percent_range_changed(self, change) -> None:
        if change.get("new") is not None:
            s, e = change.get("new")
            self.change_percent_range(s, e)


class ShowTrace:
    def __init__(self, func_show_trace):
        self._func_trace = func_show_trace

    def __getitem__(self, item):
        return self._func_trace(item[0], item[1])
