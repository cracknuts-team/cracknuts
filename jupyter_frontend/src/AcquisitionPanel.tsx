import {useModel, useModelState} from "@anywidget/react";
import {Col, Form, Input, InputNumber, Progress, Radio, Row, Select} from "antd";
import {CheckboxChangeEvent} from "antd/es/checkbox";
import React, {ChangeEvent} from "react";
import {FormattedMessage, useIntl} from "react-intl";

interface AcqRunProgress {
  finished: number;
  total: number;
}

const AcquisitionPanel: React.FC = () => {
  const [acqStatus] = useModelState<number>("acq_status"); // 0 停止 1 测试 2 运行
  const [acqRunProgress] = useModelState<AcqRunProgress>("acq_run_progress"); //{'finished': 1, total: 1000}
  const [traceCount, setTraceCount] = useModelState<number>("trace_count");
  // const [sampleOffset, setSampleOffset] = useModelState<number>("sample_offset");
  // const [sampleLength, setSampleLength] = useModelState<number>("sample_length");
  const [triggerJudgeWaitTime, setTriggerJudgeWaitTime] = useModelState<number>("trigger_judge_wait_time");
  const [triggerJudgeTimeout, setTriggerJudgeTimeout] = useModelState<number>("trigger_judge_timeout");
  const [doErrorCountMax, setDoErrorCountMax] = useModelState<number>("do_error_max_count");
  const [fileFormat, setFileFormat] = useModelState<string>("file_format");
  const [filePath, setFilePath] = useModelState<string>("file_path");
  const [traceFetchInterval, setTraceFetchInterval] = useModelState<string>("trace_fetch_interval");

  const model = useModel();

  const intl = useIntl();

  function run(status: number) {
    if (status == -1) {
      model.send({ source: "acqStatusButton", event: "onChange", args: { status: "pause" } });
    } else if (status == 1) {
      model.send({ source: "acqStatusButton", event: "onChange", args: { status: "test" } });
    } else if (status == 2) {
      model.send({ source: "acqStatusButton", event: "onChange", args: { status: "run" } });
    } else {
      // stop
      model.send({ source: "acqStatusButton", event: "onChange", args: { status: "stop" } });
    }
    setFrontStatus(status);
  }

  React.useEffect(() => {
    const callback = () => {
      const backStatus = model.get("acq_status");
      setFrontStatus(backStatus >= 0 ? backStatus : -1);
    };
    model.on("change:acq_status", callback);
    callback();
    return () => model.off(`change:acq_status`, callback);
  }, [model]);

  const [frontStatus, setFrontStatus] = React.useState<number>(0);

  function checkFrontBackStatusSync() {
    return (frontStatus > 0 && frontStatus != acqStatus) || (frontStatus < 0 && acqStatus > 0);
  }

  const conicColors = [
    '#0066ff',
    '#0099cc',
    '#00cccc',
    '#00ff99',
    '#00ff00',
  ]

  return (
    <div>
      <Row>
        <Col span={24}>
          <Form layout={"inline"}>
            <Form.Item>
              <Radio.Group
                value={frontStatus}
                buttonStyle="solid"
                onChange={(e: CheckboxChangeEvent) => {
                  run(Number(e.target.value));
                }}
                size={"small"}
              >
                <Radio.Button value={1} disabled={acqStatus == 2 || acqStatus == -2 || checkFrontBackStatusSync()}>
                  <FormattedMessage id={"acquisition.test"}/>
                </Radio.Button>
                <Radio.Button value={2} disabled={acqStatus == 1 || acqStatus == -1 || checkFrontBackStatusSync()}>
                  <FormattedMessage id={"acquisition.run"}/>
                </Radio.Button>
                <Radio.Button value={-1} disabled={acqStatus == 0 || checkFrontBackStatusSync()}>
                  <FormattedMessage id={"acquisition.pause"}/>
                </Radio.Button>
                <Radio.Button value={0} disabled={checkFrontBackStatusSync()}>
                  <FormattedMessage id={"acquisition.stop"}/>
                </Radio.Button>
              </Radio.Group>
            </Form.Item>
            <Form.Item label={intl.formatMessage({id: "acquisition.traceCount"})}>
              <InputNumber
                size={"small"}
                value={traceCount}
                onChange={(v) => {
                  setTraceCount(Number(v));
                }}
                changeOnWheel
              />
            </Form.Item>
            <Form.Item label={intl.formatMessage({id: "acquisition.triggerJudgeWaitTime"})}>
              <InputNumber
                style={{width: 100}}
                size={"small"}
                value={triggerJudgeWaitTime}
                addonAfter={intl.formatMessage({id: "cracker.config.unit.second"})}
                min={0.05}
                step={0.01}
                onChange={(v) => {
                  setTriggerJudgeWaitTime(Number(v));
                }}
                changeOnWheel
              />
            </Form.Item>
            <Form.Item label={intl.formatMessage({id: "acquisition.triggerJudgeTimeout"})}>
              <InputNumber
                style={{width: 100}}
                size={"small"}
                value={triggerJudgeTimeout}
                addonAfter={intl.formatMessage({id: "cracker.config.unit.second"})}
                min={0.05}
                step={0.01}
                onChange={(v) => {
                  setTriggerJudgeTimeout(Number(v));
                }}
                changeOnWheel
              />
            </Form.Item>
            <Form.Item label={intl.formatMessage({id: "acquisition.traceFetchInterval"})}>
              <Select size={"small"} style={{width: 70}} options={[
                {value: 1, label: "1s"},
                {value: 2, label: "2s"},
                {value: 3, label: "3s"},
                {value: 4, label: "4s"},
                {value: 5, label: "5s"},
                {value: 10, label: "10s"},
                {value: 15, label: "15s"},
                {value: 20, label: "20s"},
                {value: 25, label: "25s"},
                {value: 30, label: "30s"},
              ]} onChange={setTraceFetchInterval} value={traceFetchInterval}/>
            </Form.Item>
            <Form.Item label={intl.formatMessage({id: "acquisition.doErrorCountMax"})}>
              <InputNumber
                size={"small"}
                value={doErrorCountMax}
                min={-1}
                onChange={(v) => {
                  setDoErrorCountMax(Number(v));
                }}
                changeOnWheel
              />
            </Form.Item>
            <Form.Item label={intl.formatMessage({id: "acquisition.fileFormat"})}>
              <Select
                size={"small"}
                options={[
                  { value: "scarr", label: "Scarr" },
                  { value: "numpy", label: "Numpy" },
                ]}
                value={fileFormat}
                onChange={setFileFormat}
                style={{ minWidth: "100px" }}
              ></Select>
            </Form.Item>
            <Form.Item label={intl.formatMessage({id: "acquisition.filePath"})}>
              <Input
                size={"small"}
                value={filePath}
                onChange={(e: ChangeEvent<HTMLInputElement>) => {
                  setFilePath(e.target.value);
                }}
              />
            </Form.Item>
            <Form.Item>
              {(acqStatus == 1 || acqStatus == -1) && (
                <Progress percent={100} showInfo={false} steps={1} size={20} strokeColor={['#87d068']}/>
              )}
              {(acqStatus == 2 || acqStatus == -2 || (acqStatus ==0 && acqRunProgress["total"] != -1)) && (
                <Progress strokeColor={conicColors} steps={5} size={"default"}
                  percent={acqRunProgress["total"] > 0 ? (acqRunProgress["finished"] / acqRunProgress["total"]) * 100 : 100}
                  status={"active"}
                  format={(p) => {
                    return acqRunProgress["finished"] + "/" + acqRunProgress["total"] + "(" + p?.toFixed(2) + " %)";
                  }}
                />)
              }
            </Form.Item>
          </Form>
        </Col>
      </Row>
    </div>
  );
};

export default AcquisitionPanel;
