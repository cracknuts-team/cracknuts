import {createRender, useModelState} from "@anywidget/react";
import ScopePanel from "@/ScopePanel.tsx";
import React, {useState} from "react";
import CrackerS1Panel from "@/CrackerS1Panel.tsx";
import {ConfigProvider, theme} from "antd";
import zhCN from 'antd/es/locale/zh_CN';
import enUS from 'antd/es/locale/en_US';
import zh from '@/i18n/zh.json'
import en from '@/i18n/en.json'
import { IntlProvider } from "react-intl";

const render = createRender(() => {

    const [crackerModel] = useModelState<string>("cracker_model");

    const [language, _setLanguage] = useModelState<string>("language");
    const [antLanguage, setAntLanguage] = useState(zhCN);
    const messageMap: Record<string, any> = {
        'zh': zh,
        'en': en
    };

    const setLanguage = (language: string)=> {
        if (language == 'zh') {
            setAntLanguage(zhCN)
        } else if (language == 'en') {
            setAntLanguage(enUS);
        }
        _setLanguage(language);
    };

    const [connected, setConnected] = useState(false);

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
    let backgroundColor = "#ffffff";

    if (jpTheme != undefined && jpTheme.toLowerCase().includes("dark")) {
        algorithm = theme.darkAlgorithm;
        backgroundColor = "#000000";
    }

    function isLightColor(hexColor: string) {
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

    return (
        <IntlProvider locale={language} messages={messageMap[language]}>
            <ConfigProvider theme={{algorithm: algorithm}} locale={antLanguage}>
                <div style={{
                    padding: 20,
                    border: "1px solid #616161",
                    backgroundColor: backgroundColor,
                    marginTop: 8,
                    marginBottom: 8
                }}>
                    {crackerModel == "s1" && (<CrackerS1Panel hasAcquisition={true} connectStatusChanged={(s) => {
                        setConnected(s);
                    }} languageChanged={setLanguage}/>)}
                    {/*{crackerModel == "g1" && (<CrackerG1Panel hasAcquisition={true} connectStatusChanged={(s) => {setConnected(s);}}/>)}*/}
                    <ScopePanel disable={!connected}></ScopePanel>
                </div>
            </ConfigProvider>
        </IntlProvider>
    );
});

export default {render};
