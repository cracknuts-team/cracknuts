import { EyeInvisibleOutlined, EyeOutlined } from "@ant-design/icons";
import { useModelState } from "@anywidget/react";
import { Spin, Switch } from "antd";
import ReactEcharts from "echarts-for-react";
import React from "react";

interface SeriesData {
  1: number[] | undefined;
  2: number[] | undefined;
}

interface TraceMonitorPanelProperties {
  disable?: boolean;
}

const TraceMonitorPanel: React.FC<TraceMonitorPanelProperties> = ({disable = false}) => {
  const [seriesData] = useModelState<SeriesData>("series_data");
  const [monitorStatus, setMonitorStatus] = useModelState<boolean>("monitor_status");

  const colors = ["green", "red"];

  const option: object = {
    tooltip: {
      trigger: "axis",
      axisPointer: {
        type: "cross",
      },
    },
    grid: {
      left: "80",
      right: "80",
      top: "40",
      bottom: "80",
    },
    animation: false,
    xAxis: {
      type: "category",
      axisLine: {
        onZero: false,
      },
    },
    dataZoom: getDataZoom(),
    yAxis: getEchartsYAxis(seriesData),
    series: getEchartsSeries(seriesData),
  };

  function getDataZoom() {
    if (!monitorStatus) {
      return [
        {
          type: "inside",
          xAxisIndex: 0,
          moveOnMouseMove: "alt",
          zoomOnMouseWheel: "alt",
        },
        {
          type: "slider",
          xAxisIndex: 0,
          moveOnMouseMove: "alt",
          zoomOnMouseWheel: "alt",
          realtime: false,
        },
      ];
    } else {
      return [];
    }
  }

  function getEchartsYAxis(seriesData: SeriesData) {
    const yAxis = [];
    yAxis.push({
      type: "value",
      position: "left",
      alignTicks: true,
      axisLine: {
        show: true,
        lineStyle: {
          color: colors[0],
        },
      },
      axisLabel: {
        formatter: "{value} mV",
      },
    });
    if (seriesData["2"]) {
      yAxis.push({
        type: "value",
        position: "right",
        alignTicks: true,
        axisLine: {
          show: true,
          lineStyle: {
            color: colors[1],
          },
        },
        axisLabel: {
          formatter: "{value} mV",
        },
      });
    }

    return yAxis;
  }

  function getEchartsSeries(seriesData: SeriesData) {
    const series = [];
    series.push({
      name: "channel 1",
      data: seriesData["1"],
      type: "line",
      lineStyle: {
        color: colors[0],
        width: 1,
      },
      symbol: "none",
      emphasis: {
        disabled: true,
      },
      yAxisIndex: 0,
    });

    if (seriesData["2"]) {
      series.push({
        name: "channel 2",
        data: seriesData["2"],
        type: "line",
        lineStyle: {
          color: colors[1],
          width: 1,
        },
        symbol: "none",
        emphasis: {
          disabled: true,
        },
        yAxisIndex: 1,
      });
    }
    return series;
  }

  return (
    <Spin indicator={<span></span>} spinning={disable}>
      {/* eslint @typescript-eslint/no-unused-vars: "off" */}
      <Switch
        size="small"
        onChange={(checked: boolean, _) => {
          setMonitorStatus(checked);
        }}
        checkedChildren={<EyeOutlined />}
        unCheckedChildren={<EyeInvisibleOutlined />}
        defaultChecked={monitorStatus ? monitorStatus : false}
        value={monitorStatus}
      />
      <ReactEcharts option={option} notMerge={true} style={{ height: 350 }} />
    </Spin>
  );
};


interface TraceSeries {
  color: string;
  name: string;
  emphasis: boolean;
  data: Array<number>;
  index: Array<number>;
}

const TraceAnalysisPanel: React.FC = () => {
  const [traceSeriesList] = useModelState<Array<TraceSeries>>("trace_series_list");

  const getLegends = () => {
    const legends: Array<string> = [];
    traceSeriesList.forEach((traceSeries) => {
      legends.push(traceSeries.name);
    });

    return legends;
  };

  const getSeries = (): Array<any> => {
    const series: Array<any> = [];

    traceSeriesList.forEach((traceSeries) => {
      series.push({
        name: traceSeries.name,
        type: "line",
        data: traceSeries.data,
        symbol: "none",
        lineStyle: {
          width: 1,
          color: traceSeries.color,
        },
        emphasis: {
          disabled: traceSeries.emphasis,
          focus: "series",
        },
      });
    });

    return series;
  };

  const option = {
    grid: {
      left: "40",
      right: "40",
      top: 80,
    },
    tooltip: {
      trigger: "axis",
      axisPointer: {
        type: "cross",
      },
      confine: true,
      triggerOn: "click",
      enterable: true,
      formatter: function (params: Array<any>) {
        let htmlStr =
          '<div style="height: auto;max-height: 180px;overflow-y: auto;"><p>' + params[0].axisValue + "</p>";
        for (let i = 0; i < params.length; i++) {
          htmlStr +=
            '<p style="color: #666;">' + params[i].marker + params[i].seriesName + ":&nbsp;" + params[i].value + "</p>";
        }
        htmlStr += "</div>";
        return htmlStr;
      },
    },
    animation: false,
    toolbox: {
      show: true,
      feature: {
        dataZoom: {
          show: true,
          title: {
            zoom: "缩放",
            back: "还原",
          },
          yAxisIndex: "none",
          brushStyle: {
            color: "rgba(190, 190, 190, 0.5)",
          },
        },
        saveAsImage: { show: true },
      },
    },

    dataZoom: [
      {
        type: "inside",
        xAxisIndex: 0,
        moveOnMouseMove: "alt",
        zoomOnMouseWheel: "alt",
      },
      {
        type: "slider",
        xAxisIndex: 0,
        moveOnMouseMove: "alt",
        zoomOnMouseWheel: "alt",
        realtime: false,
      },
    ],
    legend: {
      data: getLegends(),
      type: "scroll",
      pageButtonPosition: "start",
      orient: "horizontal",
      // left: 115,
      // right: 125,
      top: 30,
      // bottom: 10,
    },
    xAxis: {
      type: "category",
      axisTick: {
        show: false,
      },
      // axisLabel: {
      //     show: false,
      // },
      axisLine: {
        show: false,
      },
    },

    yAxis: {},
    series: getSeries(),
  };

  return (
    <div>
      <ReactEcharts option={option} notMerge={true} style={{ height: 400 }} />
    </div>
  );
};

export { TraceMonitorPanel, TraceAnalysisPanel };
