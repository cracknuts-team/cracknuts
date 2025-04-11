import React, {useEffect, useRef} from "react";
import {useModelState} from "@anywidget/react";
import ReactEcharts from "echarts-for-react";
import Slider from "@/Slider.tsx";
import type { ECharts } from "echarts";

interface SeriesData {
    color: string;
    name: string;
    data: Array<number>;
    emphasis: boolean;
    z: number;
}

interface TraceSeries {
    seriesDataList: Array<SeriesData>,
    xData: Array<number>,
}

// interface TraceQuery {
//     xMin: number;
//     xMax: number;
//     yMin: number;
//     yMax: number;
// }

interface ChartSize {
    width: number;
    height: number;
}

interface BrushEndParams {
  areas?: {
    coordRange?: [number, number];
  }[];
}

const TracePanel: React.FC = () => {

    const [selectedStart, setSelectedStart] = useModelState<number>("selected_start");
    const [selectedEnd, setSelectedEnd] = useModelState<number>("selected_end");
    const selectedStartRef = useRef<number>(selectedStart);
    const selectedEndRef = useRef<number>(selectedEnd);

    const [, setSelectedRange] = useModelState<Array<number>>("selected_range");

    const [start, setStart] = useModelState<number>("range_start")
    const [end, setEnd] = useModelState<number>("range_end")

    const [, series] = useModelState<SeriesData>("series");

    const [traceSeries] = useModelState<TraceSeries>("trace_series");
    const [, setChartSize] = useModelState<ChartSize>("chart_size");




    const chartBoxRef = useRef<HTMLDivElement>(null)

    useEffect(() => {
        if (!chartBoxRef.current || typeof ResizeObserver === 'undefined') {
            return
        }
        const observer = new ResizeObserver(([entry]) => {
          const { width, height } = entry.contentRect
          setChartSize({
              width: width,
              height: height
          })
        })
        observer.observe(chartBoxRef.current)
        return () => observer.disconnect()
    }, [])

    const chartRef = useRef<ReactEcharts>(null);
    const brushAreasRef = useRef<Array<number>>([0, 0])

    // useEffect(() => {
    //     if (!chartRef.current) {
    //         return
    //     }
    //     chartRef.current?.getEchartsInstance().on("brushSelected", (params: any) => {
    //         brushAreasRef.current = params.areas;
    //         console.log("刷选区域更新", params.batch?.[0]?.areas?.[0]?.coordRange);
    //     });
    // }, []);

    const onChartReady = (chart: ECharts) => {
        chart.on("brushEnd", (params) => {
            const brushParams = params as BrushEndParams;
            if (brushParams && brushParams.areas && brushParams.areas.length > 1 && brushParams.areas[0].coordRange && brushParams.areas[0].coordRange.length == 2) {
                const [s, e] = brushParams.areas[0].coordRange
                if (s == selectedStartRef.current) {
                    setSelectedEnd(e);
                } else if (e == selectedEndRef.current) {
                    setSelectedStart(s)
                } else {
                    setSelectedStart(s)
                    setSelectedEnd(e)
                }
            }

        });

        // 监听回车键
        const handleKeyDown = (e) => {
            if (e.altKey && e.key === 'Enter') {
                console.log("按下回车，当前 brush 区域为：", brushAreasRef.current);
            }
        };

        window.addEventListener("keydown", handleKeyDown);

        // 清理事件监听
        return () => {
            window.removeEventListener("keydown", handleKeyDown);
        };
    };

    useEffect(() => {
        console.info("====", chartRef.current?.getEchartsInstance)
        const cleanup = chartRef.current?.getEchartsInstance && onChartReady(chartRef.current.getEchartsInstance());
        return () => {
            cleanup?.();
        };
    }, []);

    const getLegends = () => {
        const legends: Array<string> = [];

        if (traceSeries && traceSeries.seriesDataList) {
            traceSeries.seriesDataList.forEach((seriesData) => {
                legends.push(seriesData.name);
            });
        }

        return legends;
    };

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
                        disabled: false,
                        focus: "series",
                    },
                    z: seriesData.z
                });
            });
        }

        return series;
    };

    const getXData = () => {
        if (traceSeries && traceSeries.xData) {
            return traceSeries.xData
        } else {
            return []
        }
    }

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
                // brush: {
                //     type: 'lineX'
                // },
                // dataZoom: {
                //     show: true,
                //     title: {
                //         zoom: "缩放",
                //         back: "还原",
                //     },
                //     yAxisIndex: "none",
                //     brushStyle: {
                //         color: "rgba(190, 190, 190, 0.5)",
                //     },
                // },
                saveAsImage: {show: true},
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

        // dataZoom: [
        //     {
        //         type: "inside",
        //         xAxisIndex: 0,
        //         moveOnMouseMove: "alt",
        //         zoomOnMouseWheel: "alt",
        //     },
        //     {
        //         type: "slider",
        //         xAxisIndex: 0,
        //         moveOnMouseMove: "alt",
        //         zoomOnMouseWheel: "alt",
        //         realtime: false,
        //     },
        // ],
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
            data: getXData()
        },

        yAxis: {},
        series: getSeries(),
    };


    return (
      <div ref={chartBoxRef}>
          <ReactEcharts ref={chartRef} option={option} notMerge={true} style={{height: 400}}/>
          <Slider start={start} setStart={setStart} end={end} setEnd={setEnd}/>
      </div>
    );
};

export default TracePanel;