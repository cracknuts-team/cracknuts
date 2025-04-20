import React, {useEffect, useRef, useState} from "react";
import {useModel, useModelState} from "@anywidget/react";
import ReactEcharts from "echarts-for-react";
import Slider from "@/Slider.tsx";
import type {ECharts} from "echarts";
import {useIntl} from "react-intl";

interface SeriesData {
  color: string;
  name: string;
  data: Array<number>;
  z: number;
}

interface TraceSeries {
  seriesDataList: Array<SeriesData>,
  xData: Array<number>,
  percentRange: Array<number>,
  range: Array<number>,
}

interface ChartSize {
  width: number;
  height: number;
}

interface BrushEndParams {
  areas?: {
    coordRange?: [number, number];
  }[];
}

// interface BrushSelectedParams {
//   batch?: {
//     areas: {
//       coordRange?: [number, number];
//     }[]
//   }[];
// }

const TracePanel: React.FC = () => {

  const [, setSelectedRange] = useModelState<Array<number>>("selected_range");
  const [, setOverviewSelectedRange] = useModelState<Array<number>>("overview_select_range");
  const [, setPercentRange] = useModelState<Array<number>>("percent_range");

  const [traceSeries] = useModelState<TraceSeries>("trace_series");
  const [, setChartSize] = useModelState<ChartSize>("chart_size");

  const chartBoxRef = useRef<HTMLDivElement>(null)

  const [overviewTraceSeries] = useModelState<TraceSeries>("overview_trace_series");

  const [overviewRange, _setOverviewRange] = useState<Array<number>>(overviewTraceSeries.range)

  const setOverviewRange = (percentStart: number, percentEnd: number) => {
    if (overviewTraceSeries && overviewTraceSeries.seriesDataList && overviewTraceSeries.seriesDataList.length > 0) {
      const seriesDataLen = overviewTraceSeries.seriesDataList[0].data.length;
      _setOverviewRange([(seriesDataLen - 1) * percentStart / 100, (seriesDataLen - 1) * percentEnd / 100])
    }
  };

  const [sliderPercentRange, setSliderPercentRange] = useState<Array<number>>(traceSeries.percentRange)

  const anyWidgetModel = useModel();

  const intl = useIntl();

  useEffect(() => {

    // Since the chart component is not initialized, it uses the window size.
    setChartSize({
      width: window.innerWidth,
      height: window.innerHeight
    })

    if (!chartBoxRef.current || typeof ResizeObserver === 'undefined') {
      return
    }
    const observer = new ResizeObserver(([entry]) => {
      const {width, height} = entry.contentRect
      setChartSize({
        width: width,
        height: height
      })
    })
    observer.observe(chartBoxRef.current)
    return () => observer.disconnect()
  }, [])

  const chartRef = useRef<ReactEcharts>(null);

  const onChartReady = (chart: ECharts) => {
    chart.on("brushEnd", (params) => {
      const brushParams = params as BrushEndParams;
      if (brushParams && brushParams.areas && brushParams.areas.length > 0 && brushParams.areas[0].coordRange && brushParams.areas[0].coordRange.length == 2) {
        const [newStart, newEnd] = brushParams.areas[0].coordRange
        setSelectedRange([newStart, newEnd])
      }

    });
  };

  useEffect(() => {
    if (chartRef.current?.getEchartsInstance) {
      onChartReady(chartRef.current.getEchartsInstance());
    }
    return () => {
    }
  }, []);

  const getSeries = (): Array<object> => {
    const series: Array<object> = [];

    if (traceSeries && traceSeries.seriesDataList) {
      traceSeries.seriesDataList.forEach((seriesData) => {
        series.push({
          name: seriesData.name,
          type: "line",
          data: seriesData.data,
          symbol: "none",
          lineStyle: {
            width: 1,
            color: seriesData.color,
          },
          emphasis: {
            disabled: true,
            focus: "series",
          },
          z: seriesData.z,
          silent: true
        });
      });
    }

    return series;
  };

  const getOverviewSeries = (): Array<object> => {

    if (overviewTraceSeries.seriesDataList?.length > 0) {
      const overviewSeriesData = overviewTraceSeries.seriesDataList[0]
      return [{
        name: overviewSeriesData.name,
        type: "line",
        data: overviewSeriesData.data,
        symbol: "none",
        lineStyle: {
          width: 1,
          color: overviewSeriesData.color,
        },
        emphasis: {
          disabled: true,
          focus: "series",
        },
        silent: true
      }];
    } else {
      return [];
    }
  }

  const getXData = () => {
    if (traceSeries && traceSeries.xData) {
      return traceSeries.xData
    } else {
      return []
    }
  }

  const getOverviewXData = () => {
    if (overviewTraceSeries && overviewTraceSeries.xData) {
      return overviewTraceSeries.xData
    } else {
      return []
    }
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
      enterable: true
    },
    animation: false,
    toolbox: {
      show: true,
      feature: {
        saveAsImage: {
          show: true,
          title: intl.formatMessage({id: "trace.echarts.toolbox.saveAsImage"})
        },
        myReset: {
            show: true,
            title: intl.formatMessage({id: "trace.echarts.toolbox.myReset"}),
            icon: 'M3.8,33.4 M47,18.9h9.8V8.7 M56.3,20.1 C52.1,9,40.5,0.6,26.8,2.1C12.6,3.7,1.6,16.2,2.1,30.6 M13,41.1H3.1v10.2 M3.7,39.9c4.2,11.1,15.8,19.5,29.5,18 c14.2-1.6,25.2-14.1,24.7-28.5',
            onclick: function (){
                anyWidgetModel.send({source: "reset", event: "onClick"});
            }
        },
        brush: {
          title: {
            lineX: intl.formatMessage({id: "trace.echarts.toolbox.brush.lineX"}),
          }
        }
      },
    },

    brush: {
      toolbox: ['lineX'],
      xAxisIndex: 0,
      brushStyle: {
        borderWidth: 1,
        color: 'rgba(128, 128, 128, 0.5)',
        borderColor: 'rgba(128, 128, 128, 0.1)'
      }
    },
    xAxis: {
      type: "category",
      axisTick: {
        show: false,
      },
      axisLine: {
        show: false,
      },
      data: getXData()
    },

    yAxis: {},
    series: getSeries(),
  };

  const overviewOption = {
    brush: {
      xAxisIndex: 0,
      // transformable: false,
      brushStyle: {
        borderColor: '#007bff',
        borderWidth: 1,
        color: 'rgba(0, 123, 255, 0.2)'
      },
      throttleType: 'fixRate',
      throttleDelay: 0
    },
    toolbox: {
      show: false
    },
    grid: {
      left: 0,
      right: 0,
      top: 0,
      bottom: 0,
      backgroundColor: '#f5f5f5',
      containLabel: false,
      show: true
    },
    animation: false,
    series: getOverviewSeries(),
    yAxis: {
      axisTick: {
        show: false,
      },
      axisLine: {
        show: false,
      },
      axisLabel: {
        show: false,
      },
      splitLine: {
        show: false
      }
    },
    xAxis: {
      type: "category",
      axisTick: {
        show: false,
      },
      axisLine: {
        show: false,
      },
      axisLabel: {
        show: false,
      },
      data: getOverviewXData()
    },
  }

  const overviewChartRef = useRef<ReactEcharts>(null);

  const onOverviewChartReady = (chart: ECharts) => {
    chart.on("brushEnd", (params) => {
      const brushParams = params as BrushEndParams;
      if (brushParams && brushParams.areas && brushParams.areas.length > 0
        && brushParams.areas[0].coordRange
        && brushParams.areas[0].coordRange.length == 2) {
        const [newStart, newEnd] = brushParams.areas[0].coordRange
        console.info([newStart, newEnd])
        setOverviewSelectedRange([newStart, newEnd])
      }

    });
  };

  useEffect(() => {
    if (overviewChartRef.current?.getEchartsInstance) {
      onOverviewChartReady(overviewChartRef.current.getEchartsInstance());
    }
    return () => {
    }
  }, []);

  useEffect(() => {
    if (overviewRange == undefined) {
      return
    }
    overviewChartRef.current?.getEchartsInstance()?.dispatchAction({
      type: 'brush',
      areas: [
        {
          brushType: 'lineX',
          xAxisIndex: 0,
          coordRange: [overviewRange[0], overviewRange[1]]
        }
      ],
      removeOnClick: false,
      transformable: false
    });
  }, [overviewRange]);

  useEffect(() => {
    if (overviewTraceSeries == undefined) {
      return
    }
    overviewChartRef.current?.getEchartsInstance()?.dispatchAction({
      type: 'brush',
      areas: [
        {
          brushType: 'lineX',
          xAxisIndex: 0,
          coordRange: [overviewTraceSeries.range[0], overviewTraceSeries.range[1]]
        }
      ],
      removeOnClick: false,
      transformable: false
    });
  }, [overviewTraceSeries]);

  useEffect(() => {
    setSliderPercentRange(traceSeries.percentRange)
  }, [traceSeries]);

  useEffect(() => {
    overviewChartRef.current?.getEchartsInstance()?.dispatchAction({
      type: 'takeGlobalCursor',
      key: 'brush',
      brushOption: {
          brushType: 'lineX',
          brushMode: 'single',
          removeOnClick: false,
      }
    });
  }, [overviewTraceSeries]);

  return (
    <div ref={chartBoxRef}>
      <ReactEcharts ref={chartRef} option={option} notMerge={true} style={{height: 400}}/>
      <ReactEcharts ref={overviewChartRef} option={overviewOption} notMerge={true} style={{height: 60}}/>
      <Slider start={sliderPercentRange[0]} end={sliderPercentRange[1]} onChangeFinish={(s, e) => {
        setPercentRange([s, e]);
        setOverviewRange(s, e)
      }} onChange={(s, e) => {
        setOverviewRange(s, e);
      }}/>
    </div>
  );
};

export default TracePanel;