import React from "react";
import GlitchTestResultTable from "@/components/glitch-test/GlitchTestResultTable.tsx";
import {Space} from "antd";
import CheckableTag from "antd/es/tag/CheckableTag";
import {useModelState} from "@anywidget/react";


const GlitchTestResultFilter: React.FC = () => {
    const [selected, setSelected] = useModelState<number[]>("selected_status");

    const statusCheckOptions = [
        {key: 'glitched', label: 'Glitched', value: 1, color: 'green'},
        {key: 'not_glitched', label: 'Not Glitched', value: 2, color: 'orange'},
        {key: 'no_response', label: 'No Response', value: 3, color: 'gray'},
        {key: 'error', label: 'Error', value: 4, color: 'red'},
    ];

    return (
        <Space.Compact style={{margin: "20px 0 10px 0"}}>
            {statusCheckOptions.map(opt => (
                <CheckableTag
                    key={opt.key}
                    checked={selected.includes(opt.value)}
                    onChange={checked => {
                        setSelected(
                            // prev => checked ? [...prev, opt.key] : prev.filter(k => k !== opt.key)
                            checked ? [...selected, opt.value] : selected.filter(k => k !== opt.value)
                        );
                    }}
                    style={{
                        border: `2px solid ${opt.color}`,
                        // borderRadius: 8,
                        // padding: '4px 12px',
                        backgroundColor: selected.includes(opt.value) ? opt.color : '#fff',
                        color: selected.includes(opt.value) ? '#fff' : opt.color,
                        cursor: 'pointer',
                    }}
                >
                    {opt.label}
                </CheckableTag>
            ))}
        </Space.Compact>
    );
}

const GlitchTestResultAnalysis: React.FC = () => {
    return (
        <div>
            <GlitchTestResultFilter/>
            <GlitchTestResultTable showPagination={true}/>
        </div>
    );
};

export default GlitchTestResultAnalysis;