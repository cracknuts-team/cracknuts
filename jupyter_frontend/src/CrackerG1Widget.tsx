import {createRender, useModel, useModelState} from "@anywidget/react";
import React, {useEffect, useState} from "react";
import CrackerG1, {CrackerG1PanelProps} from "@/components/CrackerG1.tsx";
import {ConnectionProps} from "@/components/Connection.tsx"
import {G1ConfigProps} from "@/components/config/G1Config.tsx";
import {useConnectionStates} from "@/hooks/connection.ts";
import {useConfigCommonStates, useConfigGlitchTestStates, useGlitchStates, useOscConfigStates} from "@/hooks/config.ts";

import {ConfigProvider, theme,} from "antd";
import {IntlProvider} from "react-intl";
import zhCN from "antd/es/locale/zh_CN";
import zh from "@/i18n/zh.json";
import en from "@/i18n/en.json";
import enUS from "antd/es/locale/en_US";
import {bus} from "@/bus.ts";
import {ConfigurationProps} from "@/components/Configuration.tsx";
import useConfigurationStates from "@/hooks/configuration.ts";
import {ScopeProps} from "@/components/Scope.tsx";
import {useScopeStates} from "@/hooks/scope.ts";
import {AcquisitionProps} from "@/components/Acquisition.tsx";
import {useAcquisitionStates} from "@/hooks/acquisition.ts";

const render = createRender(() => {

    const model = useModel();

    const connectionProps: ConnectionProps = {...useConnectionStates(), disabled: false}; // disabled wait for acq status.
    const configurationProps: ConfigurationProps = useConfigurationStates()
    const acquisitionProps: AcquisitionProps = useAcquisitionStates()
    const configProps: G1ConfigProps = {
        common: useConfigCommonStates(),
        osc: useOscConfigStates(),
        glitch: useGlitchStates(),
        glitchTest: useConfigGlitchTestStates()
    };
    const scopeProps: ScopeProps = {...useScopeStates(), disable: false}; // todo disabled wait for cracker connection status.



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

    const isLightColor = (hexColor: string) => {
        if (hexColor.startsWith("#")) {
            hexColor = hexColor.slice(1);
        }

        if (hexColor.length === 3) {
            hexColor = hexColor
                .split("")
                .map((char) => char + char)
                .join("");
        }

        const r = parseInt(hexColor.slice(0, 2), 16);
        const g = parseInt(hexColor.slice(2, 4), 16);
        const b = parseInt(hexColor.slice(4, 6), 16);

        const brightness = 0.299 * r + 0.587 * g + 0.114 * b;

        return brightness > 128;
    }

    // in browser
    let jpTheme = document.body.getAttribute("data-jp-theme-name");

    if (jpTheme == null) {
        // in vscode
        jpTheme = document.body.getAttribute("data-vscode-theme-kind");
    }

    if (jpTheme == null) {
        // in pycharm
        jpTheme = document.documentElement.getAttribute("style");
        if (jpTheme != null && jpTheme.includes("--jb-background-color")) {
            const s = jpTheme.indexOf("--jb-background-color") + 22;
            const e = s + 7;
            const color = jpTheme.substring(s, e);
            if (!isLightColor(color)) {
                jpTheme = "dark";
            }
        }
    }

    let algorithm = theme.defaultAlgorithm;
    let panelTheme: CrackerG1PanelProps["theme"] = "light";

    if (jpTheme != undefined && jpTheme.toLowerCase().includes("dark")) {
        algorithm = theme.darkAlgorithm;
        panelTheme = "dark";
    }

    return (
        <IntlProvider locale={language} messages={messageMap[language]}>
            <ConfigProvider theme={{algorithm: algorithm}} locale={antLanguage}>
                <CrackerG1
                    connection={connectionProps}
                    configuration={configurationProps}
                    config={configProps}
                    acquisition={acquisitionProps}
                    scope={scopeProps}
                    theme={panelTheme}
                />
            </ConfigProvider>
        </IntlProvider>
    );
});

export default {render};
