import { Button, Col, Divider, Form, Input, InputNumber, Popover, Row, Select } from "antd";
import React, { useState } from "react";
import { useIntl } from "react-intl";
import { useModel, useModelState } from "@anywidget/react";
import { QuestionCircleOutlined } from "@ant-design/icons";

const ConfigGlitch: React.FC = () => {

    const intl = useIntl();
    const model = useModel();

    const [glitchVCCNormalVoltage, setGlitchVCCNormalVoltage] = useModelState<number>("glitch_vcc_normal");
    const [glitchVCCWait, setGlitchVCCWait] = useModelState<number>("glitch_vcc_config_wait");
    const [glitchVCCGlitchVoltage, setGlitchVCCGlitchVoltage] = useModelState<number>("glitch_vcc_config_level");
    const [glitchVCCCount, setGlitchVCCCount] = useModelState<number>("glitch_vcc_config_count");
    const [glitchVCCRepeat, setGlitchVCCRepeat] = useModelState<number>("glitch_vcc_config_repeat");
    const [glitchVCCDelay, setGlitchVCCDelay] = useModelState<number>("glitch_vcc_config_delay");
        const vccForce = () => {
        model.send({source: "glitchVCCForceButton", event: "onClick", args: {}});
    };

    const [glitchGNDNormalVoltage, setGlitchGNDNormalVoltage] = useModelState<number>("glitch_gnd_normal");
    const [glitchGNDWait, setGlitchGNDWait] = useModelState<number>("glitch_gnd_config_wait");
    const [glitchGNDGlitchVoltage, setGlitchGNDGlitchVoltage] = useModelState<number>("glitch_gnd_config_level");
    const [glitchGNDCount, setGlitchGNDCount] = useModelState<number>("glitch_gnd_config_count");
    const [glitchGNDRepeat, setGlitchGNDRepeat] = useModelState<number>("glitch_gnd_config_repeat");
    const [glitchGNDDelay, setGlitchGNDDelay] = useModelState<number>("glitch_gnd_config_delay");
    const gndForce = () => {
        model.send({source: "glitchGNDForceButton", event: "onClick", args: {}});
    };

    interface CLKFreqItem {
      name: string;
      tooltip: string;
      wave: number[];
    }
    const [glitchCLKFreqItems, ] = useModelState<Array<CLKFreqItem>>("glitch_clock_glitch_freq_items");
    const [glitchCLKFreqSelectedIdx, setGlitchCLKFreqSelectedIdx] = useModelState<number>("glitch_clock_glitch_selected_freq_item_idx");
    const [glitchCLKWait, setGlitchCLKWait] = useModelState<number>("glitch_clock_config_wait");
    const [glitchCLKCount, setGlitchCLKCount] = useModelState<number>("glitch_clock_config_count");
    const [glitchCLKRepeat, setGlitchCLKRepeat] = useModelState<number>("glitch_clock_config_repeat");
    const [glitchCLKDelay, setGlitchCLKDelay] = useModelState<number>("glitch_clock_config_delay");
    const addGlitchCLKFreqItem = (wave: number[]) => {
      model.send({source: "glitchClockFreqAddButton", event: "onClick", args: {wave: wave}});
    }
    const clkForce = () => {
        model.send({source: "glitchClockForceButton", event: "onClick", args: {}});
    };


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

    const clk = {
      freq: glitchCLKFreqItems.map((item, index) => ({
        label: item.name,
        value: index,
        title: item.tooltip
      })),
      setFreq: (index: number) => {
        setGlitchCLKFreqSelectedIdx(index)
      },

      defaultFreqIdx: glitchCLKFreqSelectedIdx,
      value: glitchCLKFreqSelectedIdx,

      wait: glitchCLKWait,
      setWait: setGlitchCLKWait,

      count: glitchCLKCount,
      setCount: setGlitchCLKCount,

      repeat: glitchCLKRepeat,
      setRepeat: setGlitchCLKRepeat,

      delay: glitchCLKDelay,
      setDelay: setGlitchCLKDelay,
    }

    const [glitchVCCWaitMin, glitchVCCWaitMax] = [1, 0xFFFF_FFFF];
    const [glitchVCCGlitchVoltageMin, glitchVCCGlitchVoltageMax] = [0.0, 4.0];
    const [glitchVCCCountMin, glitchVCCCountMax] = [1, 0xFFFF_FFFF];
    const [glitchVCCRepeatMin, glitchVCCRepeatMax] = [1, 0xFFFF_FFFF];

    const [glitchGNDWaitMin, glitchGNDWaitMax] = [1, 0xFFFF_FFFF];
    const [glitchGNDGlitchVoltageMin, glitchGNDGlitchVoltageMax] = [0.0, 4.0];
    const [glitchGNDCountMin, glitchGNDCountMax] = [1, 0xFFFF_FFFF];
    const [glitchGNDRepeatMin, glitchGNDRepeatMax] = [1, 0xFFFF_FFFF];

    const [glitchCLKWaitMin, glitchCLKWaitMax] = [1, 0xFFFF_FFFF];
    const [glitchCLKDelayMin, glitchCLKDelayMax] = [0, 0xFFFF_FFFF];
    const [glitchCLKRepeatMin, glitchCLKRepeatMax] = [1, 0xFFFF_FFFF];

    const [customFreqValue, setCustomFreqValue] = useState('');

    return (
        <Row>
            <Col span={24}>
                <Row>
                    <Col span={24}>
                        <Form layout={"inline"}>
                          <Form.Item label={"VCC"} style={{width: 35}}/>
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
                            <Form.Item label={intl.formatMessage({id: "cracker.config.glitch.vcc.wait"})}>
                                <InputNumber style={{width: 90}}
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
                          <Form.Item>
                              <Popover
                                content={"除了电压配置，其他参数均为时间长度，单位为10纳秒。"}
                                title="说明"
                                trigger="hover"
                              >
                                <QuestionCircleOutlined style={{ marginLeft: 8, cursor: 'pointer', color: 'black' }} />
                              </Popover>
                            </Form.Item>
                        </Form>
                    </Col>
                </Row>
                <Row>
                    <Col span={24}>
                        <Form layout={"inline"}>
                            <Form.Item label={"GND"} style={{width: 35}}/>
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
                            <Form.Item label={intl.formatMessage({id: "cracker.config.glitch.gnd.wait"})}>
                                <InputNumber style={{width: 90}}
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
                           <Form.Item>
                                <Button size={"small"} onClick={gndForce}>Force</Button>
                            </Form.Item>
                            <Form.Item>
                              <Popover
                                content={"除了电压配置，其他参数均为时间长度，单位为10纳秒。"}
                                title="说明"
                                trigger="hover"
                              >
                                <QuestionCircleOutlined style={{ marginLeft: 8, cursor: 'pointer', color: 'black' }} />
                              </Popover>
                            </Form.Item>
                        </Form>
                    </Col>
                </Row>
              <Row>
                    <Col span={24}>
                        <Form layout={"inline"}>
                            <Form.Item label={"CLK"} style={{width: 35}}/>
                            <Form.Item label={"时钟"}>
                              <Select
                                style={{ width: 238 }}
                                size={"small"}
                                placeholder="custom clock wave"
                                options={clk.freq}
                                onChange={clk.setFreq}
                                defaultValue={clk.defaultFreqIdx}
                                value={clk.value}
                                popupRender={(menu) => (
                                  <>
                                    {menu}
                                    <Divider style={{ margin: '8px 0' }} />
                                    <Input
                                      value={customFreqValue}
                                      size={"small"}
                                      style={{margin: '2px 1px 2px 1px'}}
                                      onKeyDown={(e) => {
                                        if (e.key === 'Enter') {
                                          const valueStr = e.currentTarget.value
                                          addGlitchCLKFreqItem(valueStr.split(",").map(Number))
                                          setCustomFreqValue('')
                                        }
                                        e.stopPropagation()
                                      }}
                                      onChange={(e) => setCustomFreqValue(e.target.value)}
                                    />
                                  </>
                                )}
                              />
                            </Form.Item>
                            <Form.Item label={intl.formatMessage({id: "cracker.config.glitch.gnd.wait"})}>
                                <InputNumber style={{width: 90}}
                                             step="1"
                                             stringMode
                                             size={"small"}
                                             min={glitchCLKWaitMin}
                                             max={glitchCLKWaitMax}
                                             value={clk.wait}
                                             parser={(v) => {
                                                 return Number(v);
                                             }}
                                             onChange={(v) => {
                                                 clk.setWait(Number(v));
                                             }}
                                             changeOnWheel
                                />
                            </Form.Item>
                            <Form.Item label={intl.formatMessage({id: "cracker.config.glitch.gnd.repeat"})}>
                                <InputNumber style={{width: 90}}
                                             step="1"
                                             stringMode
                                             size={"small"}
                                             min={glitchCLKRepeatMin}
                                             max={glitchCLKRepeatMax}
                                             value={clk.repeat}
                                             parser={(v) => {
                                                 return Number(v);
                                             }}
                                             onChange={(v) => {
                                                 clk.setRepeat(Number(v));
                                             }}
                                             changeOnWheel
                                />
                            </Form.Item>
                            <Form.Item label={intl.formatMessage({id: "cracker.config.glitch.gnd.delay"})}>
                                <InputNumber style={{width: 90}}
                                             step="1"
                                             stringMode
                                             size={"small"}
                                             min={glitchCLKDelayMin}
                                             max={glitchCLKDelayMax}
                                             value={clk.delay}
                                             parser={(v) => {
                                                 return Number(v);
                                             }}
                                             onChange={(v) => {
                                                 clk.setDelay(Number(v));
                                             }}
                                             changeOnWheel
                                />
                            </Form.Item>
                           <Form.Item>
                                <Button size={"small"} onClick={clkForce}>Force</Button>
                            </Form.Item>
                            <Form.Item>
                              <Popover
                                content={"除了时钟频率配置，其他参数均为时间长度，单位为10纳秒。"}
                                title="说明"
                                trigger="hover"
                              >
                                <QuestionCircleOutlined style={{ marginLeft: 8, cursor: 'pointer', color: 'black' }} />
                              </Popover>
                            </Form.Item>
                        </Form>
                    </Col>
                </Row>
            </Col>
        </Row>
    );
};

export default ConfigGlitch;