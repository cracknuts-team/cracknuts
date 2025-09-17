import {createRender, useModelState} from "@anywidget/react";
import React, {useEffect, useState} from "react";
import CrackerG1 from "@/cracker/CrackerG1.tsx";
import {ConnectionProps} from "@/cracker/Connection.tsx"
import {G1ConfigProps} from "@/cracker/config/G1Config.tsx";
import {useConnectionStates} from "@/hooks/connection.ts";
import {useConfigCommonStates, useConfigGlitchTestStates} from "@/hooks/config.ts";

import {ConfigProvider, theme,} from "antd";
import {IntlProvider} from "react-intl";
import zhCN from "antd/es/locale/zh_CN";
import zh from "@/i18n/zh.json";
import en from "@/i18n/en.json";
import enUS from "antd/es/locale/en_US";

const render = createRender(() => {

  const connectionProps: ConnectionProps = {...useConnectionStates(), disabled: false}; // disabled wait for acq status.

  const configProps: G1ConfigProps = {
    common: useConfigCommonStates(),
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

  useEffect(() => {
    setLanguage('zh')
  }, []);

  const algorithm = theme.defaultAlgorithm;

  return (
    <IntlProvider locale={language} messages={messageMap[language]}>
      <ConfigProvider theme={{algorithm: algorithm}} locale={antLanguage}>
        <CrackerG1
          connection={connectionProps}
          config={configProps}
        />
      </ConfigProvider>
    </IntlProvider>
  );
});

export default {render};
