import {useModel, useModelState} from "@anywidget/react";
import {ConfigurationProps} from "@/components/Configuration.tsx";

const useConfigurationStates: () => ConfigurationProps = () => {

    const model = useModel();

    const [panelConfigDifferentFromCrackerConfig] = useModelState<boolean>("panel_config_different_from_cracker_config");

    const dumpConfig = () => {
        model.send({source: "dumpConfigButton", event: "onClick", args: {}});
    };

    const loadConfig = (config: string) => {
        model.send({source: "loadConfigButton", event: "onClick", args: config});
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

    return {
        readConfig: readConfig,
        writeConfig: writeConfig,
        dumpConfig: dumpConfig,
        saveConfig: saveConfig,
        loadConfig: loadConfig,
        panelConfigDifferentFromCrackerConfig: panelConfigDifferentFromCrackerConfig,
    };
}

export default useConfigurationStates;