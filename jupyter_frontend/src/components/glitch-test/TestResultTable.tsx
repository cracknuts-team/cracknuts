import React from "react";
import {Table, TableProps, Tag} from "antd";
import {useModelState} from "@anywidget/react";

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
}];


const TestResultTable: React.FC = () => {

    const [data] = useModelState<TestResultData[]>("glitch_test_result");

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

    // const [selected, setSelected] = useState<string[]>(['glitched', 'not_glitched', 'no_response', 'error']);

    return (
        <div>
            {/*<Space.Compact style={{margin: "20px 0 10px 0"}}>*/}
            {/*    {statusCheckOptions.map(opt => (*/}
            {/*        <CheckableTag*/}
            {/*            key={opt.key}*/}
            {/*            checked={selected.includes(opt.key)}*/}
            {/*            onChange={checked => {*/}
            {/*                setSelected(prev =>*/}
            {/*                    checked ? [...prev, opt.key] : prev.filter(k => k !== opt.key)*/}
            {/*                );*/}
            {/*            }}*/}
            {/*            style={{*/}
            {/*                border: `2px solid ${opt.color}`,*/}
            {/*                // borderRadius: 8,*/}
            {/*                // padding: '4px 12px',*/}
            {/*                backgroundColor: selected.includes(opt.key) ? opt.color : '#fff',*/}
            {/*                color: selected.includes(opt.key) ? '#fff' : opt.color,*/}
            {/*                cursor: 'pointer',*/}
            {/*            }}*/}
            {/*        >*/}
            {/*            {opt.label}*/}
            {/*        </CheckableTag>*/}
            {/*    ))}*/}
            {/*</Space.Compact>*/}

            <Table<_TestResultData> columns={columns} dataSource={_data} size={"small"}
                                    pagination={false}
                                    // pagination={{
                                    //     total: 100,
                                    //     defaultPageSize: 5,
                                    //     showTotal: (total, range) => {
                                    //         return `${range[0]}-${range[1]} / ${total}`
                                    //     },
                                    // }}
            />
        </div>
    );
};

export default TestResultTable;