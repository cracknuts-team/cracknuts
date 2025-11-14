import React from "React"
import {Button, Col, Flex, Form, InputNumber, Row, Select, Table, TableProps} from "antd";

interface TraceIndex {
    name: string;
    path: string;
}

interface TraceIndexFilter {
    index: string,
    name: string,
    group: string,
    channel: string,
    filter: string,
}

const columns: TableProps<TraceIndexFilter>['columns'] = [{
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
}];

interface GeneralProp {
    groups: TraceIndex[];
    channels: TraceIndex[];

    selectedGroupPaths: string[];
    onSelectedGroupPathsChange: (paths: string[]) => void;

    selectedChannelPaths: string[];
    onSelectedChannelPathsChange: (paths: string[]) => void;

    traceIndexFilter: TraceIndexFilter[];
    onTraceIndexFilterChange: (index: string, filter: string) => void;

}

const GeneralControl: React.FC<GeneralProp> = ({
                                                   groups,
                                                   channels,
                                                   selectedGroupPaths,
                                                   onSelectedGroupPathsChange,
                                                   selectedChannelPaths,
                                                   onSelectedChannelPathsChange,
                                                   traceIndexFilter,
                                                   onTraceIndexFilterChange
                                               }: GeneralProp) => {
    return (
        <div>
            <Flex vertical gap={"middle"} style={{width: '100%'}}>
                <Flex gap={"small"} align={"start"}>
                    <div style={{width: 60}}>Show</div>
                    <Select
                        style={{minWidth: 80}}
                        size={"small"}
                        mode={"multiple"}
                        options={groups.map(g => ({label: g.name, value: g.path}))}
                        value={selectedGroupPaths}
                        onChange={onSelectedGroupPathsChange}
                    />
                    <Select
                        style={{minWidth: 80}}
                        size={"small"}
                        mode={"multiple"}
                        options={channels.map(c => ({label: c.name, value: c.path}))}
                        value={selectedChannelPaths}
                        onChange={onSelectedChannelPathsChange}
                    />
                </Flex>
                <Flex gap={"small"} align={"start"} style={{width: '100%'}}>
                    <div style={{width: 60}}></div>
                    <Table
                        size={"small"}
                        showHeader={false}
                        columns={columns}
                        dataSource={traceIndexFilter}
                        pagination={false}
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
export type {TraceIndexFilter};