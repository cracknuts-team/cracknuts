import React from "react";
import {Button, InputNumber, Table, TableProps} from "antd";

interface TraceInfo {
    index: string,
    group: string,
    channel: string,
    trace: number,
    offset: number
}

interface _TraceInfo extends Omit<TraceInfo, "offset"> {
    offset: React.ReactNode
    operation: React.ReactNode
}

const columns: TableProps<_TraceInfo>['columns'] = [{
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
    key: 'operation',
    dataIndex: 'operation',
    title: 'Operation'
}];

interface ShiftControlProp {
    traces: TraceInfo[],
    onOffsetChanged: (group: string, channel: string, trace_index: number, offset: number) => void,
    onOffsetApply: (group: string, channel: string, trace_index: number) => void
}

const ShiftControl: React.FC<ShiftControlProp> = ({traces, onOffsetChanged, onOffsetApply}) => {
    const _traces: _TraceInfo[] = traces.map(t => {
        return {
            ...t,
            offset: <InputNumber
                key={`offset-${t.index}`}
                value={t.offset}
                size={"small"}
                onChange={v => {onOffsetChanged(t.group, t.channel, t.trace, Number(v))}}
            />,
            operation: <Button
                onClick={() => {onOffsetApply(t.group, t.channel, t.trace)}}
                size={"small"}
                key={`apply-${t.index}`}
            >Apply</Button>
        }
    })
    return (
        <Table
            style={{width: 800}}
            size={"small"}
            columns={columns}
            dataSource={_traces}
            pagination={{pageSize:5, size:"small"}}
        />
    );
};

export default ShiftControl;
export type {ShiftControlProp, TraceInfo}