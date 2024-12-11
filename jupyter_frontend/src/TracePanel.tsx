import {useModel, useModelState} from "@anywidget/react";
import {Button, Input, InputNumber, Select, Space, Spin} from "antd";
import ReactEcharts from "echarts-for-react";
import React, {useEffect, useState} from "react";

interface SeriesData {
    1: number[] | undefined;
    2: number[] | undefined;
}

interface RangeData {
    1: number[];
    2: number[];
}

interface TraceMonitorPanelProperties {
    disable?: boolean;
}

const TraceMonitorPanel: React.FC<TraceMonitorPanelProperties> = ({disable = false}) => {
    const [seriesData] = useModelState<SeriesData>("series_data");
    const [monitorStatus, setMonitorStatus] = useModelState<boolean>("monitor_status");
    // const [customRangeModel, setCustomRangeModel] = useModelState<boolean>("custom_range_model");
    // const [combineYRange, setCombineYRange] = useModelState<boolean>("combine_y_range");
    const [yRange] = useModelState<RangeData>("y_range");
    // const [customYRange, setCustomYRange] = useModelState<RangeData>("custom_y_range");

    const [customRangeModel, setCustomRangeModel] = useState<boolean>(false)
    const [customC1YMin, setCustomC1YMin] = useState<number|undefined>(undefined)
    const [customC1YMax, setCustomC1YMax] = useState<number|undefined>(undefined)
    const [customC2YMin, setCustomC2YMin] = useState<number|undefined>(undefined)
    const [customC2YMax, setCustomC2YMax] = useState<number|undefined>(undefined)

    const colors = ["green", "red"];

    const option: object = {
        tooltip: {
            trigger: "axis",
            axisPointer: {
                type: "cross",
            },
        },
        grid: [{
            left: "80",
            right: "80",
            top: "40",
            bottom: "80",
            // show: false
        }, {
            left: "80",
            right: "80",
            top: "40",
            bottom: "80",
            // show: false
        }],
        animation: false,
        xAxis: [{
            gridIndex: 0,
            type: "category",
            axisLine: {
                onZero: false,
            },
        },{
            gridIndex: 1,
            type: "category",
            axisLine: {
                onZero: false,
            },
        }],
        dataZoom: getDataZoom(),
        yAxis: getEchartsYAxis(),
        series: getEchartsSeries(seriesData)
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

    function getEchartsYAxis() {
        const yAxis = [];

        yAxis.push({
            gridIndex: 0,
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
            min: customC1YMin ? customC1YMin : yRange[1][0],
            max: customC1YMin ? customC1YMax : yRange[1][1],
            // interval: yRange[1][2],
            minInterval: 1,
            splitLine: {
                show: false
            },
        });

        yAxis.push({
            gridIndex: 1,
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
            min: customRangeModel ? customC2YMin : yRange[2][0],
            max: customRangeModel ? customC2YMax : yRange[2][1],
            // interval: yRange[2][2],
            minInterval: 1,
            splitLine: {
                show: false
            },
        });

        return yAxis;
    }

    function getEchartsSeries(seriesData: SeriesData) {

        const series = [];

        if (seriesData["1"]) {
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
                xAxisIndex: 0,
                yAxisIndex: 0,
            });
        }

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
                xAxisIndex: 1,
                yAxisIndex: 1,
            });
        }

        return series;
    };

    const model = useModel();

    useEffect(() => {

        const updateCustomRangeOnCustom = () => {
            const yr = model.get("y_range")
            const c1 = yr["1"];
            const c2 = yr["2"];
            if (customRangeModel) {
                if (c1[0] && !customC1YMin && !customC1YMax) {
                    setCustomC1YMin(c1[0])
                    setCustomC1YMax(c1[1])
                }
                if (c2[0] && !customC2YMin && !customC2YMax) {
                    setCustomC2YMin(c2[0])
                    setCustomC2YMax(c2[1])
                }
            }
            if (!c1[0]) {
                setCustomC1YMin(undefined)
                setCustomC1YMax(undefined)
            }
            if (!c2[0]) {
                setCustomC2YMin(undefined)
                setCustomC2YMax(undefined)
            }
        };
        model.on("change:y_range", updateCustomRangeOnCustom);

        return () => {
            model.off("change:y_range", updateCustomRangeOnCustom);
        };

    });

    return (
        <Spin indicator={<span></span>} spinning={disable}>
            {/* eslint @typescript-eslint/no-unused-vars: "off" */}
            <Space>
                <Button size={"small"} type={monitorStatus ? "primary" : "default"}
                        onClick={() => setMonitorStatus(!monitorStatus)}>监视</Button>
                <Button size={"small"} type={!customRangeModel ? "default" : "primary"}
                        onClick={() => {
                            setCustomC1YMin(yRange[1][0]);
                            setCustomC1YMax(yRange[1][1]);
                            setCustomC2YMin(yRange[2][0]);
                            setCustomC2YMax(yRange[2][1]);
                            setCustomRangeModel(!customRangeModel);
                        }}>
                    指定区间
                </Button>
                {/*<Button size={"small"} type={combineYRange ? "primary" : "default"}*/}
                {/*        onClick={() => setMonitorStatus(!monitorStatus)}>共同坐标</Button>*/}
                <Space.Compact>
                    <Input size={"small"} placeholder={"CH A"} disabled className="site-input-split"
                           style={{width: 50, textAlign: 'center', pointerEvents: 'none'}}/>
                    <InputNumber disabled={!customRangeModel} placeholder={"下限"}
                                 size={"small"}
                                 value={customC1YMin} onChange={(v) => {setCustomC1YMin(Number(v))}} changeOnWheel/>
                    <Input size={"small"} placeholder={"~"} disabled className="site-input-split"
                           style={{width: 30, textAlign: 'center', pointerEvents: 'none'}}/>
                    <InputNumber disabled={!customRangeModel} placeholder={"上限"}
                                 size={"small"}
                                 value={customC1YMax} onChange={(v) => {setCustomC1YMax(Number(v))}} changeOnWheel/>
                    <Select defaultValue="0" disabled={!customRangeModel} size={"small"}>
                        <Select.Option value="0">mV</Select.Option>
                        {/*<Select.Option value="1">V</Select.Option>*/}
                    </Select>
                </Space.Compact>
                <Space.Compact>
                    <Input size={"small"} placeholder={"CH B"} disabled className="site-input-split"
                           style={{width: 50, borderRight: 0, pointerEvents: 'none'}}/>
                    <InputNumber disabled={!customRangeModel} placeholder={"下限"}
                                 size={"small"}
                                 value={customC2YMin} onChange={(v) => {setCustomC2YMin(Number(v))}} changeOnWheel/>
                    <Input size={"small"} placeholder={"~"} disabled className="site-input-split"
                           style={{width: 30,  borderRight: 0, pointerEvents: 'none',  textAlign: 'center'}}/>
                    <InputNumber disabled={!customRangeModel} placeholder={"上限"}
                                 size={"small"}
                                 value={customC2YMax} onChange={(v) => {setCustomC2YMax(Number(v))}} changeOnWheel/>
                    <Select defaultValue="0" disabled={!customRangeModel} size={"small"}>
                        <Select.Option value="0">mV</Select.Option>
                        {/*<Select.Option value="1">V</Select.Option>*/}
                    </Select>
                </Space.Compact>
            </Space>
            <ReactEcharts option={option} notMerge={true}
                          style={{
                              height: 350, marginTop: 5, padding: 8,
                              borderRadius: 3,
                              boxShadow: "inset 2px 2px 10px rgba(0, 0, 0, 0.1), inset -2px -2px 10px rgba(0, 0, 0, 0.1)"
                          }}/>
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

export {TraceMonitorPanel, TraceAnalysisPanel};
