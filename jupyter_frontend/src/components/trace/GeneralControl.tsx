import React from "React"
import {Button, Flex, Form, Input, InputNumber, Select, Table, TableProps} from "antd";
import {ChangeEvent, useEffect, useState} from "react";

interface TraceIndex {
    name: string;
    path: string;
}

interface TraceIndexFilter {
    index: string,
    name: string,
    group: string,
    channel: string,
    channelIndex: number,
    filter: string,
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
    groups: TraceIndex[];
    channels: TraceIndex[];

    selectedGroupPaths: string[];
    onSelectedGroupPathsChange: (paths: string[]) => void;

    selectedChannelPaths: string[];
    onSelectedChannelPathsChange: (paths: string[]) => void;

    traceIndexFilters: TraceIndexFilter[];
    onTraceIndexFilterApply: (filters: TraceIndexFilter[]) => void;

}

const GeneralControl: React.FC<GeneralProp> = ({
                                                   groups,
                                                   channels,
                                                   selectedGroupPaths,
                                                   onSelectedGroupPathsChange,
                                                   selectedChannelPaths,
                                                   onSelectedChannelPathsChange,
                                                   traceIndexFilters,
                                                   onTraceIndexFilterApply
                                               }: GeneralProp) => {

    const [filters, setFilters] = useState(traceIndexFilters);

    useEffect(() => {
        setFilters(traceIndexFilters)
    }, [traceIndexFilters]);

    const handleFilterChange = (index: string, filter: string) => {
        setFilters(prev =>
            prev.map(f => (f.index === index ? {...f, filter: filter} : f))
        );
    };

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

    return (
        <div>
            <Flex vertical gap={"middle"} style={{width: '100%'}}>
                <Flex gap={"small"} align={"start"}>
                    <div style={{width: 60}}>Show</div>
                    <Select
                        style={{minWidth: 80}}
                        size={"small"}
                        mode={"multiple"}
                        options={groups?groups.map(g => ({label: g.name, value: g.path})):[]}
                        value={selectedGroupPaths}
                        onChange={onSelectedGroupPathsChange}
                    />
                    <Select
                        style={{minWidth: 80}}
                        size={"small"}
                        mode={"multiple"}
                        options={groups?channels.map(c => ({label: c.name, value: c.path})):[]}
                        value={selectedChannelPaths}
                        onChange={onSelectedChannelPathsChange}
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
                        <InputNumber/>
                    </Form.Item>
                    <Form.Item label={"End"}>
                        <InputNumber/>
                    </Form.Item>
                    <Button>Apply</Button>
                </Form>
            </Flex>
        </div>
    );
}

export default GeneralControl;
export type {TraceIndex, TraceIndexFilter};