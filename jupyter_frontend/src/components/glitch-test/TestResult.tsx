import React from "react";
import {Col, Row} from "antd";
import TestResultTable from "@/components/glitch-test/TestResultTable.tsx";


const TestResult: React.FC = () => {

    return (
        <Row>
            <Col span={24}>
                <TestResultTable/>
            </Col>
        </Row>
    );
};

export default TestResult;