import React, {useEffect, useRef, useState} from "react";
import {useModel, useModelState} from "@anywidget/react";
import ReactEcharts from "echarts-for-react";
import Slider from "@/Slider.tsx";
import {ECharts, EChartsOption} from "echarts";
import {useIntl} from "react-intl";
import {Tabs} from "antd";
import {CompatibilityProps} from "antd/es/tabs";
import type {Tab} from 'rc-tabs/lib/interface';
import GeneralControl, {TraceIndex, TraceIndexFilter} from "@/components/trace/GeneralControl.tsx";
import ShiftControl, {TraceInfo} from "@/components/trace/ShiftControl.tsx";

interface SeriesData {
    color: string;
    name: string;
    data: Array<Array<number>>;
    z: number;
    realSampleCount: number
}

interface TraceSeries {
    seriesDataList: Array<SeriesData>,
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
    const [showRange,] = useModelState<Array<number>>("show_range");
    const [maxRange,] = useModelState<Array<number>>("max_range");
    const [, setOverviewSelectedRange] = useModelState<Array<number>>("overview_select_range");
    const [, setPercentRange] = useModelState<Array<number>>("percent_range");

    const [traceSeries] = useModelState<TraceSeries>("trace_series");
    const [, setChartSize] = useModelState<ChartSize>("chart_size");

    const chartBoxRef = useRef<HTMLDivElement>(null)

    const [overviewTraceSeries] = useModelState<TraceSeries>("overview_trace_series");

    const [overviewRange, _setOverviewRange] = useState<Array<number>>(overviewTraceSeries.range)

