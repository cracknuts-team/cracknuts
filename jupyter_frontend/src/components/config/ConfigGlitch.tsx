import {Button, Col, Form, InputNumber, Row} from "antd";
import React from "react";
import {useIntl} from "react-intl";
import {useModel, useModelState} from "@anywidget/react";


const ConfigGlitch: React.FC = () => {

    const intl = useIntl();
    const model = useModel();

    const [glitchVCCNormalVoltage, setGlitchVCCNormalVoltage] = useModelState<number>("glitch_vcc_normal");
    const [glitchVCCWait, setGlitchVCCWait] = useModelState<number>("glitch_vcc_config_wait");
    const [glitchVCCGlitchVoltage, setGlitchVCCGlitchVoltage] = useModelState<number>("glitch_vcc_config_level");
    const [glitchVCCCount, setGlitchVCCCount] = useModelState<number>("glitch_vcc_config_count");
    const [glitchVCCRepeat, setGlitchVCCRepeat] = useModelState<number>("glitch_vcc_config_repeat");
    const [glitchVCCDelay, setGlitchVCCDelay] = useModelState<number>("glitch_vcc_config_delay");

    const [glitchGNDNormalVoltage, setGlitchGNDNormalVoltage] = useModelState<number>("glitch_gnd_normal");
    const [glitchGNDWait, setGlitchGNDWait] = useModelState<number>("glitch_gnd_config_wait");
    const [glitchGNDGlitchVoltage, setGlitchGNDGlitchVoltage] = useModelState<number>("glitch_gnd_config_level");
    const [glitchGNDCount, setGlitchGNDCount] = useModelState<number>("glitch_gnd_config_count");
    const [glitchGNDRepeat, setGlitchGNDRepeat] = useModelState<number>("glitch_gnd_config_repeat");
    const [glitchGNDDelay, setGlitchGNDDelay] = useModelState<number>("glitch_gnd_config_delay");

    const vcc = {
        normalVoltage: glitchVCCNormalVoltage,
        setNormalVoltage: setGlitchVCCNormalVoltage,

        wait: glitchVCCWait,
        setWait: setGlitchVCCWait,

        glitchVoltage: glitchVCCGlitchVoltage,
        setGlitchVoltage: setGlitchVCCGlitchVoltage,

        count: glitchVCCCount,
        setCount: setGlitchVCCCount,

        repeat: glitchVCCRepeat,
        setRepeat: setGlitchVCCRepeat,

        delay: glitchVCCDelay,
        setDelay: setGlitchVCCDelay,
    }
    const gnd = {
        normalVoltage: glitchGNDNormalVoltage,
        setNormalVoltage: setGlitchGNDNormalVoltage,

        wait: glitchGNDWait,
        setWait: setGlitchGNDWait,

        glitchVoltage: glitchGNDGlitchVoltage,
        setGlitchVoltage: setGlitchGNDGlitchVoltage,

        count: glitchGNDCount,
        setCount: setGlitchGNDCount,

        repeat: glitchGNDRepeat,
        setRepeat: setGlitchGNDRepeat,

        delay: glitchGNDDelay,
        setDelay: setGlitchGNDDelay,
    }

    const [glitchVCCNormalVoltageMin, glitchVCCNormalVoltageMax] = [1.2, 4.0];
    const [glitchVCCWaitMin, glitchVCCWaitMax] = [0, 0xFFFF_FFFF];
    const [glitchVCCGlitchVoltageMin, glitchVCCGlitchVoltageMax] = [0.0, 4.0];
    const [glitchVCCCountMin, glitchVCCCountMax] = [1, 255];
    const [glitchVCCRepeatMin, glitchVCCRepeatMax] = [1, 255];

    const [glitchGNDNormalVoltageMin, glitchGNDNormalVoltageMax] = [0.0, 1.0];
    const [glitchGNDWaitMin, glitchGNDWaitMax] = [0, 0xFFFF_FFFF];
    const [glitchGNDGlitchVoltageMin, glitchGNDGlitchVoltageMax] = [0.0, 4.0];
    const [glitchGNDCountMin, glitchGNDCountMax] = [1, 255];
    const [glitchGNDRepeatMin, glitchGNDRepeatMax] = [1, 255];

    // model.send({source: "acqStatusButton", event: "onChange", args: {status: "stop"}});

    const vccForce = () => {
        model.send({source: "glitchVCCForceButton", event: "onClick", args: {}});
    };

    return (
        <Row>
            <Col span={24}>
                <Row>
                    <Col span={24}>
                        <Form layout={"inline"}>
                            <Form.Item label={"VCC"} style={{width: 35}}/>
                            <Form.Item label={intl.formatMessage({id: "cracker.config.glitch.vcc.normalVoltage"})}>
                                <InputNumber style={{width: 90}}
                                             addonAfter="V"
                                             step="0.1"
                                             stringMode
                                             size={"small"}
                                             min={glitchVCCNormalVoltageMin}
                                             max={glitchVCCNormalVoltageMax}
                                             value={vcc.normalVoltage}
                                             parser={(v) => {
                                                 return Number(v);
                                             }}
                                             onChange={(v) => {
                                                 vcc.setNormalVoltage(Number(v));
                                             }}
                                             changeOnWheel
                                />
                            </Form.Item>
                            <Form.Item label={intl.formatMessage({id: "cracker.config.glitch.vcc.wait"})}>
                                <InputNumber style={{width: 90}}
                                             addonAfter="10 ns"
                                             step="1"
                                             stringMode
                                             size={"small"}
                                             min={glitchVCCWaitMin}
                                             max={glitchVCCWaitMax}
                                             value={vcc.wait}
                                             parser={(v) => {
                                                 return Number(v);
                                             }}
                                             onChange={(v) => {
                                                 vcc.setWait(Number(v));
                                             }}
                                             changeOnWheel
                                />
                            </Form.Item>
                            <Form.Item label={intl.formatMessage({id: "cracker.config.glitch.vcc.glitchVoltage"})}>
                                <InputNumber style={{width: 90}}
                                             addonAfter="V"
                                             step="0.1"
                                             stringMode
                                             size={"small"}
                                             min={glitchVCCGlitchVoltageMin}
                                             max={glitchVCCGlitchVoltageMax}
                                             value={vcc.glitchVoltage}
                                             parser={(v) => {
                                                 return Number(v);
                                             }}
                                             onChange={(v) => {
                                                 vcc.setGlitchVoltage(Number(v));
                                             }}
                                             changeOnWheel
                                />
                            </Form.Item>
                            <Form.Item label={intl.formatMessage({id: "cracker.config.glitch.vcc.count"})}>
                                <InputNumber style={{width: 90}}
                                             step="1"
                                             stringMode
                                             size={"small"}
                                             min={glitchVCCCountMin}
                                             max={glitchVCCCountMax}
                                             value={vcc.count}
                                             parser={(v) => {
                                                 return Number(v);
                                             }}
                                             onChange={(v) => {
                                                 vcc.setCount(Number(v));
                                             }}
                                             changeOnWheel
                                />
                            </Form.Item>
                            <Form.Item label={intl.formatMessage({id: "cracker.config.glitch.vcc.repeat"})}>
                                <InputNumber style={{width: 90}}
                                             step="1"
                                             stringMode
                                             size={"small"}
                                             min={glitchVCCRepeatMin}
                                             max={glitchVCCRepeatMax}
                                             value={vcc.repeat}
                                             parser={(v) => {
                                                 return Number(v);
                                             }}
                                             onChange={(v) => {
                                                 vcc.setRepeat(Number(v));
                                             }}
                                             changeOnWheel
                                />
                            </Form.Item>
                            <Form.Item label={intl.formatMessage({id: "cracker.config.glitch.vcc.delay"})}>
                                <InputNumber style={{width: 90}}
                                             step="1"
                                             addonAfter="10 ns"
                                             stringMode
                                             size={"small"}
                                             value={vcc.delay}
                                             parser={(v) => {
                                                 return Number(v);
                                             }}
                                             onChange={(v) => {
                                                 vcc.setDelay(Number(v));
                                             }}
                                             changeOnWheel
                                />
                            </Form.Item>
                            <Form.Item>
                                <Button size={"small"} onClick={vccForce}>Force</Button>
                            </Form.Item>
                        </Form>
                    </Col>
                </Row>
                <Row>
                    <Col span={24}>
                        <Form layout={"inline"}>
                            <Form.Item label={"GND"} style={{width: 35}}/>
                            <Form.Item label={intl.formatMessage({id: "cracker.config.glitch.gnd.normalVoltage"})}>
                                <InputNumber style={{width: 90}}
                                             addonAfter="V"
                                             step="0.1"
                                             stringMode
                                             size={"small"}
                                             min={glitchGNDNormalVoltageMin}
                                             max={glitchGNDNormalVoltageMax}
                                             value={gnd.normalVoltage}
                                             parser={(v) => {
                                                 return Number(v);
                                             }}
                                             onChange={(v) => {
                                                 gnd.setNormalVoltage(Number(v));
                                             }}
                                             changeOnWheel
                                />
                            </Form.Item>
                            <Form.Item label={intl.formatMessage({id: "cracker.config.glitch.gnd.wait"})}>
                                <InputNumber style={{width: 90}}
                                             addonAfter="10 ns"
                                             step="1"
                                             stringMode
                                             size={"small"}
                                             min={glitchGNDWaitMin}
                                             max={glitchGNDWaitMax}
                                             value={gnd.wait}
                                             parser={(v) => {
                                                 return Number(v);
                                             }}
                                             onChange={(v) => {
                                                 gnd.setWait(Number(v));
                                             }}
                                             changeOnWheel
                                />
                            </Form.Item>
                            <Form.Item label={intl.formatMessage({id: "cracker.config.glitch.gnd.glitchVoltage"})}>
                                <InputNumber style={{width: 90}}
                                             addonAfter="V"
                                             step="0.1"
                                             stringMode
                                             size={"small"}
                                             min={glitchGNDGlitchVoltageMin}
                                             max={glitchGNDGlitchVoltageMax}
                                             value={gnd.glitchVoltage}
                                             parser={(v) => {
                                                 return Number(v);
                                             }}
                                             onChange={(v) => {
                                                 gnd.setGlitchVoltage(Number(v));
                                             }}
                                             changeOnWheel
                                />
                            </Form.Item>
                            <Form.Item label={intl.formatMessage({id: "cracker.config.glitch.gnd.count"})}>
                                <InputNumber style={{width: 90}}
                                             step="1"
                                             stringMode
                                             size={"small"}
                                             min={glitchGNDCountMin}
                                             max={glitchGNDCountMax}
                                             value={gnd.count}
                                             parser={(v) => {
                                                 return Number(v);
                                             }}
                                             onChange={(v) => {
                                                 gnd.setCount(Number(v));
                                             }}
                                             changeOnWheel
                                />
                            </Form.Item>
                            <Form.Item label={intl.formatMessage({id: "cracker.config.glitch.gnd.repeat"})}>
                                <InputNumber style={{width: 90}}
                                             step="1"
                                             stringMode
                                             size={"small"}
                                             min={glitchGNDRepeatMin}
                                             max={glitchGNDRepeatMax}
                                             value={gnd.repeat}
                                             parser={(v) => {
                                                 return Number(v);
                                             }}
                                             onChange={(v) => {
                                                 gnd.setRepeat(Number(v));
                                             }}
                                             changeOnWheel
                                />
                            </Form.Item>
                            <Form.Item label={intl.formatMessage({id: "cracker.config.glitch.gnd.delay"})}>
                                <InputNumber style={{width: 90}}
                                             step="1"
                                             addonAfter="10 ns"
                                             stringMode
                                             size={"small"}
                                             value={gnd.delay}
                                             parser={(v) => {
                                                 return Number(v);
                                             }}
                                             onChange={(v) => {
                                                 gnd.setDelay(Number(v));
                                             }}
                                             changeOnWheel
                                />
                            </Form.Item>
                        </Form>
                    </Col>
                </Row>
            </Col>
        </Row>
    );
};

export default ConfigGlitch;