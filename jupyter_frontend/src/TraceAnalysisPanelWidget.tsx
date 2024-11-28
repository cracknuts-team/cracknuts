import { createRender } from "@anywidget/react";
import React from "react";
import {TraceAnalysisPanel} from "@/TracePanel.tsx";

const render = createRender(() => {
  return (
    <div >
      <TraceAnalysisPanel></TraceAnalysisPanel>
    </div>
  );
});

export default { render };
