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
        for i in range(self._traces.shape[0]):
            if self._trace_name_prefix is not None and i < len(self._trace_name_prefix):
                trace_name = self._trace_name_prefix[i] + "/"
            else:
                trace_name = ""
            trace_name += f"t-{i}"
            # self._fig.add_trace(
            #     go.Scattergl(name=trace_name, showlegend=True, line={"width": 1}, mode="lines"),
            #     hf_y=self._traces[i, :],
            # )
        traces_list = [
            go.Scattergl(name=f"trace {i}", showlegend=True, line={"width": 1}, mode="lines", y=self._traces[i, :])
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
            elif isinstance(t_idx, slice):
                self._traces = traces[t_idx]
            elif isinstance(t_idx, list):
                self._traces = traces[t_idx[0]]
        elif isinstance(ch_idx, list):
            traces = []
            name_ch_prefixes = []
            for i, _ch_idx in enumerate(ch_idx):
                trace = self._trace_dataset.get_origin_data()[f"0/{_ch_idx}/traces"]
                if isinstance(t_idx, slice):
                    trace = trace[t_idx]
                if isinstance(t_idx, list):
                    if len(ch_idx) != len(trace):
                        raise ValueError("通道数量和曲线切片数组长度不一致")
                    trace = trace[t_idx[i]]
                traces.append(trace)
                name_ch_prefixes.append([f"c-{_ch_idx}" for _ in range(trace.shape[0])])
            self._traces = np.vstack(traces)

        if self._has_plot:
            self.plot_line()
