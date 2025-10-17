import React from "react";
import {Col, Row} from "antd";
import GlitchTestResultTable from "@/components/glitch-test/GlitchTestResultTable.tsx";


const TestResult: React.FC = () => {

    return (
        <Row>
            <Col span={24}>
                <GlitchTestResultTable/>
            </Col>
        </Row>
    );
};

export default TestResult;