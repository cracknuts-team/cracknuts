import React from "react";
import {useModelState} from "@anywidget/react";
import ReactEcharts from "echarts-for-react";

interface TraceSeries {
    color: string;
    name: string;
    emphasis: boolean;
    data: Array<number>;
    index: Array<number>;
    z: number;
}

const TracePanel: React.FC = () => {
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
                z: traceSeries.z
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
        },

        yAxis: {},
        series: getSeries(),
    };

    return (
        <div>
            <ReactEcharts option={option} notMerge={true} style={{height: 400}}/>
        </div>
    );
};

export default TracePanel;