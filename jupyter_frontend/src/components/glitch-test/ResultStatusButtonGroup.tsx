import {Button, Space} from "antd";
import React, {useState} from "react";

const ResultStatusButtonGroup: React.FC = () => {
    const [statusChecked, setStatusChecked] = useState([false, false, false, false]);
    const [values] = useState([10, 20, 30, 40]); // 对应每个按钮的数值

    const colors = ['#f16053', '#fa8c16', '#d9d9d9', '#52c41a'];
    const labels = ['ERROR', 'NO_RETURN', 'NO_GLITCHED', 'GLITCHED'];

    const highlightColor = '#1091df'; // 底部高亮色

    return (
        <Space.Compact>
            {colors.map((color, i) => (
                <Button
                    key={i}
                    style={{
                        backgroundColor: color,
                        color: '#000',
                        position: 'relative',
                        display: 'flex',
                        flexDirection: 'column',
                        alignItems: 'center',
                        justifyContent: 'center',
                        height: 48,
                    }}
                    onClick={() => {
                        const newChecked = [...statusChecked];
                        newChecked[i] = !newChecked[i];
                        setStatusChecked(newChecked);
                    }}
                >
                    <span style={{fontSize: '0.8rem'}}>{labels[i]}</span>
                    <span style={{fontSize: '0.9rem', marginBottom: 3}}>{values[i]}</span>
                    {statusChecked[i] && (
                        <span
                            style={{
                                position: 'absolute',
                                bottom: 0,
                                left: 0,
                                width: '100%',
                                height: 4,
                                backgroundColor: highlightColor,
                            }}
                        />
                    )}
                </Button>
            ))}
        </Space.Compact>
    )
}

export default ResultStatusButtonGroup;
