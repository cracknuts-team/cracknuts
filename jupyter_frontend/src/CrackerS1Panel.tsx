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
  Tooltip,
  Upload,
} from "antd";
import React, {ChangeEvent, useEffect, useState} from "react";
import {useModel, useModelState} from "@anywidget/react";
import {DownloadOutlined, SaveOutlined, UploadOutlined,} from "@ant-design/icons";
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

  // const [crackerId] = useModelState<string>("cracker_id");
  // const [crackerName] = useModelState<string>("cracker_name");
  // const [crackerVersion] = useModelState<string>("cracker_version");

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

  // nut
  const [nutEnable, setNutEnable] = useModelState<boolean>("nut_enable");
  const [nutClockEnable, setNutClockEnable] = useModelState<boolean>("nut_clock_enable");
  const [nutVoltage, setNutVoltage] = useModelState<number>("nut_voltage");
  const [nutVoltageMin, nutVoltageMax] = [2.0, 4.1];
  const [nutClock, setNutClock] = useModelState<number>("nut_clock");

  const [nutUartEnable, setNutUartEnable] = useModelState<boolean>("nut_uart_enable")
  const [nutUartBaudrate, setNutUartBaudrate] = useModelState<number>("nut_uart_baudrate");
  const [nutUartBytesize, setNutUartBytesize] = useModelState<number>("nut_uart_bytesize");
  const [nutUartParity, setNutUartParity] = useModelState<number>("nut_uart_parity");
  const [nutUartStopbits, setNutUartStopbits] = useModelState<number>("nut_uart_stopbits");

  const [nutSpiEnable, setNutSpiEnable] = useModelState<boolean>("nut_spi_enable");
  const [nutSpiSpeed, setNutSpiSpeed] = useModelState<number>("nut_spi_speed");
  const [nutSpiCpol, setNutSpiCpol] = useModelState<number>("nut_spi_cpol");
  const [nutSpiCpha, setNutSpiCpha] = useModelState<number>("nut_spi_cpha");
  const [nutSpiAutoSelect, setSpiAutoSelect] = useModelState<boolean>("nut_spi_auto_select");

  const [nutI2cEnable, setNutI2cEnable] = useModelState<boolean>("nut_i2c_enable");
  const [nutI2cDevAddr, setNutI2cDevAddr] = useModelState<string>("nut_i2c_dev_addr");
  const [nutI2cSpeed, setNutI2cSpeed] = useModelState<number>("nut_i2c_speed");

  // osc
  const [oscSampleRate, setOscSampleRate] = useModelState<number>("osc_sample_rate");
  const [oscSamplePhase, setOscSamplePhase] = useModelState<number>("osc_sample_phase");
  const [oscSampleLength, setOscSampleLength] = useModelState<number>("osc_sample_length");
  const [oscSampleDelay, setOscSampleDelay] = useModelState<number>("osc_sample_delay");
  const [channelAEnable, setChannelAEnable] = useModelState<boolean>("osc_analog_channel_a_enable");
  const [channelBEnable, setChannelBEnable] = useModelState<boolean>("osc_analog_channel_b_enable");

  const [oscTriggerSource, setOscTriggerSource] = useModelState<number>("osc_trigger_source");
  const [oscTriggerMode, setOscTriggerMode] = useModelState<number>("osc_trigger_mode");
  const [oscTriggerEdge, setOscTriggerEdge] = useModelState<number>("osc_trigger_edge");
  const [oscTriggerEdgeLevel, setOscTriggerEdgeLevel] = useModelState<number>("osc_trigger_edge_level");
  const [socAnalogChannelAGain, setOscAnalogChannelAGain] = useModelState<number>("osc_analog_channel_a_gain");
  const [socAnalogChannelBGain, setOscAnalogChannelBGain] = useModelState<number>("osc_analog_channel_b_gain");

  const [panelConfigDifferentFromCrackerConfig] = useModelState<boolean>("panel_config_different_from_cracker_config");

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

  const writeConfig = () => {
    model.send({source: "writeConfigButton", event: "onClick", args: {}});
  };

  const readConfig = () => {
    model.send({source: "readConfigButton", event: "onClick", args: {}});
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
      <Row justify="space-between">
        <Col flex={"auto"}>
          <Space size={"large"} style={{paddingTop: "5px", paddingBottom: "5px"}}>
            <Space.Compact style={{maxWidth: "18em", minWidth: "18em"}} size={"small"}>
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
            {/*<span>*/}
            {/*  <Tag icon={<InfoCircleOutlined/>} color="success">*/}
            {/*    <FormattedMessage id={"cracker.id"}/>: {crackerId}*/}
            {/*  </Tag>*/}
            {/*</span>*/}
            {/*<span>*/}
            {/*  <Tag icon={<InfoCircleOutlined/>} color="success">*/}
            {/*    <FormattedMessage id={"cracker.name"}/>: {crackerName}*/}
            {/*  </Tag>*/}
            {/*</span>*/}
            {/*<span>*/}
            {/*  <Tag icon={<InfoCircleOutlined/>} color="success">*/}
            {/*    <FormattedMessage id={"cracker.version"}/>: {crackerVersion}*/}
            {/*  </Tag>*/}
            {/*</span>*/}
          </Space>
        </Col>
        <Col style={{marginLeft: "auto"}}>
          <Form layout={"inline"}>
            <Form.Item>
              <Tooltip title={panelConfigDifferentFromCrackerConfig ? "当前配置与设备不同步，写入当前控制面板中的配置信息到Cracker" : "写入当前控制面板中的配置信息到Cracker"}>
                <Button icon={<SaveOutlined/>} size={"small"} onClick={writeConfig} color={panelConfigDifferentFromCrackerConfig ? "danger" : "primary"} variant="solid">
                  写入配置
                </Button>
              </Tooltip>
            </Form.Item>
            <Form.Item>
              <Tooltip title={"读取Cracker中的配置信息到控制面板"}>
                <Button icon={<SaveOutlined/>} size={"small"} onClick={readConfig} type="primary">
                  读取配置
                </Button>
              </Tooltip>
            </Form.Item>
            <Form.Item>
              <Tooltip title={"保存控制面板中的配置到配置文件"}>
                <Button icon={<SaveOutlined/>} size={"small"} onClick={saveConfig} type="primary">
                  <FormattedMessage id={"cracknuts.config.save"}/>
                </Button>
              </Tooltip>
            </Form.Item>
            <Form.Item>
              <Tooltip title={"上传配置文件到控制面板"}>
                <Upload {...uploadProp}>
                  <Button icon={<DownloadOutlined/>} size={"small"} type="primary">
                    <FormattedMessage id={"cracknuts.config.load"}/>
                  </Button>
                </Upload>
              </Tooltip>
            </Form.Item>
            <Form.Item>
              <Tooltip title={"导出控制面板中的配置到配置文件"}>
                <Button icon={<UploadOutlined/>} size={"small"} onClick={dumpConfig} type="primary">
                  <FormattedMessage id={"cracknuts.config.dump"}/>
                </Button>
              </Tooltip>
            </Form.Item>
            <Form.Item>
              <Button size={"small"} variant="text" color="default" onClick={changeLanguage}>
                <span style={{fontSize: '0.8em', width: 13, textAlign: 'center'}}>{language}</span>
              </Button>
            </Form.Item>
          </Form>
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
                        step="0.1"
                        stringMode
                        size={"small"}
                        min={nutVoltageMin}
                        max={nutVoltageMax}
                        value={nutVoltage}
                        parser={(v) => {
                          return Number(v);
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
              {/*    </Form>*/}
              {/*  </Col>*/}
              {/*</Row>*/}
              {/*<Row>*/}
              {/*  <Col span={24}>*/}
              {/*    <Form layout={"inline"}>*/}
                    <Form.Item style={{marginRight: 1}}>
                      <Checkbox id={"cracker_config_uart_enable"} checked={nutUartEnable} onChange={() => {
                        setNutUartEnable(!nutUartEnable);
                      }}><FormattedMessage id={"cracker.config.nut.uart.enable"}/></Checkbox>
                    </Form.Item>
                    <Form.Item label={intl.formatMessage({id: "cracker.config.nut.uart.baudrate"})}>
                      <Space.Compact>
                        <Select id={"cracker_config_uart_baudrate"} size={"small"} style={{minWidth: 90}} disabled={!nutUartEnable} value={nutUartBaudrate}
                          onChange={setNutUartBaudrate} options={[
                          {value: 0, label: "9600"},
                          {value: 1, label: "19200"},
                          {value: 2, label: "38400"},
                          {value: 3, label: "57600"},
                          {value: 4, label: "115200"},
                          {value: 5, label: "1000000"},
                        ]}/>
                      </Space.Compact>
                    </Form.Item>
                    <Form.Item label={intl.formatMessage({id: "cracker.config.nut.uart.bytesize"})}>
                      <Space.Compact>
                        <Select id={"cracker_config_uart_bytesize"} size={"small"} style={{minWidth: 90}} disabled={!nutUartEnable}
                          value={nutUartBytesize} onChange={setNutUartBytesize} options={[
                          {value: 5, label: "5"},
                          {value: 6, label: "6"},
                          {value: 7, label: "7"},
                          {value: 8, label: "8"},
                        ]}/>
                      </Space.Compact>
                    </Form.Item>
                    <Form.Item label={intl.formatMessage({id: "cracker.config.nut.uart.parity"})}>
                      <Space.Compact>
                        <Select id={"cracker_config_uart_parity"} size={"small"} style={{minWidth: 90}} disabled={!nutUartEnable}
                          value={nutUartParity} onChange={setNutUartParity} options={[
                          {value: 0, label: intl.formatMessage({id: "cracker.config.nut.uart.parity.none"})},
                          {value: 1, label: intl.formatMessage({id: "cracker.config.nut.uart.parity.even"})},
                          {value: 2, label: intl.formatMessage({id: "cracker.config.nut.uart.parity.odd"})},
                          {value: 3, label: intl.formatMessage({id: "cracker.config.nut.uart.parity.mark"})},
                          {value: 4, label: intl.formatMessage({id: "cracker.config.nut.uart.parity.space"})},
                        ]}/>
                      </Space.Compact>
                    </Form.Item>
                    <Form.Item label={intl.formatMessage({id: "cracker.config.nut.uart.stopbits"})}>
                      <Space.Compact>
                        <Select id={"cracker_config_uart_stopbits"} size={"small"} style={{minWidth: 90}} disabled={!nutUartEnable}
                          value={nutUartStopbits} onChange={setNutUartStopbits} options={[
                          {value: 0, label: "1"},
                          {value: 1, label: "1.5"},
                          {value: 2, label: "2"},
                        ]}/>
                      </Space.Compact>
                    </Form.Item>
              {/*    </Form>*/}
              {/*  </Col>*/}
              {/*</Row>*/}
              {/*<Row>*/}
              {/*  <Col span={24}>*/}
              {/*    <Form layout={"inline"}>*/}
                    <Form.Item style={{marginRight: 1}}>
                      <Checkbox id={"cracker_config_spi_enable"} checked={nutSpiEnable} onChange={() => {setNutSpiEnable(!nutSpiEnable)}}>
                        <FormattedMessage id={"cracker.config.nut.spi.enable"}/>
                      </Checkbox>
                    </Form.Item>
                    <Form.Item label={intl.formatMessage({id: "cracker.config.nut.spi.speed"})}>
                      <InputNumber id={"cracker_config_spi_speed"} value={nutSpiSpeed} onChange={(v) => {
                          setNutSpiSpeed(Number(v));
                        }} size={"small"} disabled={!nutSpiEnable}/>
                    </Form.Item>
                    <Form.Item label={intl.formatMessage({id: "cracker.config.nut.spi.cpol"})}>
                      <Space.Compact>
                        <Select id={"cracker_config_spi_cpol"} size={"small"} style={{minWidth: 90}} disabled={!nutSpiEnable}
                           value={nutSpiCpol} onChange={setNutSpiCpol} options={[
                          {value: 0, label: intl.formatMessage({id: "cracker.config.nut.spi.cpol.low"})},
                          {value: 1, label: intl.formatMessage({id: "cracker.config.nut.spi.cpol.high"})},
                        ]}/>
                      </Space.Compact>
                    </Form.Item>
                    <Form.Item label={intl.formatMessage({id: "cracker.config.nut.spi.cpha"})}>
                      <Space.Compact>
                        <Select id={"cracker_config_spi_cpha"} size={"small"} style={{minWidth: 90}} disabled={!nutSpiEnable}
                          value={nutSpiCpha} onChange={setNutSpiCpha} options={[
                          {value: 0, label: intl.formatMessage({id: "cracker.config.nut.spi.cpha.low"})},
                          {value: 1, label: intl.formatMessage({id: "cracker.config.nut.spi.cpha.high"})},
                        ]}/>
                      </Space.Compact>
                    </Form.Item>
                    <Form.Item style={{marginRight: 1}}>
                      <Checkbox id={"cracker_config_spi_auto_select"} checked={nutSpiAutoSelect} onChange={() => {setSpiAutoSelect(!nutSpiAutoSelect)}}>
                        <FormattedMessage id={"cracker.config.nut.spi.autoSelect"}/>
                      </Checkbox>
                    </Form.Item>
              {/*    </Form>*/}
              {/*  </Col>*/}
              {/*</Row>*/}
              {/*<Row>*/}
              {/*  <Col>*/}
              {/*    <Form layout={"inline"}>*/}
                    <Form.Item style={{marginRight: 1}}>
                      <Checkbox id={"cracker_config_i2c_enable"} checked={nutI2cEnable} onChange={() => {setNutI2cEnable(!nutI2cEnable)}}>
                        <FormattedMessage id={"cracker.config.nut.i2c.enable"}/>
                      </Checkbox>
                    </Form.Item>
                    <Form.Item label={intl.formatMessage({id: "cracker.config.nut.i2c.dev_addr"})}>
                      <Input id={"cracker_config_i2c_dev_addr"} value={nutI2cDevAddr} onChange={(e: ChangeEvent<HTMLInputElement>) => setNutI2cDevAddr(e.target.value)}
                             disabled={!nutI2cEnable} size={"small"} style={{width: 90}}/>
                    </Form.Item>
                     <Form.Item label={intl.formatMessage({id: "cracker.config.nut.i2c.speed"})}>
                      <Space.Compact>
                        <Select id={"cracker_config_i2c_speed"} size={"small"} style={{minWidth: 90}} disabled={!nutI2cEnable}
                          value={nutI2cSpeed} onChange={setNutI2cSpeed} options={[
                          {value: 0, label: "100K"},
                          {value: 1, label: "400K"},
                          {value: 2, label: "1M"},
                          {value: 3, label: "3400K"},
                          {value: 4, label: "5M"},
                        ]}/>
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
