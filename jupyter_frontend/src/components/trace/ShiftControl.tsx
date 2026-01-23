import React from "react";
import {Button, InputNumber, Table, TableProps} from "antd";
import {FormattedMessage} from "react-intl";

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
    title: <FormattedMessage id={"trace.toolbar.shift.group"}/>
}, {
    key: 'channel',
    dataIndex: 'channel',
    title: <FormattedMessage id={"trace.toolbar.shift.channel"}/>
}, {
    key: 'trace',
    dataIndex: 'trace',
    title: <FormattedMessage id={"trace.toolbar.shift.trace"}/>
}, {
    key: 'offset',
    dataIndex: 'offset',
    title: <FormattedMessage id={"trace.toolbar.shift.offset"}/>
}, {
    key: 'operation',
    dataIndex: 'operation',
    title: <FormattedMessage id={"trace.toolbar.shift.operation"}/>
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
            ><FormattedMessage id={"trace.toolbar.shift.operation.apply"}/></Button>
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