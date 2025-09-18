import React from "react";
import Connection, {ConnectionProps} from "@/components/Connection.tsx";
import G1Config, {G1ConfigProps} from "@/components/config/G1Config.tsx";
import {Col, Row} from "antd";
import Configuration, {ConfigurationProps} from "@/components/Configuration.tsx";


interface CrackerG1PanelProps {
    connection: ConnectionProps;
    configuration: ConfigurationProps;
    config: G1ConfigProps;
}

const CrackerG1: React.FC<CrackerG1PanelProps> = (props) => {
    return (
        <div>
            <Row justify="space-between">
                <Col flex={"auto"}>
                    <Connection
                        uri={props.connection.uri}
                        connect={props.connection.connect}
                        connected={props.connection.connected}
                        onUriChanged={props.connection.onUriChanged}
                        disconnect={props.connection.disconnect}
                        disabled={props.connection.disabled}
                    />
                </Col>
                <Col style={{marginLeft: "auto"}}>
                    <Configuration
                        readConfig={props.configuration.readConfig}
                        writeConfig={props.configuration.writeConfig}
                        saveConfig={props.configuration.saveConfig}
                        dumpConfig={props.configuration.dumpConfig}
                        loadConfig={props.configuration.loadConfig}
                        panelConfigDifferentFromCrackerConfig={props.configuration.panelConfigDifferentFromCrackerConfig}
                    />
                </Col>
            </Row>
            <Row>
                <Col>
                    <G1Config
                        common={props.config.common}
                        osc={props.config.osc}
                        glitch={props.config.glitch}
                        glitchTest={props.config.glitchTest}
                    />
                </Col>
            </Row>
        </div>
    );
};

export default CrackerG1;