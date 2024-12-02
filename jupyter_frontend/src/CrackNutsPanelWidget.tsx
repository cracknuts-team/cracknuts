import {createRender} from "@anywidget/react";
import {TraceMonitorPanel} from "@/TracePanel.tsx";
import React, {useState} from "react";
import CrackerPanel from "@/CrackerPanel.tsx";
import {ConfigProvider, theme} from "antd";

const render = createRender(() => {
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
        <ConfigProvider theme={{algorithm: algorithm}}>
            <div style={{padding: 20, border: "1px solid #616161", backgroundColor: backgroundColor,}}>
                <CrackerPanel hasAcquisition={true} connectStatusChanged={(s) => {setConnected(s);}}/>
                <TraceMonitorPanel disable={!connected}></TraceMonitorPanel>
            </div>
        </ConfigProvider>
    );
});

export default {render};
