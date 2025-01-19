import {useModel, useModelState} from "@anywidget/react";
import {Button, Input, InputNumber, Radio, Space, Spin} from "antd";
import ReactEcharts from "echarts-for-react";
import React, {useEffect, useRef, useState} from "react";
import {LinkOutlined, MinusCircleOutlined, PlusCircleOutlined} from "@ant-design/icons";
import {CheckboxChangeEvent} from "antd/es/checkbox";

interface SeriesData {
    1: number[] | undefined;
    2: number[] | undefined;
}

interface RangeData {
    1: number[];
    2: number[];
}

interface ScopePanelProperties {
    disable?: boolean;
}

const ScopePanel: React.FC<ScopePanelProperties> = ({disable = false}) => {

     const chartRef = useRef<ReactEcharts | null>(null);

    const [seriesData] = useModelState<SeriesData>("series_data");
    const [monitorStatus, setMonitorStatus] = useModelState<boolean>("monitor_status");
    const [lockScopeOperation] = useModelState<boolean>("lock_scope_operation");
    const [scopeStatus, setScopeStatus] = useModelState<number>("scope_status");

    const [yRange] = useModelState<RangeData>("y_range");

    const [customRangeModel, setCustomRangeModel] = useState<boolean>(false)
    const [customC1YMin, setCustomC1YMin] = useState<number | undefined>(undefined)
    const [customC1YMax, setCustomC1YMax] = useState<number | undefined>(undefined)
    const [customC2YMin, setCustomC2YMin] = useState<number | undefined>(undefined)
    const [customC2YMax, setCustomC2YMax] = useState<number | undefined>(undefined)

    const [customC1YRangeLink, setCustomC1YRangeLink] = useState<boolean>(true)
    const [customC2YRangeLink, setCustomC2YRangeLink] = useState<boolean>(true)

    // const [customXRangeEnabled, setCustomXRangeEnabled] = useState<boolean>(false)
    const [customXMin, setCustomXMin] = useState<number | undefined>(undefined)
    const [customXMax, setCustomXMax] = useState<number | undefined>(undefined)

    const [xRangeBrushEnabled, setXRangeBrushEnabled] = useState<boolean>(false)


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
    const setCustomC2YMinLink = (v: number) => {
        if (customC2YRangeLink) {
            const min = customC2YMin ? customC2YMin : 0
            const max = customC2YMax ? customC2YMax : 0
            const offset = v - min
            setCustomC2YMax(max + offset)
            setCustomC2YMin(v)
        } else {
            setCustomC2YMin(v)
        }
    };
    const setCustomC2YMaxLink = (v: number) => {
        if (customC2YRangeLink) {
            const max = customC2YMax ? customC2YMax : 0
            const min = customC2YMin ? customC2YMin : 0
            const offset = v - max
            setCustomC2YMin(min + offset)
            setCustomC2YMax(v)
        } else {
            setCustomC2YMax(v)
        }
    };

    const colors = ["green", "red"];

    const option: object = {
        toolbox: {
        //   show: false,
        feature: {
          dataZoom: {
            id: "toolboxDataZoom",
            show: true,
            xAxisIndex: 0,
            yAxisIndex: false,
            brushStyle: {
              color: "rgba(144, 238, 144, 0.4)",
            },
            filterMode: "none",
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
            type: "category",
            axisLine: {
                onZero: false,
            },
        },
        dataZoom: [
            {
                type: "inside",
                moveOnMouseMove: "alt",
                zoomOnMouseWheel: "alt",
            },
            {
                type: "slider",
            },
        ],
        yAxis: getEchartsYAxis(),
        series: [
          {
                name: "channel 2",
                data: seriesData["2"] ? seriesData["2"] : undefined,
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
                name: "channel 1",
                data: seriesData["1"] ? seriesData["1"] : undefined,
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
            alignTicks: true,
            axisLine: {
                show: true,
                lineStyle: {
                    color: colors[0],
                },
            },
            min: customC1YMin ? customC1YMin : undefined,
            max: customC1YMin ? customC1YMax : undefined,
        });

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
            min: customRangeModel ? customC2YMin : undefined,
            max: customRangeModel ? customC2YMax : undefined,
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

    const setZoomRange = (param: any) => {
        console.log(param);
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

    const onChartReady = (instance: any) => {
        instance.on('dataZoom', setZoomRange);
    };

    const chARangeIncrease = () => {
      if (customC1YMax == undefined || customC1YMin == undefined) {
        return
      }
      const range = customC1YMax - customC1YMin
      const size = range * 0.1

      setCustomC1YMin(Math.floor(customC1YMin - size));
      setCustomC1YMax(Math.ceil(customC1YMax + size));
    };

    const chARangeDecrease = () => {
      if (customC1YMax == undefined || customC1YMin == undefined) {
        return
      }
      const range = customC1YMax - customC1YMin
      const size = range * 0.1

      setCustomC1YMin(Math.ceil(customC1YMin + size));
      setCustomC1YMax(Math.floor(customC1YMax - size));
    };

    const chBRangeIncrease = () => {
      if (customC2YMax == undefined || customC2YMin == undefined) {
        return
      }
      const range = customC2YMax - customC2YMin
      const size = range * 0.1

      setCustomC2YMin(Math.floor(customC2YMin - size));
      setCustomC2YMax(Math.ceil(customC2YMax + size));
    };

    const chBRangeDecrease = () => {
       if (customC2YMax == undefined || customC2YMin == undefined) {
        return
      }
      const range = customC2YMax - customC2YMin
      const size = range * 0.1

      setCustomC2YMin(Math.ceil(customC2YMin + size));
      setCustomC2YMax(Math.floor(customC2YMax - size));
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
            } else {
                if (!c1[0]) {
                    setCustomC1YMin(undefined)
                    setCustomC1YMax(undefined)
                }
                if (!c2[0]) {
                    setCustomC2YMin(undefined)
                    setCustomC2YMax(undefined)
                }
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

                <Radio.Group
                    value={scopeStatus}
                    buttonStyle="solid"
                    onChange={(e: CheckboxChangeEvent) => {
                        setScopeStatus(Number(e.target.value));
                    }}
                    size={"small"}
                    disabled={lockScopeOperation}
                >
                    <Radio.Button value={0}>
                        停止
                    </Radio.Button>
                    <Radio.Button value={1}>
                        运行
                    </Radio.Button>
                    <Radio.Button value={2}>
                        单次
                    </Radio.Button>
                    <Radio.Button value={3}>
                        重复
                    </Radio.Button>
                </Radio.Group>

                <Button size={"small"} type={monitorStatus ? "primary" : "default"}
                        onClick={() => {
                            setMonitorStatus(!monitorStatus);
                        }}
                >监视</Button>
                <Button size={"small"} type={!customRangeModel ? "default" : "primary"}
                        onClick={() => {
                          console.error(chartRef.current)
                            setCustomC1YMin(yRange[1][0]);
                            setCustomC1YMax(yRange[1][1]);
                            setCustomC2YMin(yRange[2][0]);
                            setCustomC2YMax(yRange[2][1]);
                            setCustomRangeModel(!customRangeModel);
                        }}>
                    指定区间
                </Button>
                <Space.Compact>
                    <Button size={"small"} disabled={!customRangeModel} onClick={chARangeDecrease}><MinusCircleOutlined /></Button>
                    <Input size={"small"} placeholder={"CH A"} disabled className="site-input-split"
                           style={{width: 50, textAlign: 'center', pointerEvents: 'none'}}/>
                    <InputNumber disabled={!customRangeModel} placeholder={"下限"}
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
                    <InputNumber disabled={!customRangeModel} placeholder={"上限"}
                                 size={"small"}
                                 value={customC1YMax} onChange={(v) => {
                        setCustomC1YMaxLink(Number(v))
                    }} changeOnWheel/>
                   <Button size={"small"} disabled={!customRangeModel} onClick={chARangeIncrease}><PlusCircleOutlined /></Button>
                </Space.Compact>
                <Space.Compact>
                  <Button size={"small"} disabled={!customRangeModel} onClick={chBRangeDecrease}><MinusCircleOutlined /></Button>
                    <Input size={"small"} placeholder={"CH B"} disabled className="site-input-split"
                           style={{width: 50, borderRight: 0, pointerEvents: 'none'}}/>
                    <InputNumber disabled={!customRangeModel} placeholder={"下限"}
                                 size={"small"}
                                 value={customC2YMin} onChange={(v) => {
                        setCustomC2YMinLink(Number(v))
                    }} changeOnWheel/>
                    <Button type={customC2YRangeLink ? "primary" : "default"}
                            size={"small"}
                            disabled={!customRangeModel}
                            onClick={() => {
                                setCustomC2YRangeLink(!customC2YRangeLink)
                            }}>
                        <LinkOutlined/>
                    </Button>
                    <InputNumber disabled={!customRangeModel} placeholder={"上限"}
                                 size={"small"}
                                 value={customC2YMax} onChange={(v) => {
                        setCustomC2YMaxLink(Number(v))
                    }} changeOnWheel/>
                   <Button size={"small"} disabled={!customRangeModel} onClick={chBRangeIncrease}><PlusCircleOutlined /></Button>
                </Space.Compact>
                <Space.Compact>
                    <Button size={"small"} onClick={() => {
                        enableXRangeBrush(!xRangeBrushEnabled)
                        setXRangeBrushEnabled(!xRangeBrushEnabled);
                    }} type = {xRangeBrushEnabled ? "primary" : "default"}
                    >框选放大</Button>
                    <Button size={"small"}>指定区间</Button>
                    <InputNumber size={"small"} changeOnWheel value={customXMin} onChange={(v) => {
                        setCustomXRangeMin(Number(v))
                    }}/>
                    <InputNumber size={"small"} changeOnWheel value={customXMax} onChange={(v) => {
                        setCustomXRangeMax(Number(v))
                    }}/>
                </Space.Compact>
            </Space>
            <ReactEcharts option={option} ref={chartRef} onChartReady = {onChartReady}
                          style={{
                              height: 550, marginTop: 5, padding: 8,
                              borderRadius: 3,
                              boxShadow: "inset 2px 2px 10px rgba(0, 0, 0, 0.1), inset -2px -2px 10px rgba(0, 0, 0, 0.1)"
                          }}/>
        </Spin>
    );
};

export default ScopePanel;
