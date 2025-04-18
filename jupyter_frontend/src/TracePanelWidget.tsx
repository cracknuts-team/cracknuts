import {createRender, useModelState} from "@anywidget/react";
import React from "react";
import TracePanel from "@/TracePanel.tsx";
import zh from "@/i18n/zh.json";
import en from "@/i18n/en.json";
import {IntlProvider} from "react-intl";

const render = createRender(() => {
  const [language] = useModelState<string>("language");
  const messageMap: Record<string, Record<string, string>> = {
      'zh': zh,
      'en': en
  };
  return (
    <IntlProvider locale={language} messages={messageMap[language]}>
      <TracePanel></TracePanel>
    </IntlProvider>
  );
});

export default { render };
