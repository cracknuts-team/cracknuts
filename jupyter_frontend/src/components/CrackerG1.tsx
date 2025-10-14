import React, {useState} from "react";
import Connection, {ConnectionProps} from "@/components/Connection.tsx";
import G1Config from "@/components/config/G1Config.tsx";
import {Col, Row} from "antd";
import Configuration from "@/components/Configuration.tsx";
import Scope from "@/components/Scope.tsx";
import Acquisition from "@/components/Acquisition.tsx";


interface CrackerG1PanelProps {
    connection: ConnectionProps;
    theme: "light" | "dark";
}

const CrackerG1: React.FC<CrackerG1PanelProps> = (props) => {

    const backgroundColor = props.theme === "light" ? "#ffffff" : "#000000";

    const [, setShowScope] = useState<boolean>(true);

    return (
        <div id={"cracknuts_widget"} style={{
                    padding: 20,
                    border: "1px solid #616161",
                    backgroundColor: backgroundColor,
                    marginTop: 8,
                    marginBottom: 8
                }}>
            <Row justify="space-between">
                <Col flex={"auto"} style={{paddingBottom: 10}}>
                    <Connection {...props.connection}/>
                </Col>
                <Col style={{marginLeft: "auto"}}>
                    <Configuration/>
                </Col>
            </Row>
            <Row>
                <Col>
                    <Acquisition/>
                </Col>
            </Row>
            <Row>
                <Col span={24}>
                    <G1Config isGlitchTestShow={(show) => setShowScope(!show)}/>
                </Col>
            </Row>
            <Row>
                <Col span={24}>
                    <Scope disable={false}/>
                    {/*{showScope && <Scope disable={false}/>}*/}
                </Col>
            </Row>
        </div>
    );
};

export default CrackerG1;

export type {CrackerG1PanelProps};