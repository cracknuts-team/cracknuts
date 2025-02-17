import {Button, Checkbox, Col, Divider, Form, Input, InputNumber, Row, Select, Space, Spin, Tag, Upload,} from "antd";
import React, {ChangeEvent, useEffect, useState} from "react";
import {useModel, useModelState} from "@anywidget/react";
import {DownloadOutlined, InfoCircleOutlined, SaveOutlined, UploadOutlined,} from "@ant-design/icons";
import AcquisitionPanel from "@/AcquisitionPanel.tsx";
import {FormattedMessage, useIntl} from "react-intl";

interface CrackS1PanelProps {
  hasAcquisition?: boolean;
  connectStatusChanged?: (connected: boolean) => void;
  languageChanged?: (language: string) => void;
}

const CrackerS1Panel: React.FC<CrackS1PanelProps> = ({hasAcquisition = false, connectStatusChanged = undefined, languageChanged = undefined}) => {
  // 连接
  const [uri, setUri] = useModelState<string>("uri");
  const [connectStatus] = useModelState<boolean>("connect_status");
  const [buttonBusy, setButtonBusy] = useState<boolean>(false);

  const [crackerId] = useModelState<string>("cracker_id");
  const [crackerName] = useModelState<string>("cracker_name");
  const [crackerVersion] = useModelState<string>("cracker_version");

  const model = useModel();

  const intl = useIntl();

  const getUri = () => {
    if (uri) {
      return uri.replace("cnp://", "");
    } else {
      return "";
    }
  };

  function connect(): void {
    setButtonBusy(true);
    model.send({source: "connectButton", event: "onClick", args: {action: "connect"}});
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
    model.send({source: "connectButton", event: "onClick", args: {action: "disconnect"}});
  }

  // nut配置

  const [nutEnable, setNutEnable] = useModelState<boolean>("nut_enable");
  const [nutClockEnable, setNutClockEnable] = useModelState<boolean>("nut_clock_enable");
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
    model.send({source: "dumpConfigButton", event: "onClick", args: {}});
  };

  const dumpConfigCompleted = (config: string) => {
    const blob = new Blob([config], {type: "text/plain"});
    const link = document.createElement("a");
    link.href = URL.createObjectURL(blob);
    link.download = "config.json";
    link.click();
    URL.revokeObjectURL(link.href);
  };

  const loadConfig = (config: string) => {
    model.send({source: "loadConfigButton", event: "onClick", args: config});
  };

  const loadConfigCompleted = () => {
    // nothing.
  };

  const saveConfig = () => {
    model.send({source: "saveConfigButton", event: "onClick", args: {}});
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

  const lMap: Record<string, string> = {
    'en': 'En',
    'zh': '中'
  }
  const [language, setLanguage] = useState(lMap[intl.locale]);
  const changeLanguage = () => {
    let languageCode;
    if (language == '中') {
      setLanguage('En');
      languageCode = 'en'
    } else {
      setLanguage('中');
      languageCode = 'zh'
    }
    if (languageChanged) {
      languageChanged(languageCode);
    }
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
            <Space.Compact style={{width: "400"}} size={"small"}>
              <Input
                addonBefore="cnp://"
                value={getUri()}
                onChange={(e: ChangeEvent<HTMLInputElement>) => {
                  setUri("cnp://" + e.target.value);
                }}
              />
              <Button type="primary" onClick={connectButtonOnClick} loading={buttonBusy} disabled={acqStatus != 0}>
                {connectStatus ? intl.formatMessage({id: 'cracker.disconnect'})
                    : intl.formatMessage({id: 'cracker.connect'})}
              </Button>
            </Space.Compact>
            <span>
              <Tag icon={<InfoCircleOutlined/>} color="success">
                <FormattedMessage id={"cracker.id"}/>: {crackerId}
              </Tag>
            </span>
            <span>
              <Tag icon={<InfoCircleOutlined/>} color="success">
                <FormattedMessage id={"cracker.name"}/>: {crackerName}
              </Tag>
            </span>
            <span>
              <Tag icon={<InfoCircleOutlined/>} color="success">
                <FormattedMessage id={"cracker.version"}/>: {crackerVersion}
              </Tag>
            </span>
          </Space>
        </Col>
        <Col span={7} style={{textAlign: "right"}}>
          <Space.Compact>
            <Button icon={<SaveOutlined/>} size={"small"} onClick={saveConfig} type="primary">
              <FormattedMessage id={"cracknuts.config.save"}/>
            </Button>
            <Upload {...uploadProp}>
              <Button icon={<DownloadOutlined/>} size={"small"} type="primary">
                <FormattedMessage id={"cracknuts.config.load"}/>
              </Button>
            </Upload>
            <Button icon={<UploadOutlined/>} size={"small"} onClick={dumpConfig} type="primary">
              <FormattedMessage id={"cracknuts.config.dump"}/>
            </Button>
          </Space.Compact>
        </Col>
        <Col span={1} style={{textAlign: "right"}}>
            <Button size={"small"} variant="text" color="default" onClick={changeLanguage}>
              <span style={{fontSize: '0.8em', width: 13, textAlign: 'center'}}>{language}</span>
            </Button>
        </Col>
      </Row>
      <Spin indicator={<span></span>} spinning={!connectStatus}>
        <Row>
          {hasAcquisition && (
            <Col span={24} style={{paddingTop: 15, paddingBottom: 15}}>
              <AcquisitionPanel></AcquisitionPanel>
            </Col>
          )}
        </Row>
        <Row>
          <Col span={24} style={{paddingBottom: 15}}>
            <Spin indicator={<span></span>} spinning={acqStatus == 2 || acqStatus == -2}>
              <Divider orientation="left" style={{marginTop: 15, marginBottom: 5, borderColor: '#3da9c7'}}>NUT</Divider>
              <Row>
                <Col span={24}>
                  <Form layout={"inline"}>
                    <Form.Item>
                      <Checkbox checked={nutEnable} onChange={() => {setNutEnable(!nutEnable)}}>
                        <FormattedMessage id={"cracker.config.nut.power"}/>
                      </Checkbox>
                      <InputNumber style={{width: 90}}
                        disabled={!nutEnable}
                        addonAfter="V"
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
                    <Form.Item>
                      <Checkbox checked={nutClockEnable} onChange={() => {
                        setNutClockEnable(!nutClockEnable)
                      }}>
                        <FormattedMessage id={"cracker.config.nut.clock"}/>
                      </Checkbox>
                      <Space.Compact>
                        <Select
                            disabled={!nutClockEnable}
                            size={"small"}
                            options={[
                              {value: 24000, label: "24 M"},
                              {value: 12000, label: "12 M"},
                              {value: 8000, label: "8  M"},
                              {value: 4000, label: "4  M"},
                            ]}
                            value={nutClock}
                            onChange={setNutClock}
                            style={{width: 80}}
                        ></Select>
                        <Button style={{pointerEvents: "none", opacity: 1, cursor: "default"}}
                                size={"small"}>Hz</Button>
                      </Space.Compact>
                    </Form.Item>
                  </Form>
                </Col>
              </Row>
              <Divider orientation="left" style={{marginTop: 15, marginBottom: 5, borderColor: '#3da9c7'}}>SCOPE</Divider>
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
                                {value: 4000, label: "4  M"},
                              ]}
                              value={oscSampleRate}
                              onChange={setOscSampleRate}
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
                                checked={channelAEnable}
                                onChange={(v) => {
                                  setChannelAEnable(v.target.checked);
                                }}
                              >
                                <FormattedMessage id={"cracker.config.scope.channel.a.gain"}/>
                              </Checkbox>
                              <InputNumber
                                addonAfter="%"
                                style={{width: 100}}
                                step="1"
                                size={"small"}
                                min={1}
                                max={100}
                                changeOnWheel
                                disabled={!channelAEnable}
                                value={socAnalogChannelAGain}
                                onChange={(v: number | string | null) => {
                                  if (v != null) {
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
                                <FormattedMessage id={"cracker.config.scope.channel.b.gain"}/>
                              </Checkbox>
                              <InputNumber
                                addonAfter="%"
                                style={{width: 100}}
                                step="1"
                                size={"small"}
                                min={1}
                                max={100}
                                changeOnWheel
                                disabled={!channelBEnable}
                                value={socAnalogChannelBGain}
                                onChange={(v: number | string | null) => {
                                  if (v != null) {
                                    setOscAnalogChannelBGain(Number(v));
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
                            value={oscSampleLen}
                            defaultValue={oscSampleLen}
                            onChange={(v: number | string | null) => {
                              if (v != null) {
                                setOscSampleLen(Number(v));
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
                              {label: intl.formatMessage({id: "cracker.config.scope.triggerMode.waveform"}), value: 1},
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
                              {label: intl.formatMessage({id: "cracker.config.scope.triggerEdge.rising"}), value: 0},
                              {label: intl.formatMessage({id: "cracker.config.scope.triggerEdge.falling"}), value: 1},
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
            </Spin>
          </Col>
        </Row>
      </Spin>
    </div>
  );
};

export default CrackerS1Panel;
