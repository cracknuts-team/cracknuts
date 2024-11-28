import { useModel, useModelState } from "@anywidget/react";
import { Col, Form, Input, InputNumber, Progress, Radio, Row, Select } from "antd";
import { CheckboxChangeEvent } from "antd/es/checkbox";
import React, { ChangeEvent } from "react";

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

  const model = useModel();

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

    return () => model.off(`change:acq_status`, callback);
  }, [model]);

  const [frontStatus, setFrontStatus] = React.useState<number>(0);

  function checkFrontBackStatusSync() {
    return (frontStatus > 0 && frontStatus != acqStatus) || (frontStatus < 0 && acqStatus > 0);
  }

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
                  测试
                </Radio.Button>
                <Radio.Button value={2} disabled={acqStatus == 1 || acqStatus == -1 || checkFrontBackStatusSync()}>
                  运行
                </Radio.Button>
                <Radio.Button value={-1} disabled={acqStatus == 0 || checkFrontBackStatusSync()}>
                  暂停
                </Radio.Button>
                <Radio.Button value={0} disabled={checkFrontBackStatusSync()}>
                  停止
                </Radio.Button>
              </Radio.Group>
            </Form.Item>
            <Form.Item label="采样轮数">
              <InputNumber
                size={"small"}
                value={traceCount}
                onChange={(v) => {
                  setTraceCount(Number(v));
                }}
                changeOnWheel
              />
            </Form.Item>
            {/*<Form.Item label="采样长度">*/}
            {/*  <InputNumber*/}
            {/*    size={"small"}*/}
            {/*    value={sampleLength}*/}
            {/*    onChange={(v) => {*/}
            {/*      setSampleLength(Number(v));*/}
            {/*    }}*/}
            {/*    changeOnWheel*/}
            {/*  />*/}
            {/*</Form.Item>*/}
            {/*<Form.Item label="采样偏移">*/}
            {/*  <InputNumber*/}
            {/*    size={"small"}*/}
            {/*    value={sampleOffset}*/}
            {/*    onChange={(v) => {*/}
            {/*      setSampleOffset(Number(v));*/}
            {/*    }}*/}
            {/*    changeOnWheel*/}
            {/*  />*/}
            {/*</Form.Item>*/}
            <Form.Item label="触发判断等待时长">
              <InputNumber
                size={"small"}
                value={triggerJudgeWaitTime}
                suffix={"秒"}
                min={0.05}
                step={0.01}
                onChange={(v) => {
                  setTriggerJudgeWaitTime(Number(v));
                }}
                changeOnWheel
              />
            </Form.Item>
            <Form.Item label="触发判断超时">
              <InputNumber
                size={"small"}
                value={triggerJudgeTimeout}
                suffix={"秒"}
                min={0.05}
                step={0.01}
                onChange={(v) => {
                  setTriggerJudgeTimeout(Number(v));
                }}
                changeOnWheel
              />
            </Form.Item>
            <Form.Item label="do异常最大次数">
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
            <Form.Item label="保存格式">
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
            <Form.Item label="保存路径">
              <Input
                size={"small"}
                value={filePath}
                onChange={(e: ChangeEvent<HTMLInputElement>) => {
                  setFilePath(e.target.value);
                }}
              />
            </Form.Item>
          </Form>
        </Col>
      </Row>
      <Row>
        <Col span={24}>
          {acqStatus != 0 && (
            <Progress
              percent={acqRunProgress["total"] > 0 ? (acqRunProgress["finished"] / acqRunProgress["total"]) * 100 : 100}
              status="active"
              format={(p) => {
                return acqRunProgress["finished"] + "/" + acqRunProgress["total"] + "(" + p?.toFixed(2) + " %)";
              }}
              showInfo={acqStatus == 2 || acqStatus == -2}
            />
          )}
        </Col>
      </Row>
    </div>
  );
};

export default AcquisitionPanel;
