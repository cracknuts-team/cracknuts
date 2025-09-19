import {useModelState} from "@anywidget/react";
import {AcqRunProgress, AcquisitionProps} from "@/components/Acquisition.tsx";

const useAcquisitionStates: () => AcquisitionProps = () => {
    const [acqStatus] = useModelState<number>("acq_status"); // 0 停止 1 测试 2 运行
    const [acqRunProgress] = useModelState<AcqRunProgress>("acq_run_progress"); //{'finished': 1, total: 1000}
    const [traceCount, setTraceCount] = useModelState<number>("trace_count");
    const [triggerJudgeWaitTime, setTriggerJudgeWaitTime] = useModelState<number>("trigger_judge_wait_time");
    const [triggerJudgeTimeout, setTriggerJudgeTimeout] = useModelState<number>("trigger_judge_timeout");
    const [doErrorCountMax, setDoErrorCountMax] = useModelState<number>("do_error_max_count");
    const [fileFormat, setFileFormat] = useModelState<string>("file_format");
    const [filePath, setFilePath] = useModelState<string>("file_path");
    const [traceFetchInterval, setTraceFetchInterval] = useModelState<string>("trace_fetch_interval");

    return {
        status: acqStatus,
        runProgress: acqRunProgress,
        traceCount: traceCount,
        setTraceCount: setTraceCount,
        triggerJudgeWaitTime: triggerJudgeWaitTime,
        setTriggerJudgeWaitTime: setTriggerJudgeWaitTime,
        triggerJudgeTimeout: triggerJudgeTimeout,
        setTriggerJudgeTimeout: setTriggerJudgeTimeout,
        doErrorCountMax: doErrorCountMax,
        setErrorCountMax: setDoErrorCountMax,
        fileFormat: fileFormat,
        setFileFormat: setFileFormat,
        filePath: filePath,
        setFilePath: setFilePath,
        traceFetchInterval: traceFetchInterval,
        setTraceFetchInterval: setTraceFetchInterval
    };
}

export {useAcquisitionStates};