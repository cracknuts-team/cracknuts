import {createRender, useModel, useModelState} from "@anywidget/react";
import React, {useEffect, useState} from "react";
import CrackerG1 from "@/components/CrackerG1.tsx";
import {ConnectionProps} from "@/components/Connection.tsx"
import {G1ConfigProps} from "@/components/config/G1Config.tsx";
import {useConnectionStates} from "@/hooks/connection.ts";
import {useConfigCommonStates, useOscConfigStates, useConfigGlitchTestStates, useGlitchStates} from "@/hooks/config.ts";

import {ConfigProvider, theme,} from "antd";
import {IntlProvider} from "react-intl";
import zhCN from "antd/es/locale/zh_CN";
import zh from "@/i18n/zh.json";
import en from "@/i18n/en.json";
import enUS from "antd/es/locale/en_US";
import {bus} from "@/bus.ts";
import {ConfigurationProps} from "@/components/Configuration.tsx";
import useConfigurationStates from "@/hooks/configuration.ts";

const render = createRender(() => {

    const model = useModel();

    const connectionProps: ConnectionProps = {...useConnectionStates(), disabled: false}; // disabled wait for acq status.
    const configurationProps: ConfigurationProps = useConfigurationStates()
    const configProps: G1ConfigProps = {
        common: useConfigCommonStates(),
        osc: useOscConfigStates(),
        glitch: useGlitchStates(),
        glitchTest: useConfigGlitchTestStates()
    };

    const [language, _setLanguage] = useModelState<string>("language");
    const [antLanguage, setAntLanguage] = useState(zhCN);
    const messageMap: Record<string, any> = {
        'zh': zh,
        'en': en
    };
    const setLanguage = (language: string) => {
        if (language == 'zh') {
            setAntLanguage(zhCN)
        } else if (language == 'en') {
            setAntLanguage(enUS);
        }
        _setLanguage(language);
    };

    const customCallback = (msg: { [x: string]: any; }, _: any) => {
        if ("dumpConfigCompleted" in msg) {
            bus.emit("dumpConfigCompleted", msg["dumpConfigCompleted"]);
        }
    };

    useEffect(() => {

        model.on("msg:custom", customCallback);
        bus.on("changeLanguage", _setLanguage);

        return () => {
            model.off("msg:custom", customCallback);
            bus.off("changeLanguage", setLanguage);
        };
    }, []);

    useEffect(() => {
        setLanguage(language);
    }, [language]);

    const algorithm = theme.defaultAlgorithm;

    return (
        <IntlProvider locale={language} messages={messageMap[language]}>
            <ConfigProvider theme={{algorithm: algorithm}} locale={antLanguage}>
                <CrackerG1
                    connection={connectionProps}
                    configuration={configurationProps}
                    config={configProps}
                />
            </ConfigProvider>
        </IntlProvider>
    );
});

export default {render};
