import {useModelState} from "@anywidget/react";
import {ScopeProps, RangeData, SeriesData} from "@/components/Scope.tsx";

const useScopeStates: () => Omit<ScopeProps, 'disable'> = () => {
    const [scopeStatus, setScopeStatus] = useModelState<number>("scope_status");
    const [lockScopeOperation] = useModelState<boolean>("lock_scope_operation");
    const [monitorStatus, setMonitorStatus] = useModelState<boolean>("monitor_status");
    const [monitorPeriod, setMonitorPeriod] = useModelState<number>("monitor_period")

    const [yRange] = useModelState<RangeData>("y_range");
    const [seriesData] = useModelState<SeriesData>("series_data");

    return {
        scopeStatus: scopeStatus,
        setScopeStatus: setScopeStatus,
        monitorStatus: monitorStatus,
        setMonitorStatus: setMonitorStatus,
        monitorPeriod: monitorPeriod,
        setMonitorPeriod: setMonitorPeriod,
        disableOperate: lockScopeOperation,
        yRange: yRange,
        seriesData: seriesData
    }
};

export {useScopeStates};