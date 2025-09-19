import React from "react";
import {Col, Row} from "antd";
import ResultStatusButtonGroup from "@/components/glitch-test/ResultStatusButtonGroup.tsx";


const TestResult: React.FC = () => {

    return (
        <Row>
            <Col span={24}>
                <ResultStatusButtonGroup/>
            </Col>
        </Row>
    );
};

export default TestResult;