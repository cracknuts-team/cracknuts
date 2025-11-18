import React from "React";
import {InputNumber, Table, TableProps} from "antd";

interface TraceInfo {
    index: string,
    group: string,
    channel: string,
    trace: number,
    offset: number | React.ReactNode,
    operator: React.ReactNode
}

const columns: TableProps<TraceInfo>['columns'] = [{
    key: 'group',
    dataIndex: 'group',
    title: 'Group'
}, {
    key: 'channel',
    dataIndex: 'channel',
    title: 'Channel'
}, {
    key: 'trace',
    dataIndex: 'trace',
    title: 'Trace'
}, {
    key: 'offset',
    dataIndex: 'offset',
    title: 'Offset'
}, {
    key: 'operator',
    dataIndex: 'operator',
    title: 'Operator'
}];

interface ShiftControlProp {
    traces: TraceInfo[]
}

const ShiftControl: React.FC<ShiftControlProp> = ({traces}) => {
    const _traces: TraceInfo[] = traces.map(t => {
        return {
            ...t,
            offset: <div><InputNumber value={100} size={"small"}/></div>
        }
    })
    return (
        <Table
            size={"small"}
            columns={columns}
            dataSource={_traces}
            pagination={false}
        />
    );
};

export default ShiftControl;
export type {ShiftControl}