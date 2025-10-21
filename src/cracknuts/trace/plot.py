# Copyright 2024 CrackNuts. All rights reserved.

import numpy as np
import plotly.graph_objects as go
from numpy.typing import ArrayLike
from plotly_resampler import FigureWidgetResampler

from cracknuts.trace.trace import TraceDataset


class TracePlot:
    """
    使用 Plotly Resampler 绘制大规模示波图的面板，仅保留曲线信息
    """

    def __init__(self):
        self._trace_dataset: TraceDataset | None = None
        self._traces: ArrayLike | None = None
        self._trace_names: list | None = None
        self._trace_name_prefix: list[str] | None = None
        self._fig = FigureWidgetResampler(go.Figure())
        self._fig.update_xaxes(  # type: ignore
            showline=True,
            linewidth=1,
            linecolor="#dddddd",
            mirror=True,
            gridwidth=1,
            gridcolor="#dddddd",
        )
        self._fig.update_yaxes(  # type: ignore
            showline=True, linewidth=1, linecolor="#dddddd", mirror=True, gridwidth=1, gridcolor="#dddddd"
        )

        self._fig.update_layout(
            plot_bgcolor="white",  # 绘图区背景白色
            paper_bgcolor="white",  # 整个画布背景白色
        )
        self._fig.update_layout(margin=dict(t=40, b=40, l=0))
        self._fig.update_layout(height=350)
        self._has_plot = False

    def set_trace_dataset(self, trace_dataset: TraceDataset) -> None:
        """
        设置曲线
        :param trace_dataset: 曲线数据集
        :type trace_dataset: TraceDataset
        """
        self._trace_dataset = trace_dataset

    def plot_line(self) -> FigureWidgetResampler:
        """
        显示曲线， 默认不通过配置 show_trace 配置显示曲线时，则显示 通道 0 的所有曲线
        """
        if self._traces is None:
            self.show_trace()
        self._fig.data = []
        traces_list = [
            go.Scattergl(
                name=f"{self._trace_names[i]}", showlegend=True, line={"width": 1}, mode="lines", y=self._traces[i, :]
            )
            for i in range(self._traces.shape[0])
        ]
        self._fig.add_traces(traces_list)
        self._fig.reload_data()
        self._has_plot = True
        return self._fig

    def show_trace(self, ch_idx: int | list[int] = 0, t_idx: list[slice, slice] | slice | None = None) -> None:
        """
        配置要显示的曲线

        :param ch_idx: 通道索引，可以是 int 或 list
        :type ch_idx: int | list[int]
        :param t_idx: 曲线切片，当传入切片列表时，列表与 ch_idx 列表匹配进行切片
        :type t_idx: list[slice, slice]
        """

        if isinstance(ch_idx, int):
            traces = self._trace_dataset.get_origin_data()[f"0/{ch_idx}/traces"]
            if t_idx is None:
                self._traces = traces
                self._trace_names = [f"T{i}" for i in range(traces.shape[0])]
            elif isinstance(t_idx, slice):
                self._traces = traces[t_idx]
                self._trace_names = [f"T{i}" for i in self._slice_to_list(t_idx, traces.shape[0])]
            elif isinstance(t_idx, list):
                self._traces = traces[t_idx[0]]
                self._trace_names = [f"T{i}" for i in self._slice_to_list(t_idx[0], traces.shape[0])]
        elif isinstance(ch_idx, list):
            traces_list = []
            trace_names_list = []
            for i, _ch_idx in enumerate(ch_idx):
                traces = self._trace_dataset.get_origin_data()[f"0/{_ch_idx}/traces"]
                name_ch_prefix = f"C{_ch_idx}-"
                if t_idx is None:
                    traces_list.append(traces)
                    trace_names_list.append([f"{name_ch_prefix}T{i}" for i in range(traces.shape[0])])
                elif isinstance(t_idx, slice):
                    traces_list.append(traces[t_idx])
                    trace_names_list.append(
                        [f"{name_ch_prefix}T{i}" for i in self._slice_to_list(t_idx, traces.shape[0])]
                    )
                elif isinstance(t_idx, list):
                    if len(ch_idx) != len(traces):
                        raise ValueError("通道数量和曲线切片数组长度不一致")
                    traces_list.append(traces[t_idx[i]])
                    trace_names_list.append(
                        [f"{name_ch_prefix}T{i}" for i in self._slice_to_list(t_idx[i], traces.shape[0])]
                    )
            self._traces = np.vstack(traces_list)
            self._trace_names = [name for sublist in trace_names_list for name in sublist]
        if self._has_plot:
            self.plot_line()

    @staticmethod
    def _slice_to_list(s: slice, length: int = None):
        """
        将 slice 对象展开为一个 list。

        参数:
            s (slice): 需要展开的切片对象
            length (int, 可选): 当 slice.stop 为 None 时，需要给定序列长度，用于确定范围。

        返回:
            list: 按 slice 展开的列表
        """
        start = s.start or 0
        step = s.step or 1

        if s.stop is None:
            if length is None:
                raise ValueError("slice.stop 为 None 时必须指定 length")
            stop = length
        else:
            stop = s.stop

        return list(range(start, stop, step))
