import React, {useCallback} from "react"
import {Button, Flex, Form, Input, InputNumber, Select, Space, Table, TableProps} from "antd";
import {ChangeEvent, useEffect, useState} from "react";

interface TraceIndex {
    name: string;
    path: string;
    children?: TraceIndex[]
}

interface TraceIndexFilter {
    index: string,
    name: string,
    group: string,
    groupPath: string,
    channel: string,
    channelPath: string,
    filter: string,
    indices?: number[]
}

interface _TraceIndexFilter extends Omit<TraceIndexFilter, "filter"> {
    filter: React.ReactNode,
}

const columns: TableProps<_TraceIndexFilter>['columns'] = [{
    key: 'name',
    dataIndex: 'name',
    title: 'Name'
}, {
    key: 'filter',
    dataIndex: 'filter',
    title: 'Filter',
    onHeaderCell: () => ({
        style: {
            minWidth: 200
        }
    })
}, {
    key: 'operation',
    dataIndex: 'operation',
    title: 'Operation',
}];

interface GeneralProp {
    groupChannels: TraceIndex[];

    selectedChannelPaths: string[];
    onSelectedChannelPathsChange: (paths: string[]) => void;

    traceIndexFilters: TraceIndexFilter[];
    onTraceIndexFilterApply: (filters: TraceIndexFilter[]) => void;
    range: number[];
    zoomStart: number;
    zoomEnd: number;
    zoomApply: (start: number, end: number) => void;
}

