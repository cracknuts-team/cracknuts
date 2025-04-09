import React, {useEffect, useRef} from "react";
import {useModelState} from "@anywidget/react";
import ReactEcharts from "echarts-for-react";

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
    xMin: number;
    xMax: number;
    totalXMin: number;
    totalXMax: number;
    yMin: number;
    yMax: number;
    totalYMin: number;
    totalYMax: number;
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

const TracePanel: React.FC = () => {
    const [traceSeries] = useModelState<TraceSeries>("trace_series");
    const [, setChartSize] = useModelState<ChartSize>("chart_size");

    const chartRef = useRef<HTMLDivElement>(null)

    useEffect(() => {
        console.log("==", chartRef.current);
        if (!chartRef.current || typeof ResizeObserver === 'undefined') return

        const observer = new ResizeObserver(([entry]) => {
          const { width, height } = entry.contentRect
          setChartSize({
              width: width,
              height: height
          })
        })

        observer.observe(chartRef.current)

        return () => observer.disconnect()
    }, [])

    console.info(traceSeries)

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
                saveAsImage: {show: true},
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
            data: getXData()
        },

        yAxis: {},
        series: getSeries(),
    };

    console.info(option)

    return (
        <div ref={chartRef}>
            <ReactEcharts option={option} notMerge={true} style={{height: 400}}/>
            <so
        </div>
    );
};

export default TracePanel;