    const setOverviewRange = (percentStart: number, percentEnd: number) => {
        if (overviewTraceSeries && overviewTraceSeries.seriesDataList && overviewTraceSeries.seriesDataList.length > 0) {
            const seriesDataLen = overviewTraceSeries.seriesDataList[0].realSampleCount
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
                let [newStart, newEnd] = brushParams.areas[0].coordRange
                newStart = Math.max(Math.floor(newStart), maxRange[0])
                newEnd = Math.min(Math.ceil(newEnd), maxRange[1])
                setSelectedRange([newStart, newEnd])
                chart.dispatchAction({
                    type: 'brush',
                    areas: []
                })
            }
        });
        chart.dispatchAction({
            type: 'takeGlobalCursor',
            key: 'brush',
            brushOption: {
                brushType: 'lineX',
                brushMode: 'single',
            }
        });
    };

    // useEffect(() => {
    //     if (chartRef.current?.getEchartsInstance) {
    //         onChartReady(chartRef.current.getEchartsInstance());
    //     }
    //     return () => {
    //     }
    // }, []);

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

    // const getXData = () => {
    //   if (traceSeries && traceSeries.xData) {
    //     return traceSeries.xData
    //   } else {
    //     return []
    //   }
    // }

    // const getOverviewXData = () => {
    //   if (overviewTraceSeries && overviewTraceSeries.xData) {
    //     return overviewTraceSeries.xData
    //   } else {
    //     return []
    //   }
    // };

    type TooltipFormatterParam = {
        seriesId: string;
        seriesName: string;
        seriesIndex: number;
        marker: string;
        value: Array<number>;
        axisValue?: string | number;
    }

    const [option, setOption] = useState<EChartsOption>({
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
            extraCssText: `
                max-height: 170px;
                overflow-y: auto;
                display: block;
                box-sizing: border-box;
            `,
            formatter: function (_params) {
                const params = _params as TooltipFormatterParam[]
                if (!params || !params.length) return '';

                const seen = new Set();
                const uniqueParams = params.filter(p => {
                    if (seen.has(p.seriesId)) return false;
                    seen.add(p.seriesId);
                    return true;
                });

                const xValue = uniqueParams[0]?.value?.[0] ?? uniqueParams[0]?.axisValue ?? '';

                const maxRows = 5;
                const maxCols = 3;
                const n = uniqueParams.length;
                let rows = Math.min(maxRows, n);
                let cols = Math.ceil(n / rows);
                if (cols > maxCols) {
                    cols = maxCols;
                    rows = Math.ceil(n / cols);
                }

                const columns: Array<Array<TooltipFormatterParam>> = Array.from({length: cols}, () => []);
                for (let i = 0; i < n; i++) {
                    const colIndex = Math.floor(i / rows);
                    columns[colIndex].push(uniqueParams[i]);
                }

                const columnHtml = columns.map(colItems => {
                    const rowsHtml = colItems.map((p) => {
                        const marker = p.marker || '';
                        const val = Array.isArray(p.value)
                            ? p.value[1]
                            : (p.value ?? '-');
                        return `
                          <div style="display:flex;align-items:center;gap:6px;line-height:1.4;">
                            <span>${marker}</span>
                            <span>${p.seriesName}: ${val}</span>
                          </div>
                        `;
                    }).join('');
                    return `<div style="display:flex;flex-direction:column;gap:2px;">${rowsHtml}</div>`;
                }).join('<div style="width:18px;"></div>');
                return `
                  <div style="display:flex;flex-direction:column;gap:8px;">
                    <div style="font-weight:bold;margin-bottom:4px;">X: ${xValue}</div>
                    <div style="display:flex;align-items:flex-start;">${columnHtml}</div>
                  </div>
                `;
            }
        },
        animation: false,
        animationDuration: 0,
        animationDurationUpdate: 0,
        animationEasing: 'linear',
        animationEasingUpdate: 'linear',
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
                    onclick: function () {
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
            type: "value",
            axisTick: {
                show: false,
            },
            axisLine: {
                show: false,
            },
            min: 'dataMin',
            max: 'dataMax'
        },
        yAxis: {},
        series: [],
    });

    useEffect(() => {
        setOption({
            series: getSeries()
        })
    }, [traceSeries]);

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
            // data: getOverviewXData()
        },
    });

    useEffect(() => {
        setOverviewOption({
            series: getOverviewSeries()
        })
    }, [overviewTraceSeries]);

    const overviewChartRef = useRef<ReactEcharts>(null);

    const onOverviewChartReady = (chart: ECharts) => {
        chart.on("brushEnd", (params) => {
            const brushParams = params as BrushEndParams;
            if (brushParams && brushParams.areas && brushParams.areas.length > 0
                && brushParams.areas[0].coordRange
                && brushParams.areas[0].coordRange.length == 2) {
                let [newStart, newEnd] = brushParams.areas[0].coordRange
                newStart = Math.max(Math.floor(newStart), maxRange[0])
                newEnd = Math.min(Math.ceil(newEnd), maxRange[1])
                setOverviewSelectedRange([newStart, newEnd])
            }
        });
        chart.dispatchAction({
            type: 'takeGlobalCursor',
            key: 'brush',
            brushOption: {
                brushType: 'lineX',
                brushMode: 'single',
                removeOnClick: false,
            }
        });
        chart.dispatchAction({
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
    };

    // useEffect(() => {
    //     if (overviewChartRef.current?.getEchartsInstance) {
    //         onOverviewChartReady(overviewChartRef.current.getEchartsInstance());
    //     }
    //     return () => {
    //     }
    // }, []);

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

    useEffect(() => {
        setSliderPercentRange(traceSeries.percentRange)
    }, [traceSeries]);

    const [_bTraceIndexFilters, _bSetTraceIndexFilters] = useModelState<Array<TraceIndexFilter>>("_f_trace_index_filters")
    const [_bInfoChannels,] = useModelState<Array<TraceIndex>>("_f_dataset_info_channels")
    const [, _bSetTraceOffset] = useModelState<TraceInfo>("_f_trace_offset")

    const [selectTraceChannelPaths, setSelectedTraceChannelPaths] = useState<string[]>([])
    const [selectedTraceIndex, setSelectedTraceIndex] = useState<Array<TraceInfo>>([])

    useEffect(() => {
        setSelectedTraceChannelPaths(_bTraceIndexFilters.map(f => `${f.groupPath}/${f.channelPath}`))
        const traceIndices = _bTraceIndexFilters
            .flatMap(f =>
                f.indices?.map(index => ({
                    index: `${f.index}/${index}`,
                    group: f.group,
                    channel: f.channel,
                    trace: index,
                    offset: 0
                })) ?? []
            );
        setSelectedTraceIndex(traceIndices);
    }, [_bTraceIndexFilters]);

    const handleOffsetChanged = (group: string, channel: string, trace_index: number, offset: number) => {
        setSelectedTraceIndex(prev =>
            prev.map(t => (t.group === group && t.channel === channel && t.trace === trace_index ? {...t, offset: offset} : t))
        );
    }

    const handleOffsetApply = (group: string, channel: string, trace_index: number) => {
        console.log(`Apply offset for ${group}/${channel}/${trace_index}: offset=${selectedTraceIndex.find(t => t.group === group && t.channel === channel && t.trace === trace_index)?.offset}`);
        const traceIndex = selectedTraceIndex.find(t => t.group === group && t.channel === channel && t.trace === trace_index);
        if (traceIndex) {
            _bSetTraceOffset(traceIndex);
        }
    };


    const tabsItems: (Omit<Tab, "destroyInactiveTabPane"> & CompatibilityProps)[] = [{
        key: "1",
        label: 'General',
        children: <GeneralControl
            groupChannels={_bInfoChannels}
            selectedChannelPaths={selectTraceChannelPaths}
            onSelectedChannelPathsChange={setSelectedTraceChannelPaths}
            traceIndexFilters={_bTraceIndexFilters}
            onTraceIndexFilterApply={_bSetTraceIndexFilters}
            range={maxRange}
            zoomStart={showRange[0]}
            zoomEnd={showRange[1]}
            zoomApply={(start: number, end: number) => {
                setSelectedRange([start, end]);
                // setOverviewRange(start, end);
            }}
        />
    }, {
        key: "2",
        label: "Shift",
        children: <ShiftControl
            onOffsetChanged={handleOffsetChanged}
            onOffsetApply={handleOffsetApply}
            traces={selectedTraceIndex}
        />
    }]

    return (
        <div ref={chartBoxRef}>
            <Tabs items={tabsItems} size={"small"}/>
            <ReactEcharts ref={chartRef} option={option} style={{height: 400}} replaceMerge={"series"}
                          onChartReady={onChartReady}/>
            <ReactEcharts ref={overviewChartRef} option={overviewOption} style={{height: 60}} replaceMerge={"series"}
                          onChartReady={onOverviewChartReady}/>
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