const GeneralControl: React.FC<GeneralProp> = ({
                                                   groupChannels,
                                                   selectedChannelPaths,
                                                   onSelectedChannelPathsChange,
                                                   traceIndexFilters,
                                                   onTraceIndexFilterApply,
                                                   range,
                                                   zoomStart,
                                                   zoomEnd,
                                                   zoomApply
                                               }: GeneralProp) => {
    const [filtersCache, setFiltersCache] = useState<TraceIndexFilter[]>(traceIndexFilters); // cache the filter from python
    const [filters, setFilters] = useState<TraceIndexFilter[]>(traceIndexFilters);
    const [channelSelectOptions, setChannelSelectOptions] = useState<{
        label: React.ReactNode;
        options: object[]
    }[]>([]);

    useEffect(() => {
        setChannelSelectOptions(groupChannels.map(channel => ({
            label: <span>{channel.name}</span>,
            options: channel.children?.map(child => ({
                label: <span>{child.name}</span>,
                value: `${child.path}`,
            })) ?? []
        })))
    }, [groupChannels]);

    useEffect(() => {
        setFiltersCache(traceIndexFilters)
        setFilters(traceIndexFilters)
    }, [traceIndexFilters]);

    const handleFilterChange = (index: string, filter: string) => {
        setFilters(prev =>
            prev.map(f => (f.index === index ? {...f, filter: filter} : f))
        );
    };

    const handleChannelChange = useCallback((paths: string[]) => {
        onSelectedChannelPathsChange(paths);
        console.log(`filter cache ${JSON.stringify(filtersCache)}`)
        console.log(`group-channels: ${JSON.stringify(groupChannels)}`)
        const newFilters: TraceIndexFilter[] = [];
        for (const path of paths) {
            for (const group of groupChannels) {
                for (const channel of group.children || []) {
                    if (path === channel.path) {
                        const newFilter = {
                            index: `${channel.path}`,
                            group: group.name,
                            groupPath: group.path,
                            channel: channel.name.split("/")[1],
                            channelPath: channel.path.split("/")[1],
                            name: `${channel.name}`,
                            filter: '',
                        };
                        const existFilter = filtersCache.find(f => f.index === newFilter.index)
                        if (existFilter) {
                            newFilter.filter = existFilter.filter
                        }
                        newFilters.push(newFilter)
                    }
                }
            }
        }
        setFilters(newFilters);
    }, [filtersCache]);

    const _traceIndexFilters: _TraceIndexFilter[] = filters.map(f => ({
        ...f,
        filter: (
            <Input
                key={f.index}
                size="small"
                value={f.filter}
                onChange={(e: ChangeEvent<HTMLInputElement>) => handleFilterChange(f.index, e.target.value)}
            />
        ),
    }));

    const [zoomStartInput, setZoomStartInput] = useState<number>(zoomStart);
    const [zoomEndInput, setZoomEndInput] = useState<number>(zoomEnd);

    useEffect(() => {
        setZoomStartInput(zoomStart);
    }, [zoomStart]);
    useEffect(() => {
        setZoomEndInput(zoomEnd);
    }, [zoomEnd]);

    return (
        <div>
            <Flex vertical gap={"middle"} style={{width: '100%'}}>
                <Flex gap={"small"} align={"start"}>
                    <div style={{width: 60}}>Show</div>
                    <Select
                        style={{minWidth: 120, fontSize: 12}}
                        size={"small"}
                        mode={"multiple"}
                        options={channelSelectOptions}
                        value={selectedChannelPaths}
                        onChange={handleChannelChange}
                    />
                    <Button
                        onClick={() => {
                            onTraceIndexFilterApply(filters)
                        }}
                        size={"small"}
                    >
                        Apply
                    </Button>
                </Flex>
                <Flex gap={"small"} align={"start"} style={{width: '100%'}}>
                    <div style={{width: 60}}></div>
                    <Table
                        size={"small"}
                        showHeader={false}
                        columns={columns}
                        dataSource={_traceIndexFilters}
                        rowKey={"index"}
                        pagination={false}
                        locale={{emptyText: null}}
                    />
                </Flex>
            </Flex>
            <Flex style={{marginTop: 30}}>
                <div style={{width: 60}}>Zoom</div>
                <Form layout={"inline"} size={"small"}>
                    <Form.Item label={"Start"}>
                        <InputNumber
                            min={range[0]}
                            max={range[1]}
                            value={zoomStartInput}
                            onChange={(v) => setZoomStartInput(Number(v))}/>
                    </Form.Item>
                    <Form.Item label={"End"}>
                        <InputNumber
                            min={range[0]}
                            max={range[1]}
                            value={zoomEndInput}
                            onChange={(v) => setZoomEndInput(Number(v))}/>
                    </Form.Item>
                    <Space.Compact>
                        <Button onClick={() => {
                            console.log(`zoom out pre start-end: ${zoomStartInput}, ${zoomEndInput}`)
                            const center = (zoomStartInput + zoomEndInput) / 2;
                            const newStart = Math.floor(Math.max(range[0], center - (zoomEndInput - zoomStartInput) / 2 * 1.2));
                            const newEnd = Math.ceil(Math.min(range[1], center + (zoomEndInput - zoomStartInput) / 2 * 1.2));
                            setZoomStartInput(newStart);
                            setZoomEndInput(newEnd);
                            console.log(`zoom out new start-end: ${newStart}, ${newEnd}`)
                            zoomApply(newStart, newEnd)
                        }}>Zoom Out</Button>
                        <Button onClick={() => {
                            console.log(`zoom in pre start-end: ${zoomStartInput}, ${zoomEndInput}`)
                            if (zoomEndInput - zoomStartInput >= 100) { // minimum zoom range is 100
                                const center = (zoomStartInput + zoomEndInput) / 2;
                                const newStart = Math.floor(Math.max(range[0], center - (zoomEndInput - zoomStartInput) / 2 / 1.2));
                                const newEnd = Math.ceil(Math.min(range[1], center + (zoomEndInput - zoomStartInput) / 2 / 1.2));
                                setZoomStartInput(newStart);
                                setZoomEndInput(newEnd);
                                console.log(`zoom in new start-end: ${newStart}, ${newEnd}`)
                                zoomApply(newStart, newEnd)
                            }
                        }}>Zoom In</Button>
                        <Button onClick={() => {zoomApply(zoomStartInput, zoomEndInput);}}>Apply</Button>
                    </Space.Compact>
                </Form>
            </Flex>
        </div>
    );
}

export default GeneralControl;
export type {TraceIndex, TraceIndexFilter};