import React, {useEffect, useRef} from "react";
import {useModelState} from "@anywidget/react";
import ReactEcharts from "echarts-for-react";
import Slider from "@/Slider.tsx";
import type {ECharts} from "echarts";

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

    const [, setSelectedRange] = useModelState<Array<number>>("selected_range");
    const [, setPercentRange] = useModelState<Array<number>>("percent_range");

    const [traceSeries] = useModelState<TraceSeries>("trace_series");
    const [, setChartSize] = useModelState<ChartSize>("chart_size");

    const chartBoxRef = useRef<HTMLDivElement>(null)

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

    const onChartReady = (chart: ECharts) => {
        chart.on("brushEnd", (params) => {
            const brushParams = params as BrushEndParams;
            if (brushParams && brushParams.areas && brushParams.areas.length > 0 && brushParams.areas[0].coordRange && brushParams.areas[0].coordRange.length == 2) {
                const [new_start, new_end] = brushParams.areas[0].coordRange

                setSelectedRange([new_start, new_end])
            }

        });
    };

    useEffect(() => {
        if (chartRef.current?.getEchartsInstance) {
            onChartReady(chartRef.current.getEchartsInstance());
        }
        return () => {}
    }, []);

    // const getLegends = () => {
    //     const legends: Array<string> = [];
    //
    //     if (traceSeries && traceSeries.seriesDataList) {
    //         traceSeries.seriesDataList.forEach((seriesData) => {
    //             legends.push(seriesData.name);
    //         });
    //     }
    //
    //     return legends;
    // };

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
        // legend: {
        //     data: getLegends(),
        //     type: "scroll",
        //     pageButtonPosition: "start",
        //     orient: "horizontal",
        //     // left: 115,
        //     // right: 125,
        //     top: 30,
        //     // bottom: 10,
        // },
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
          <Slider start={traceSeries.percentRange[0]} end={traceSeries.percentRange[1]} onChange={(s, e) => {setPercentRange([s, e])}}/>
      </div>
    );
};

export default TracePanel;