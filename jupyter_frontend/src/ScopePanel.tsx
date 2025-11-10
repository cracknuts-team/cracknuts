import {useModel, useModelState} from "@anywidget/react";
import {Button, Form, Input, InputNumber, Radio, Select, Slider, Space, Spin} from "antd";
import ReactEcharts from "echarts-for-react";
import React, {useEffect, useRef, useState} from "react";
import {LinkOutlined, MinusCircleOutlined, PlusCircleOutlined} from "@ant-design/icons";
import {CheckboxChangeEvent} from "antd/es/checkbox";
import {FormattedMessage, useIntl} from "react-intl";
import type {ECharts, EChartsOption} from "echarts";
import {EChartsInstance} from "echarts-for-react/src/types.ts";

// interface SeriesData {
//     0: number[] | undefined;
//     1: number[] | undefined;
// }

interface TraceSeries {
    // dict[int, list[tuple[int, int]]]  ==> {channel: [(x1, y1), (x2, y2), ...]}
    0: Array<Array<number>> | undefined;
    1: Array<Array<number>> | undefined;
}

interface RangeData {
    0: number[];
    1: number[];
}

interface ScopePanelProperties {
    disable?: boolean;
}

const ScopePanel: React.FC<ScopePanelProperties> = ({disable = false}) => {

    const chartRef = useRef<ReactEcharts | null>(null);

    const [series] = useModelState<TraceSeries>("series");
    const [monitorStatus, setMonitorStatus] = useModelState<boolean>("monitor_status");
    const [lockScopeOperation] = useModelState<boolean>("lock_scope_operation");
    const [scopeStatus, setScopeStatus] = useModelState<number>("scope_status");
    const [monitorPeriod, setMonitorPeriod] = useModelState<number>("monitor_period")

    const [yRange] = useModelState<RangeData>("y_range");

    const [customRangeModel, setCustomRangeModel] = useState<boolean>(false)
    const [customC0YMin, setCustomC0YMin] = useState<number | undefined>(undefined)
    const [customC0YMax, setCustomC0YMax] = useState<number | undefined>(undefined)
    const [customC1YMin, setCustomC1YMin] = useState<number | undefined>(undefined)
    const [customC1YMax, setCustomC1YMax] = useState<number | undefined>(undefined)

    const [customC0YRangeLink, setCustomC0YRangeLink] = useState<boolean>(true)
    const [customC1YRangeLink, setCustomC1YRangeLink] = useState<boolean>(true)

    // const [customXRangeEnabled, setCustomXRangeEnabled] = useState<boolean>(false)
    const [customXMin, setCustomXMin] = useState<number | undefined>(undefined)
    const [customXMax, setCustomXMax] = useState<number | undefined>(undefined)

    const [xRangeBrushEnabled, setXRangeBrushEnabled] = useState<boolean>(false)

    const intl = useIntl();

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

    const setCustomC0YMinLink = (v: number) => {
        if (customC0YRangeLink) {
            const min = customC0YMin ? customC0YMin : 0
            const max = customC0YMax ? customC0YMax : 0
            const offset = v - min
            setCustomC0YMax(max + offset)
            setCustomC0YMin(v)
        } else {
            setCustomC0YMin(v)
        }
    };
    const setCustomC0YMaxLink = (v: number) => {
        if (customC0YRangeLink) {
            const max = customC0YMax ? customC0YMax : 0
            const min = customC0YMin ? customC0YMin : 0
            const offset = v - max
            setCustomC0YMin(min + offset)
            setCustomC0YMax(v)
        } else {
            setCustomC0YMax(v)
        }
    };
    const setCustomC1YMinLink = (v: number) => {
        if (customC1YRangeLink) {
            const min = customC1YMin ? customC1YMin : 0
            const max = customC1YMax ? customC1YMax : 0
            const offset = v - min
            setCustomC1YMax(max + offset)
            setCustomC1YMin(v)
        } else {
            setCustomC1YMin(v)
        }
    };
    const setCustomC1YMaxLink = (v: number) => {
        if (customC1YRangeLink) {
            const max = customC1YMax ? customC1YMax : 0
            const min = customC1YMin ? customC1YMin : 0
            const offset = v - max
            setCustomC1YMin(min + offset)
            setCustomC1YMax(v)
        } else {
            setCustomC1YMax(v)
        }
    };

    const colors = ["green", "red"];

    const option: object = {
        toolbox: {
            feature: {
                dataZoom: {
                    id: "toolboxDataZoom",
                    show: true,
                    title: {
                        zoom: intl.formatMessage({id: "cracker.scope.echarts.toolbox.dataZoom.zoom"}),
                        back: intl.formatMessage({id: "cracker.scope.echarts.toolbox.dataZoom.back"}),
                    },
                    xAxisIndex: 0,
                    yAxisIndex: false,
                    brushStyle: {
                        color: "rgba(144, 238, 144, 0.4)",
                    },
                    filterMode: "none",
                },
                saveAsImage: {
                    show: true,
                    title: intl.formatMessage({id: "cracker.scope.echarts.toolbox.saveAsImage"})
                },
            },
        },
        tooltip: {
            trigger: "axis",
            axisPointer: {
                type: "cross",
            },
        },
        animation: false,
        xAxis: {
            // gridIndex: 0,
            type: "value",
            axisLine: {
                onZero: false,
            },
            min: 'dataMin',
            max: 'dataMax'
        },
        dataZoom: [
            {
                type: "inside",
                moveOnMouseMove: "alt",
                zoomOnMouseWheel: "alt",
            },
        ],
        yAxis: getEchartsYAxis(),
        grid: {
            left: "40",
            right: "40",
            bottom: "40",
            top: 50,
        },
        series: [
            {
                name: "channel 1",
                data: series["1"] ? series["1"] : undefined,
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
            },
            {
                name: "channel 0",
                data: series["0"] ? series["0"] : undefined,
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
            }
        ]
    };

    function getEchartsYAxis() {
        const yAxis = [];

        yAxis.push({
            type: "value",
            position: "left",
            // alignTicks: true,
            axisLine: {
                show: true,
                lineStyle: {
                    color: colors[0],
                },
            },
            min: customC0YMin ? customC0YMin : undefined,
            max: customC0YMin ? customC0YMax : undefined,
        });

        yAxis.push({
            type: "value",
            position: "right",
            // alignTicks: true,
            axisLine: {
                show: true,
                lineStyle: {
                    color: colors[1],
                },
            },
            min: customRangeModel ? customC1YMin : undefined,
            max: customRangeModel ? customC1YMax : undefined,
        });

        return yAxis;
    }

    const enableXRangeBrush = (enabled: boolean = true) => {
        const chartInstance = chartRef.current?.getEchartsInstance();
        if (chartInstance) {
            chartInstance.dispatchAction({
                type: "takeGlobalCursor",
                key: enabled ? "dataZoomSelect" : null,
                dataZoomSelectActive: enabled,
            });
        }
    };

    const setZoomRange = (param: { batch: { startValue: number, endValue: number }[] }) => {
        if (param.batch) {
            const {startValue, endValue} = param.batch[0]
            setCustomXMin(startValue);
            setCustomXMax(endValue)
        }
    }

    const setCustomXRangeMin = (value: number) => {
        const chartInstance = chartRef.current?.getEchartsInstance();
        if (chartInstance) {
            chartInstance.dispatchAction({
                type: "dataZoom",
                startValue: value,
            });
        }
        setCustomXMin(value)
    };

    const setCustomXRangeMax = (value: number) => {
        const chartInstance = chartRef.current?.getEchartsInstance();
        if (chartInstance) {
            chartInstance.dispatchAction({
                type: "dataZoom",
                endValue: value,
            });
        }
        setCustomXMax(value);
    };

    const onChartReady = (instance: EChartsInstance) => {
        instance.on('dataZoom', setZoomRange);
    };

    const chARangeIncrease = () => {
        if (customC0YMax == undefined || customC0YMin == undefined) {
            return
        }
        const range = customC0YMax - customC0YMin
        const size = range * 0.1

        setCustomC0YMin(Math.floor(customC0YMin - size));
        setCustomC0YMax(Math.ceil(customC0YMax + size));
    };

    const chARangeDecrease = () => {
        if (customC0YMax == undefined || customC0YMin == undefined) {
            return
        }
        const range = customC0YMax - customC0YMin
        const size = range * 0.1

        setCustomC0YMin(Math.ceil(customC0YMin + size));
        setCustomC0YMax(Math.floor(customC0YMax - size));
    };

    const chBRangeIncrease = () => {
        if (customC1YMax == undefined || customC1YMin == undefined) {
            return
        }
        const range = customC1YMax - customC1YMin
        const size = range * 0.1

        setCustomC1YMin(Math.floor(customC1YMin - size));
        setCustomC1YMax(Math.ceil(customC1YMax + size));
    };

    const chBRangeDecrease = () => {
        if (customC1YMax == undefined || customC1YMin == undefined) {
            return
        }
        const range = customC1YMax - customC1YMin
        const size = range * 0.1

        setCustomC1YMin(Math.ceil(customC1YMin + size));
        setCustomC1YMax(Math.floor(customC1YMax - size));
    };

    const model = useModel();

    useEffect(() => {

        const updateCustomRangeOnCustom = () => {
            const yr = model.get("y_range")
            const c0 = yr["0"];
            const c1 = yr["1"];
            if (customRangeModel) {
                if (c0[0] && !customC0YMin && !customC0YMax) {
                    setCustomC0YMin(c0[0])
                    setCustomC0YMax(c0[1])
                }
                if (c1[0] && !customC1YMin && !customC1YMax) {
                    setCustomC1YMin(c1[0])
                    setCustomC1YMax(c1[1])
                }
            } else {
                if (!c0[0]) {
                    setCustomC0YMin(undefined)
                    setCustomC0YMax(undefined)
                }
                if (!c1[0]) {
                    setCustomC1YMin(undefined)
                    setCustomC1YMax(undefined)
                }
            }
        };
        model.on("change:y_range", updateCustomRangeOnCustom);

        return () => {
            model.off("change:y_range", updateCustomRangeOnCustom);
        };

    });

    // ============== overview ================
    // interface TraceSeries {
    //     // dict[int, list[tuple[int, int]]]  ==> {channel: [(x1, y1), (x2, y2), ...]}
    //     0: Array<Array<number>> | undefined;
    //     1: Array<Array<number>> | undefined;
    //     percentRange: Array<number>,
    //     range: Array<number>,
    // }

    interface BrushEndParams {
        areas?: {
            coordRange?: [number, number];
        }[];
    }

    // const [overviewSelectedRange, setOverviewSelectedRange] = useModelState<Array<number>>("overview_select_range");
    const [selectedRange, setSelectedRange] = useModelState<Array<number>>("selected_range");
    const [overviewSeries] = useModelState<TraceSeries>("overview_series");
    const [overviewRange, setOverviewRange] = useState<Array<number> | null>(null);

    useEffect(() => {
        setOverviewRange(selectedRange)
    }, [selectedRange]);

    const overviewChartRef = useRef<ReactEcharts>(null);
    const onOverviewChartReady = (chart: ECharts) => {
        chart.on("brushEnd", (params) => {
            const brushParams = params as BrushEndParams;
            if (brushParams && brushParams.areas && brushParams.areas.length > 0
                && brushParams.areas[0].coordRange
                && brushParams.areas[0].coordRange.length == 2) {
                const [newStart, newEnd] = brushParams.areas[0].coordRange
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


    const [overviewOption, setOverviewOption] = useState<EChartsOption>({
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
        series: [],
        yAxis: [{
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
        }, {
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
        }],
        xAxis: {
            type: "value",
            axisTick: {
                show: false,
            },
            axisLine: {
                show: false,
            },
            axisLabel: {
                show: false,
            },
            min: 'dataMin',
            max: 'dataMax'
        },
    });

    useEffect(() => {
        setOverviewOption({
            ...overviewOption,
            series: [
                {
                    name: "channel 1",
                    data: overviewSeries["1"] ? overviewSeries["1"] : undefined,
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
                },
                {
                    name: "channel 0",
                    data: overviewSeries["0"] ? overviewSeries["0"] : undefined,
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
                }
            ]
        });
    }, [overviewSeries]);

    return (
        <Spin indicator={<span></span>} spinning={disable}>
            {/* eslint @typescript-eslint/no-unused-vars: "off" */}
            <Form layout={"inline"}>
                <Form.Item>
                    <Radio.Group
                        value={scopeStatus}
                        buttonStyle="solid"
                        onChange={(e: CheckboxChangeEvent) => {
                            setScopeStatus(Number(e.target.value));
                        }}
                        size={"small"}
                        disabled={lockScopeOperation}
                        style={{minWidth: 200}}
                    >
                        <Radio.Button value={0}>
                            <FormattedMessage id={"cracker.scope.stop"}/>
                        </Radio.Button>
                        <Radio.Button value={1}>
                            <FormattedMessage id={"cracker.scope.run"}/>
                        </Radio.Button>
                        <Radio.Button value={2}>
                            <FormattedMessage id={"cracker.scope.single"}/>
                        </Radio.Button>
                        <Radio.Button value={3}>
                            <FormattedMessage id={"cracker.scope.repeat"}/>
                        </Radio.Button>
                    </Radio.Group>
                </Form.Item>
                <Form.Item>
                    <Button size={"small"} type={monitorStatus ? "primary" : "default"}
                            onClick={() => {
                                setMonitorStatus(!monitorStatus);
                            }}
                    ><FormattedMessage id={"cracker.scope.monitor"}/></Button>
                </Form.Item>
                <Form.Item>
                    <Button size={"small"} type={!customRangeModel ? "default" : "primary"}
                            onClick={() => {
                                setCustomC0YMin(yRange[0][0]);
                                setCustomC0YMax(yRange[0][1]);
                                setCustomC1YMin(yRange[1][0]);
                                setCustomC1YMax(yRange[1][1]);
                                setCustomRangeModel(!customRangeModel);
                            }}>
                        <FormattedMessage id={"cracker.scope.customRange"}/>
                    </Button>
                </Form.Item>
                <Form.Item>
                    <Space.Compact>
                        <Button size={"small"} disabled={!customRangeModel}
                                onClick={chARangeDecrease}><MinusCircleOutlined/></Button>
                        <Input size={"small"} placeholder={"CH A"} disabled className="site-input-split"
                               style={{width: 50, textAlign: 'center', pointerEvents: 'none'}}/>
                        <InputNumber disabled={!customRangeModel}
                                     placeholder={intl.formatMessage({id: "cracker.scope.customRange.min"})}
                                     size={"small"}
                                     value={customC0YMin} onChange={(v) => {
                            setCustomC0YMinLink(Number(v))
                        }} changeOnWheel/>
                        <Button type={customC0YRangeLink ? "primary" : "default"}
                                size={"small"}
                                disabled={!customRangeModel}
                                onClick={() => {
                                    setCustomC0YRangeLink(!customC0YRangeLink)
                                }}>
                            <LinkOutlined/>
                        </Button>
                        <InputNumber disabled={!customRangeModel}
                                     placeholder={intl.formatMessage({id: "cracker.scope.customRange.max"})}
                                     size={"small"}
                                     value={customC0YMax} onChange={(v) => {
                            setCustomC0YMaxLink(Number(v))
                        }} changeOnWheel/>
                        <Button size={"small"} disabled={!customRangeModel}
                                onClick={chARangeIncrease}><PlusCircleOutlined/></Button>
                    </Space.Compact>
                </Form.Item>
                <Form.Item>
                    <Space.Compact>
                        <Button size={"small"} disabled={!customRangeModel}
                                onClick={chBRangeDecrease}><MinusCircleOutlined/></Button>
                        <Input size={"small"} placeholder={"CH B"} disabled className="site-input-split"
                               style={{width: 50, borderRight: 0, pointerEvents: 'none'}}/>
                        <InputNumber disabled={!customRangeModel}
                                     placeholder={intl.formatMessage({id: "cracker.scope.customRange.min"})}
                                     size={"small"}
                                     value={customC1YMin} onChange={(v) => {
                            setCustomC1YMinLink(Number(v))
                        }} changeOnWheel/>
                        <Button type={customC1YRangeLink ? "primary" : "default"}
                                size={"small"}
                                disabled={!customRangeModel}
                                onClick={() => {
                                    setCustomC1YRangeLink(!customC1YRangeLink)
                                }}>
                            <LinkOutlined/>
                        </Button>
                        <InputNumber disabled={!customRangeModel}
                                     placeholder={intl.formatMessage({id: "cracker.scope.customRange.max"})}
                                     size={"small"}
                                     value={customC1YMax} onChange={(v) => {
                            setCustomC1YMaxLink(Number(v))
                        }} changeOnWheel/>
                        <Button size={"small"} disabled={!customRangeModel}
                                onClick={chBRangeIncrease}><PlusCircleOutlined/></Button>
                    </Space.Compact>
                </Form.Item>
                <Form.Item>
                    <Space.Compact>
                        <Button size={"small"} onClick={() => {
                            enableXRangeBrush(!xRangeBrushEnabled)
                            setXRangeBrushEnabled(!xRangeBrushEnabled);
                        }} type={xRangeBrushEnabled ? "primary" : "default"}
                        ><FormattedMessage id={"cracker.scope.zoomBrush"}/></Button>
                        <Button size={"small"}><FormattedMessage id={"cracker.scope.zoomBrush.customRange"}/></Button>
                        <InputNumber size={"small"} changeOnWheel value={customXMin} onChange={(v) => {
                            setCustomXRangeMin(Number(v))
                        }}/>
                        <InputNumber size={"small"} changeOnWheel value={customXMax} onChange={(v) => {
                            setCustomXRangeMax(Number(v))
                        }}/>
                    </Space.Compact>
                </Form.Item>
                <Form.Item label={intl.formatMessage({id: "cracker.scope.monitorPeriod"})}>
                    <Select size={"small"} style={{width: 70}} options={[
                        {value: 1, label: "1s"},
                        {value: 2, label: "2s"},
                        {value: 3, label: "3s"},
                        {value: 4, label: "4s"},
                        {value: 5, label: "5s"},
                        {value: 10, label: "10s"},
                        {value: 15, label: "15s"},
                        {value: 20, label: "20s"},
                        {value: 25, label: "25s"},
                        {value: 30, label: "30s"},
                    ]} onChange={setMonitorPeriod} value={monitorPeriod}/>
                </Form.Item>
            </Form>
            <div style={{
                height: 400,
                borderRadius: 3,
            }}>
                <ReactEcharts option={option} ref={chartRef} onChartReady={onChartReady}
                              style={{
                                  marginTop: 5,
                                  padding: "8 8 0 8",
                                  height: 350
                              }}
                />
                <ReactEcharts ref={overviewChartRef} option={overviewOption} notMerge={true} style={{
                    height: 40,
                    marginRight: 40,
                    marginLeft: 40,
                    marginBottom: 40
                }}/>
            </div>

            <Slider start={sliderPercentRange[0]} end={sliderPercentRange[1]} onChangeFinish={(s, e) => {
                setPercentRange([s, e]);
                setOverviewRange(s, e)
            }} onChange={(s, e) => {
                setOverviewRange(s, e);
            }}/>
        </Spin>
    );
};

export default ScopePanel;
