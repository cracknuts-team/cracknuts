import React, {ChangeEvent} from "react";
import {Form, Input, InputNumber, Progress, Radio, Select} from "antd";
import {CheckboxChangeEvent} from "antd/es/checkbox";
import {FormattedMessage, useIntl} from "react-intl";
import {useModel} from "@anywidget/react";

interface AcqRunProgress {
    finished: number;
    total: number;
}

interface AcquisitionProps {
    status: number,
    runProgress: AcqRunProgress,
    traceCount: number,
    setTraceCount: (count: number) => void,
    triggerJudgeWaitTime: number,
    setTriggerJudgeWaitTime: (time: number) => void,
    triggerJudgeTimeout: number,
    setTriggerJudgeTimeout: (timeout: number) => void,
    doErrorCountMax: number,
    setErrorCountMax: (max: number) => void,
    fileFormat: string,
    setFileFormat: (format: string) => void,
    filePath: string,
    setFilePath: (path: string) => void,
    traceFetchInterval: string
    setTraceFetchInterval: (interval: string) => void
}

const Acquisition: React.FC<AcquisitionProps> = ({
                                                     status,
                                                     runProgress,
                                                     traceCount,
                                                     setTraceCount,
                                                     triggerJudgeWaitTime,
                                                     setTriggerJudgeWaitTime,
                                                     triggerJudgeTimeout,
                                                     setTriggerJudgeTimeout,
                                                     doErrorCountMax,
                                                     setErrorCountMax,
                                                     fileFormat,
                                                     setFileFormat,
                                                     filePath,
                                                     setFilePath,
                                                     traceFetchInterval,
                                                     setTraceFetchInterval
                                                 }) => {

    const model = useModel();

    const intl = useIntl();

    const run = (status: number) => {
        if (status == -1) {
            model.send({source: "acqStatusButton", event: "onChange", args: {status: "pause"}});
        } else if (status == 1) {
            model.send({source: "acqStatusButton", event: "onChange", args: {status: "test"}});
        } else if (status == 2) {
            model.send({source: "acqStatusButton", event: "onChange", args: {status: "run"}});
            // } else if (status == 3) {
            //   model.send({source: "acqStatusButton", event: "onChange", args: {status: "glitch_test"}});
        } else {
            // stop
            model.send({source: "acqStatusButton", event: "onChange", args: {status: "stop"}});
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

    const checkFrontBackStatusSync = () => {
        return (frontStatus > 0 && frontStatus != status) || (frontStatus < 0 && status > 0);
    }

    const conicColors = [
        '#0066ff',
        '#0099cc',
        '#00cccc',
        '#00ff99',
        '#00ff00',
    ]

    return (
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
                    <Radio.Button value={1}
                                  disabled={status == 2 || status == -2 || status == -3 || checkFrontBackStatusSync()}>
                        <FormattedMessage id={"acquisition.test"}/>
                    </Radio.Button>
                    <Radio.Button value={2} disabled={status == 1 || status == -1 || checkFrontBackStatusSync()}>
                        <FormattedMessage id={"acquisition.run"}/>
                    </Radio.Button>
                    {/*<Radio.Button value={3} disabled={acqStatus == 1 || acqStatus == -1 || checkFrontBackStatusSync()}>*/}
                    {/*  Glitch Test*/}
                    {/*</Radio.Button>*/}
                    <Radio.Button value={-1} disabled={status == 0 || checkFrontBackStatusSync()}>
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
                        setErrorCountMax(Number(v));
                    }}
                    changeOnWheel
                />
            </Form.Item>
            <Form.Item label={intl.formatMessage({id: "acquisition.fileFormat"})}>
                <Select
                    size={"small"}
                    options={[
                        {value: "zarr", label: "Zarr"},
                        {value: "numpy", label: "Numpy"},
                    ]}
                    value={fileFormat}
                    onChange={setFileFormat}
                    style={{minWidth: "100px"}}
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
                {(status == 1 || status == -1) && (
                    <Progress percent={100} showInfo={false} steps={1} size={20} strokeColor={['#87d068']}/>
                )}
                {(status == 2 || status == -2 || status == 3 || status == -3 || (status == 0 && runProgress["total"] != -1)) && (
                    <Progress strokeColor={conicColors} steps={5} size={"default"}
                              percent={runProgress["total"] > 0 ? (runProgress["finished"] / runProgress["total"]) * 100 : 100}
                              status={"active"}
                              format={(p) => {
                                  return runProgress["finished"] + "/" + runProgress["total"] + "(" + p?.toFixed(2) + " %)";
                              }}
                    />)
                }
            </Form.Item>
        </Form>
    );
};

export default Acquisition;
export type {AcquisitionProps, AcqRunProgress};