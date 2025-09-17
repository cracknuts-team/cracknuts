import React from "react";
import {Button, Checkbox, Col, Form, InputNumber, Row, Select, Space} from "antd";
import {FormattedMessage} from "react-intl";


interface ConfigOSCProps {
  sample: {
    rate: number,
    setRate: (number: number) => void,
    phase: number,
    setPhase: (number: number) => void,
    length: number,
    setLength: (number: number) => void,
    delay: number,
    setDelay: (number: number) => void,
    channelA: {
      enable: boolean;
      setEnable: (enable: boolean) => void;
      gain: number;
      setGain: (value: number) => void;
    },
    channelB: {
      enable: boolean;
      setEnable: (enable: boolean) => void;
      gain: number;
      setGain: (value: number) => void;
    },
  },
  trigger: {
    source: number,
    setSource: (source: number) => void,
    mode: number,
    setMode: (mode: number) => void,
    edge: number,
    setEdge: (edge: number) => void,
    edgeLevel: number,
    setEdgeLevel: (level: number) => void,
  }
}

const ConfigOSC: React.FC = () => {
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
                    value={oscSampleClock}
                    onChange={setOscSampleClock}
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
                  value={oscSamplePhase}
                  onChange={(v) => {
                    setOscSamplePhase(Number(v));
                  }}
                  changeOnWheel
                />
              </Form.Item>
              <Form.Item>
                <Space.Compact>
                  <Form.Item>
                    <Checkbox
                      checked={channel0Enable}
                      onChange={(v) => {
                        setChannel0Enable(v.target.checked);
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
                      disabled={!channel0Enable}
                      value={socChannel0Gain}
                      onChange={(v: number | string | null) => {
                        if (v != null) {
                          setOscChannel0Gain(Number(v));
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
                      checked={channel1Enable}
                      onChange={(v) => {
                        setChannel1Enable(v.target.checked);
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
                      disabled={!channel1Enable}
                      value={socChannel1Gain}
                      onChange={(v: number | string | null) => {
                        if (v != null) {
                          setOscChannel1Gain(Number(v));
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
                  value={oscSampleLength}
                  defaultValue={oscSampleLength}
                  onChange={(v: number | string | null) => {
                    if (v != null) {
                      setOscSampleLength(Number(v));
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
                  defaultValue={oscSampleDelay}
                  value={oscSampleDelay}
                  onChange={(v: number | string | null) => {
                    console.error(v)
                    if (v != null) {
                      setOscSampleDelay(Number(v));
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
                    {label: intl.formatMessage({id: "cracker.config.scope.triggerMode.edge"}), value: 0},
                    {
                      label: intl.formatMessage({id: "cracker.config.scope.triggerMode.waveform"}),
                      value: 1
                    },
                  ]}
                  style={{width: 100}}
                  value={oscTriggerMode}
                  onChange={setOscTriggerMode}
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
                  value={oscTriggerSource}
                  onChange={setOscTriggerSource}
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
                    {label: intl.formatMessage({id: "cracker.config.scope.triggerEdge.both"}), value: 2},
                  ]}
                  style={{width: 100}}
                  value={oscTriggerEdge}
                  onChange={setOscTriggerEdge}
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
                  value={oscTriggerEdgeLevel}
                  onChange={(value) => {
                    if (value != null) {
                      setOscTriggerEdgeLevel(value);
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
export type {ConfigOSCProps};