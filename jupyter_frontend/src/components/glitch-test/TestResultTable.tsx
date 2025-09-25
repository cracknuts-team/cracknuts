import React, {useState} from "react";
import {Space, Table, TableProps, Tag} from "antd";
import CheckableTag from "antd/es/tag/CheckableTag";

interface TestResultData {
    no: number,

    normal: number,
    glitch: number,
    wait: number,
    repeat: number,
    interval: number,

    status: number,
    time: number
}

interface _TestResultData extends Omit<TestResultData, 'status'> {
    status: React.ReactNode
}

const columns: TableProps<_TestResultData>['columns'] = [{
    title: 'NO',
    dataIndex: 'no',
    key: 'no',
}, {
    title: 'Normal',
    dataIndex: 'normal',
    key: 'normal',
}, {
    title: 'Glitch',
    dataIndex: 'glitch',
    key: 'glitch',
}, {
    title: 'Wait',
    dataIndex: 'wait',
    key: 'wait',
}, {
    title: 'Repeat',
    dataIndex: 'repeat',
    key: 'repeat',
}, {
    title: 'Interval(10 ns)',
    dataIndex: 'interval',
    key: 'interval',
}, {
    title: 'Status',
    dataIndex: 'status',
    key: 'status',
}, {
    title: 'Time',
    dataIndex: 'time',
    key: 'time',
}];


const data: TestResultData[] = [
    {no: 1, normal: 10, glitch: 20, wait: 30, repeat: 1, interval: 100, status: 2, time: 1234567890},
    {no: 2, normal: 11, glitch: 21, wait: 31, repeat: 2, interval: 101, status: 1, time: 1234567891},
    {no: 3, normal: 12, glitch: 22, wait: 32, repeat: 3, interval: 102, status: 1, time: 1234567892},
    {no: 4, normal: 13, glitch: 23, wait: 33, repeat: 4, interval: 103, status: 2, time: 1234567893},
    {no: 5, normal: 14, glitch: 24, wait: 34, repeat: 5, interval: 104, status: 1, time: 1234567894},
    {no: 6, normal: 15, glitch: 25, wait: 35, repeat: 6, interval: 105, status: 2, time: 1234567895},
    {no: 7, normal: 16, glitch: 26, wait: 36, repeat: 7, interval: 106, status: 1, time: 1234567896},
    {no: 8, normal: 17, glitch: 27, wait: 37, repeat: 8, interval: 107, status: 3, time: 1234567897},
    {no: 9, normal: 18, glitch: 28, wait: 38, repeat: 9, interval: 108, status: 1, time: 1234567898},
    {no: 10, normal: 19, glitch: 29, wait: 39, repeat: 10, interval: 109, status: 1, time: 1234567899},
    {no: 11, normal: 20, glitch: 30, wait: 40, repeat: 11, interval: 110, status: 4, time: 1234567800},
    {no: 12, normal: 21, glitch: 31, wait: 41, repeat: 12, interval: 111, status: 3, time: 1234567801},
];

const TestResultTable: React.FC = () => {

    const statusCheckOptions = [
        {key: 'glitched', label: 'Glitched', value: 1, color: 'green'},
        {key: 'not_glitched', label: 'Not Glitched', value: 2, color: 'orange'},
        {key: 'no_response', label: 'No Response', value: 3, color: 'gray'},
        {key: 'error', label: 'Error', value: 4, color: 'red'},
    ];

    const statusMap = Object.fromEntries(
        statusCheckOptions.map(opt => [opt.value, {label: opt.label, color: opt.color}])
    );

    const _data: _TestResultData[] = data.map(d => {
        const s = statusMap[d.status];
        return {...d,  status: <Tag color={s.color}>{s.label}</Tag>}
    });

    const [selected, setSelected] = useState<string[]>(['glitched', 'not_glitched', 'no_response', 'error']);

    return (
        <div>
            <Space.Compact style={{margin: "20px 0 10px 0"}}>
                {statusCheckOptions.map(opt => (
                    <CheckableTag
                        key={opt.key}
                        checked={selected.includes(opt.key)}
                        onChange={checked => {
                            setSelected(prev =>
                                checked ? [...prev, opt.key] : prev.filter(k => k !== opt.key)
                            );
                        }}
                        style={{
                            border: `2px solid ${opt.color}`,
                            // borderRadius: 8,
                            // padding: '4px 12px',
                            backgroundColor: selected.includes(opt.key) ? opt.color : '#fff',
                            color: selected.includes(opt.key) ? '#fff' : opt.color,
                            cursor: 'pointer',
                        }}
                    >
                        {opt.label}
                    </CheckableTag>
                ))}
            </Space.Compact>

            <Table<_TestResultData> columns={columns} dataSource={_data} size={"small"}
                                    pagination={{
                                        total: 100,
                                        defaultPageSize: 5,
                                        showTotal: (total, range) => {
                                            return `${range[0]}-${range[1]} / ${total}`
                                        },
                                    }}
            />
        </div>
    );
};

export default TestResultTable;