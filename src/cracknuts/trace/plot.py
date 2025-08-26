import plotly.graph_objects as go
from numpy.typing import ArrayLike
from plotly_resampler import FigureResampler

from cracknuts.trace.trace import TraceDataset


class TracePlot:
    """
    使用 Plotly Resampler 绘制大规模示波图的面板，仅保留曲线信息
    """

    def __init__(self):
        self._traces: ArrayLike | None = None
        self._trace_names: list[str] | None = None
        self._fig = FigureResampler(go.Figure())
        self._fig.update_xaxes(
            showline=True,  # 显示 x 轴外框
            linewidth=1,  # 外框宽度
            linecolor="#dddddd",  # 外框颜色
            mirror=True,  # 上下两边都画
            gridwidth=1,  # 网格线宽度
            gridcolor="#dddddd",
        )
        self._fig.update_yaxes(
            showline=True, linewidth=1, linecolor="#dddddd", mirror=True, gridwidth=1, gridcolor="#dddddd"
        )

        self._fig.update_layout(
            plot_bgcolor="white",  # 绘图区背景白色
            paper_bgcolor="white",  # 整个画布背景白色
        )

    def set_trace_dataset(self, trace_dataset: TraceDataset):
        self._traces = trace_dataset.get_origin_data()["/0/0/traces"]

    def show(self):
        for i in range(self._traces.shape[0]):
            if self._trace_names is not None and i < len(self._trace_names):
                trace_name = self._trace_names[i]
            else:
                trace_name = f"trace {i}"
            self._fig.add_trace(
                go.Scattergl(name=trace_name, showlegend=True, line={"width": 1}, mode="lines"),
                hf_y=self._traces[i, :],
            )
        return self._fig
