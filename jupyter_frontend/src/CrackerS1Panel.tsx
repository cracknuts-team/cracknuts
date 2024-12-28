import {
  Button,
  Checkbox,
  Col,
  Divider,
  Form,
  Input,
  InputNumber,
  Row,
  Select,
  Space,
  Spin,
  Switch,
  Tabs,
  Tag,
  Upload,
} from "antd";
import React, { ChangeEvent, useEffect, useState } from "react";
import { useModel, useModelState } from "@anywidget/react";
import {
  CheckOutlined,
  CloseOutlined,
  DownloadOutlined,
  InfoCircleOutlined,
  SaveOutlined,
  UploadOutlined,
} from "@ant-design/icons";
import TabPane from "antd/es/tabs/TabPane";
import AcquisitionPanel from "@/AcquisitionPanel.tsx";

interface CrackS1PanelProps {
  hasAcquisition?: boolean;
  connectStatusChanged?: (connected: boolean) => void;
}

const CrackerS1Panel: React.FC<CrackS1PanelProps> = ({ hasAcquisition = false, connectStatusChanged = undefined }) => {
  // 连接
  const [uri, setUri] = useModelState<string>("uri");
  const [connectStatus] = useModelState<boolean>("connect_status");
  const [buttonBusy, setButtonBusy] = useState<boolean>(false);

  const [crackerId] = useModelState<string>("cracker_id");
  const [crackerName] = useModelState<string>("cracker_name");
  const [crackerVersion] = useModelState<string>("cracker_version");

  const model = useModel();

  const getUri = () => {
    if (uri) {
      return uri.replace("cnp://", "");
    } else {
      return "";
    }
  };

  function connect(): void {
    setButtonBusy(true);
    model.send({ source: "connectButton", event: "onClick", args: { action: "connect" } });
    // setTimeout(() => setConnectStatus(2), 1000)
    // setTimeout(() => setConnectStatus(0), 3000)
  }

  function connectButtonOnClick() {
    if (connectStatus) {
      disconnect();
    } else {
      connect();
    }
  }

  function connectFinish(status: boolean): void {
    setButtonBusy(false);
    if (connectStatusChanged != undefined) {
      connectStatusChanged(status);
    }
  }

  if (connectStatusChanged != undefined) {
    connectStatusChanged(connectStatus);
  }

  function disconnect(): void {
    model.send({ source: "connectButton", event: "onClick", args: { action: "disconnect" } });
  }

  // nut配置

  const [nutEnable, setNutEnable] = useModelState<boolean>("nut_enable");
  const [nutVoltage, setNutVoltage] = useModelState<number>("nut_voltage");
  const [nutVoltageMin, nutVoltageMax] = [2000, 4100];
  const [nutClock, setNutClock] = useModelState<number>("nut_clock");

  // adc
  const [oscSampleRate, setOscSampleRate] = useModelState<number>("osc_sample_rate");
  const [oscSamplePhase, setOscSamplePhase] = useModelState<number>("osc_sample_phase");
  const [oscSampleLen, setOscSampleLen] = useModelState<number>("osc_sample_len");
  const [oscSampleDelay, setOscSampleDelay] = useModelState<number>("osc_sample_delay");
  const [channelAEnable, setChannelAEnable] = useModelState<boolean>("osc_analog_channel_a_enable");
  const [channelBEnable, setChannelBEnable] = useModelState<boolean>("osc_analog_channel_b_enable");

  const [oscTriggerSource, setOscTriggerSource] = useModelState<number>("osc_trigger_source");
  const [oscTriggerMode, setOscTriggerMode] = useModelState<number>("osc_trigger_mode");
  const [oscTriggerEdge, setOscTriggerEdge] = useModelState<number>("osc_trigger_edge");
  const [oscTriggerEdgeLevel, setOscTriggerEdgeLevel] = useModelState<number>("osc_trigger_edge_level");
  const [socAnalogChannelAGain, setOscAnalogChannelAGain] = useModelState<number>("osc_analog_channel_a_gain");
  const [socAnalogChannelBGain, setOscAnalogChannelBGain] = useModelState<number>("osc_analog_channel_b_gain");

  const dumpConfig = () => {
    model.send({ source: "dumpConfigButton", event: "onClick", args: {} });
  };

  const dumpConfigCompleted = (config: string) => {
    const blob = new Blob([config], { type: "text/plain" });
    const link = document.createElement("a");
    link.href = URL.createObjectURL(blob);
    link.download = "config.json";
    link.click();
    URL.revokeObjectURL(link.href);
  };

  const loadConfig = (config: string) => {
    model.send({ source: "loadConfigButton", event: "onClick", args: config });
  };

  const loadConfigCompleted = () => {
    // nothing.
  };

  const saveConfig = () => {
    model.send({ source: "saveConfigButton", event: "onClick", args: {} });
  };

  const uploadProp = {
    maxCount: 1,
    showUploadList: false,
    // @ts-expect-error option type ignore
    customRequest: (options) => {
      console.info(options);
      const reader = new FileReader();
      reader.readAsText(options.file);
      reader.onload = () => {
        loadConfig(JSON.parse(String(reader.result)));
      };
      options.onSuccess();
    },
  };

  const [acqStatus, setAcqStatus] = useState(0);

  useEffect(() => {
    // eslint-disable-next-line @typescript-eslint/ban-ts-comment
    // @ts-expect-error
    // eslint-disable-next-line @typescript-eslint/no-unused-vars
    const customCallback = (msg, _) => {
      if ("connectFinished" in msg) {
        connectFinish(msg["connectFinished"]);
      } else if ("dumpConfigCompleted" in msg) {
        dumpConfigCompleted(msg["dumpConfigCompleted"]);
      } else if ("loadConfigCompleted" in msg) {
        loadConfigCompleted();
      }
    };
    model.on("msg:custom", customCallback);

    // listen acq status disable disconnect when acq is running or testing.
    const changeCallback = () => {
      setAcqStatus(model.get("acq_status"));
    };

    changeCallback();

    model.on(`change:acq_status`, changeCallback);

    return () => {
      model.off("custom:custom", customCallback);
      model.off("change:acq_status", changeCallback);
    };
  });

  return (
    <div>
      <Row>
        <Col span={16}>
          <Space size={"large"}>
            <Space.Compact style={{ width: "400" }} size={"small"}>
              <Input
                addonBefore="cnp://"
                value={getUri()}
                onChange={(e: ChangeEvent<HTMLInputElement>) => {
                  setUri("cnp://" + e.target.value);
                }}
              />
              <Button type="primary" onClick={connectButtonOnClick} loading={buttonBusy} disabled={acqStatus != 0}>
                {connectStatus ? "断开" : "连接"}
              </Button>
            </Space.Compact>
            <span>
              <Tag icon={<InfoCircleOutlined />} color="success">
                Id: {crackerId}
              </Tag>
            </span>
            <span>
              <Tag icon={<InfoCircleOutlined />} color="success">
                Name: {crackerName}
              </Tag>
            </span>
            <span>
              <Tag icon={<InfoCircleOutlined />} color="success">
                Version: {crackerVersion}
              </Tag>
            </span>
          </Space>
        </Col>
        <Col span={8} style={{ textAlign: "right" }}>
          <Space.Compact>
            <Button icon={<SaveOutlined />} size={"small"} onClick={saveConfig} type="primary">
              保存配置
            </Button>
            <Upload {...uploadProp}>
              <Button icon={<DownloadOutlined />} size={"small"} type="primary">
                加载配置
              </Button>
            </Upload>
            <Button icon={<UploadOutlined />} size={"small"} onClick={dumpConfig} type="primary">
              导出配置
            </Button>
          </Space.Compact>
        </Col>
      </Row>
      <Spin indicator={<span></span>} spinning={!connectStatus}>
        <Row>
          {hasAcquisition && (
            <Col span={24} style={{ paddingTop: 15 }}>
              <AcquisitionPanel></AcquisitionPanel>
            </Col>
          )}
        </Row>
        <Row>
          <Col span={24} style={{ paddingBottom: 15 }}>
            <Spin indicator={<span></span>} spinning={acqStatus == 2 || acqStatus == -2}>
              <Tabs>
                <TabPane key={"1"} tab={"OSC配置"}>
                  <Row>
                    <Col span={24}>
                      <Row>
                        <Col span={24}>
                          <Form layout="inline">
                            <Form.Item>
                              <Space.Compact>
                                <Form.Item>
                                  <Checkbox
                                    checked={channelAEnable}
                                    onChange={(v) => {
                                      setChannelAEnable(v.target.checked);
                                    }}
                                  >
                                    Ch A 增益
                                  </Checkbox>
                                  <InputNumber
                                    suffix="%"
                                    step="1"
                                    size={"small"}
                                    min={1}
                                    max={100}
                                    changeOnWheel
                                    disabled={!channelAEnable}
                                    value={socAnalogChannelAGain}
                                    onChange={(v: number | string | null) => {
                                      if (v) {
                                        setOscAnalogChannelAGain(Number(v));
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
                                    checked={channelBEnable}
                                    onChange={(v) => {
                                      setChannelBEnable(v.target.checked);
                                    }}
                                  >
                                    Ch B 增益
                                  </Checkbox>
                                  <InputNumber
                                    suffix="%"
                                    step="1"
                                    size={"small"}
                                    min={1}
                                    max={100}
                                    changeOnWheel
                                    disabled={!channelBEnable}
                                    value={socAnalogChannelBGain}
                                    onChange={(v: number | string | null) => {
                                      if (v) {
                                        setOscAnalogChannelBGain(Number(v));
                                      }
                                    }}
                                  />
                                </Form.Item>
                              </Space.Compact>
                            </Form.Item>
                            <Form.Item label="采样点数">
                              <InputNumber
                                suffix=""
                                step="1"
                                size={"small"}
                                min={1024}
                                value={oscSampleLen}
                                defaultValue={oscSampleLen}
                                onChange={(v: number | string | null) => {
                                  if (v) {
                                    setOscSampleLen(Number(v));
                                  }
                                }}
                                changeOnWheel
                              />
                            </Form.Item>
                            <Form.Item label="延迟点数">
                              <InputNumber
                                suffix=""
                                step="1"
                                size={"small"}
                                min={0}
                                defaultValue={oscSampleDelay}
                                value={oscSampleDelay}
                                onChange={(v: number | string | null) => {
                                  if (v) {
                                    setOscSampleDelay(Number(v));
                                  }
                                }}
                                changeOnWheel
                              />
                            </Form.Item>
                          </Form>
                        </Col>
                      </Row>
                      <Divider variant="dotted" style={{ marginTop: 5, marginBottom: 5 }} />
                      <Row>
                        <Col>
                          <Form layout={"inline"}>
                            <Form.Item label="采样频率">
                              <Select
                                size={"small"}
                                options={[
                                  { value: 65000, label: "65 mHz" },
                                  { value: 48000, label: "48 mHz" },
                                  { value: 24000, label: "24 mHz" },
                                  { value: 12000, label: "12 mHz" },
                                  { value: 8000, label: "8 mHz" },
                                  { value: 4000, label: "4 mHz" },
                                ]}
                                value={oscSampleRate}
                                onChange={setOscSampleRate}
                                style={{ minWidth: 100 }}
                              ></Select>
                            </Form.Item>
                            <Form.Item label="采样相位">
                              <InputNumber
                                suffix="°"
                                step="10"
                                stringMode
                                size={"small"}
                                min={-360}
                                max={360}
                                value={oscSamplePhase}
                                onChange={(v) => {
                                  setOscSamplePhase(Number(v));
                                }}
                                changeOnWheel
                              />
                            </Form.Item>
                          </Form>
                          <Divider variant="dotted" style={{ marginTop: 5, marginBottom: 5 }} />
                          <Form layout={"inline"}>
                            <Form.Item label="触发源(SR)">
                              <Select
                                size={"small"}
                                defaultValue={0}
                                options={[
                                  { label: "N (Nut)", value: 0 },
                                  { label: "A (Ch A)", value: 1 },
                                  { label: "B (Ch B)", value: 2 },
                                  { label: "P (Protocol)", value: 3 },
                                ]}
                                style={{ width: 110 }}
                                value={oscTriggerSource}
                                onChange={setOscTriggerSource}
                              />
                            </Form.Item>
                            <Form.Item label="触发模式(MD)">
                              <Select
                                size={"small"}
                                defaultValue={0}
                                options={[
                                  { label: "边沿", value: 0 },
                                  { label: "波形", value: 1 },
                                ]}
                                style={{ width: 100 }}
                                value={oscTriggerMode}
                                onChange={setOscTriggerMode}
                              />
                            </Form.Item>
                            <Form.Item label="边缘类型(EG)">
                              <Select
                                size={"small"}
                                defaultValue={0}
                                options={[
                                  { label: "上升", value: 0 },
                                  { label: "下降", value: 1 },
                                  { label: "任意", value: 2 },
                                ]}
                                style={{ width: 100 }}
                                value={oscTriggerEdge}
                                onChange={setOscTriggerEdge}
                              />
                            </Form.Item>
                            <Form.Item label="触发源级别">
                              <InputNumber
                                suffix=""
                                step="1"
                                size={"small"}
                                changeOnWheel
                                value={oscTriggerEdgeLevel}
                                onChange={(value) => {
                                  if (value) {
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
                </TabPane>
                <TabPane key={"2"} tab={"NUT配置"}>
                  <Row>
                    <Col span={24}>
                      <Form layout={"inline"}>
                        <Form.Item label="供电使能">
                          <Switch
                            size={"small"}
                            checkedChildren={<CheckOutlined />}
                            unCheckedChildren={<CloseOutlined />}
                            value={nutEnable}
                            onChange={(c) => {
                              setNutEnable(c);
                            }}
                          />
                        </Form.Item>
                        <Form.Item label="NUT电压">
                          <InputNumber
                            suffix="V"
                            step="100"
                            stringMode
                            size={"small"}
                            min={nutVoltageMin}
                            max={nutVoltageMax}
                            value={nutVoltage}
                            formatter={(v) => {
                              return Number(Number(v) / 1000).toFixed(1);
                            }}
                            parser={(v) => {
                              return Number(v) * 1000;
                            }}
                            onChange={(v) => {
                              setNutVoltage(Number(v));
                            }}
                            changeOnWheel
                          />
                        </Form.Item>
                        <Form.Item label="NUT时钟">
                          <Select
                            size={"small"}
                            options={[
                              { value: 65000, label: "65 mHz" },
                              { value: 48000, label: "48 mHz" },
                              { value: 24000, label: "24 mHz" },
                              { value: 12000, label: "12 mHz" },
                              { value: 8000, label: "8 mHz" },
                              { value: 4000, label: "4 mHz" },
                            ]}
                            value={nutClock}
                            onChange={setNutClock}
                            style={{ minWidth: 100 }}
                          ></Select>
                        </Form.Item>
                      </Form>
                    </Col>
                  </Row>
                </TabPane>
              </Tabs>
            </Spin>
          </Col>
        </Row>
      </Spin>
    </div>
  );
};

export default CrackerS1Panel;
