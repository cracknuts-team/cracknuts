import React from "react";
import {Button, Checkbox, Col, Form, InputNumber, Row, Select, Space} from "antd";
import {FormattedMessage, useIntl} from "react-intl";
import {useModelState} from "@anywidget/react";


const ConfigOSC: React.FC = () => {

    const intl = useIntl();

    // Sample
    const [oscSampleClock, setOscSampleClock] = useModelState<number>("osc_sample_clock");
    const [oscSamplePhase, setOscSamplePhase] = useModelState<number>("osc_sample_phase");
    const [oscSampleLength, setOscSampleLength] = useModelState<number>("osc_sample_length");
    const [oscSampleDelay, setOscSampleDelay] = useModelState<number>("osc_sample_delay");

    // Channels
    const [channelAEnable, setChannelAEnable] = useModelState<boolean>("osc_channel_0_enable");
    const [channelBEnable, setChannelBEnable] = useModelState<boolean>("osc_channel_1_enable");
    const [channelAGain, setChannelAGain] = useModelState<number>("osc_channel_0_gain");
    const [channelBGain, setChannelBGain] = useModelState<number>("osc_channel_1_gain");

    // Trigger
    const [oscTriggerSource, setOscTriggerSource] = useModelState<number>("osc_trigger_source");
    const [oscTriggerMode, setOscTriggerMode] = useModelState<number>("osc_trigger_mode");
    const [oscTriggerEdge, setOscTriggerEdge] = useModelState<number>("osc_trigger_edge");
    const [oscTriggerEdgeLevel, setOscTriggerEdgeLevel] = useModelState<number>("osc_trigger_edge_level");

    const sample = {
        rate: oscSampleClock,
        setRate: setOscSampleClock,
        phase: oscSamplePhase,
        setPhase: setOscSamplePhase,
        length: oscSampleLength,
        setLength: setOscSampleLength,
        delay: oscSampleDelay,
        setDelay: setOscSampleDelay,
        channelA: {
            enable: channelAEnable,
            setEnable: setChannelAEnable,
            gain: channelAGain,
            setGain: setChannelAGain,
        },
        channelB: {
            enable: channelBEnable,
            setEnable: setChannelBEnable,
            gain: channelBGain,
            setGain: setChannelBGain,
        },
    }
    const trigger = {
        source: oscTriggerSource,
        setSource: setOscTriggerSource,
        mode: oscTriggerMode,
        setMode: setOscTriggerMode,
        edge: oscTriggerEdge,
        setEdge: setOscTriggerEdge,
        edgeLevel: oscTriggerEdgeLevel,
        setEdgeLevel: setOscTriggerEdgeLevel,
    }

    return (
        <Row>
            <Col span={24}>
                <Row>
                    <Col span={24}>
                        <Form layout="inline">
                            <Form.Item label={intl.formatMessage({id: "cracker.config.scope.sampleRate"})}>
                                <Space.Compact>
                                    <Select
                                        size={"small"}
                                        options={[
                                            {value: 65000, label: "65 M"},
                                            {value: 48000, label: "48 M"},
                                            {value: 24000, label: "24 M"},
                                            {value: 12000, label: "12 M"},
                                            {value: 8000, label: "8  M"},
                                        ]}
                                        value={sample.rate}
                                        onChange={sample.setRate}
                                        style={{width: 80}}
                                    ></Select>
                                    <Button style={{pointerEvents: "none", opacity: 1, cursor: "default"}}
                                            size={"small"}>Hz</Button>
                                </Space.Compact>
                            </Form.Item>
                            <Form.Item label={intl.formatMessage({id: "cracker.config.scope.samplePhase"})}>
                                <InputNumber
                                    addonAfter="°"
                                    style={{width: 100}}
                                    step="1"
                                    stringMode
                                    size={"small"}
                                    min={0}
                                    max={360}
                                    value={sample.phase}
                                    onChange={(v) => {
                                        sample.setPhase(Number(v));
                                    }}
                                    changeOnWheel
                                />
                            </Form.Item>
                            <Form.Item>
                                <Space.Compact>
                                    <Form.Item>
                                        <Checkbox
                                            checked={sample.channelA.enable}
                                            onChange={(v) => {
                                                sample.channelA.setEnable(v.target.checked);
                                            }}
                                        >
                                            <FormattedMessage id={"cracker.config.scope.channel.a.gain"}/>
                                        </Checkbox>
                                        <InputNumber
                                            addonAfter="dB"
                                            style={{width: 100}}
                                            step="1"
                                            size={"small"}
                                            min={1}
                                            max={50}
                                            changeOnWheel
                                            disabled={!sample.channelA.enable}
                                            value={sample.channelA.gain}
                                            onChange={(v: number | string | null) => {
                                                if (v != null) {
                                                    sample.channelA.setGain(Number(v));
                                                }
                                            }}
                                        />
                                    </Form.Item>
                                </Space.Compact>
                            </Form.Item>
                            <Form.Item>
                                <Space.Compact>
                                    <Form.Item>
                                        <Checkbox
                                            checked={sample.channelB.enable}
                                            onChange={(v) => {
                                                sample.channelB.setEnable(v.target.checked);
                                            }}
                                        >
                                            <FormattedMessage id={"cracker.config.scope.channel.b.gain"}/>
                                        </Checkbox>
                                        <InputNumber
                                            addonAfter="dB"
                                            style={{width: 100}}
                                            step="1"
                                            size={"small"}
                                            min={1}
                                            max={50}
                                            changeOnWheel
                                            disabled={!sample.channelB.enable}
                                            value={sample.channelB.gain}
                                            onChange={(v: number | string | null) => {
                                                if (v != null) {
                                                    sample.channelB.setGain(Number(v));
                                                }
                                            }}
                                        />
                                    </Form.Item>
                                </Space.Compact>
                            </Form.Item>
                            <Form.Item label={intl.formatMessage({id: "cracker.config.scope.sampleLength"})}>
                                <InputNumber
                                    suffix=""
                                    step="1"
                                    size={"small"}
                                    min={10}
                                    value={sample.length}
                                    onChange={(v: number | string | null) => {
                                        if (v != null) {
                                            sample.setLength(Number(v));
                                        }
                                    }}
                                    changeOnWheel
                                />
                            </Form.Item>
                            <Form.Item label={intl.formatMessage({id: "cracker.config.scope.sampleDelay"})}>
                                <InputNumber
                                    step="1"
                                    size={"small"}
                                    min={0}
                                    value={sample.delay}
                                    onChange={(v: number | string | null) => {
                                        console.error(v)
                                        if (v != null) {
                                            sample.setDelay(Number(v));
                                        }
                                    }}
                                    changeOnWheel
                                />
                            </Form.Item>
                        </Form>
                    </Col>
                </Row>
                <Row>
                    <Col>
                        <Form layout={"inline"}>
                            <Form.Item label={intl.formatMessage({id: "cracker.config.scope.triggerMode"})}>
                                <Select
                                    size={"small"}
                                    defaultValue={0}
                                    options={[
                                        {
                                            label: intl.formatMessage({id: "cracker.config.scope.triggerMode.edge"}),
                                            value: 0
                                        },
                                        {
                                            label: intl.formatMessage({id: "cracker.config.scope.triggerMode.waveform"}),
                                            value: 1
                                        },
                                    ]}
                                    style={{width: 100}}
                                    value={trigger.mode}
                                    onChange={trigger.setMode}
                                />
                            </Form.Item>
                            <Form.Item label={intl.formatMessage({id: "cracker.config.scope.triggerSource"})}>
                                <Select
                                    size={"small"}
                                    defaultValue={0}
                                    options={[
                                        {label: "N (Nut)", value: 0},
                                        {label: "A (Ch A)", value: 1},
                                        {label: "B (Ch B)", value: 2},
                                        {label: "P (Protocol)", value: 3},
                                    ]}
                                    style={{width: 110}}
                                    value={trigger.source}
                                    onChange={trigger.setSource}
                                />
                            </Form.Item>
                            <Form.Item label={intl.formatMessage({id: "cracker.config.scope.triggerEdge"})}>
                                <Select
                                    size={"small"}
                                    defaultValue={0}
                                    options={[
                                        {
                                            label: intl.formatMessage({id: "cracker.config.scope.triggerEdge.rising"}),
                                            value: 0
                                        },
                                        {
                                            label: intl.formatMessage({id: "cracker.config.scope.triggerEdge.falling"}),
                                            value: 1
                                        },
                                        {
                                            label: intl.formatMessage({id: "cracker.config.scope.triggerEdge.both"}),
                                            value: 2
                                        },
                                    ]}
                                    style={{width: 100}}
                                    value={trigger.edge}
                                    onChange={trigger.setEdge}
                                />
                            </Form.Item>
                            <Form.Item label={intl.formatMessage({id: "cracker.config.scope.triggerEdgeLevel"})}>
                                <InputNumber
                                    suffix=""
                                    step="1"
                                    size={"small"}
                                    min={-2047}
                                    max={2048}
                                    changeOnWheel
                                    value={trigger.edgeLevel}
                                    onChange={(value) => {
                                        if (value != null) {
                                            trigger.setEdgeLevel(value);
                                        }
                                    }}
                                />
                            </Form.Item>
                        </Form>
                    </Col>
                </Row>
            </Col>
        </Row>
    );
};

export default ConfigOSC;