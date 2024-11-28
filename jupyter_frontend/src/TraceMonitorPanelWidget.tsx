import { createRender } from "@anywidget/react";
import React from "react";
import {TraceMonitorPanel} from "@/TracePanel.tsx";

const render = createRender(() => {
  return (
    <div style={{ padding: 10, border: "1px solid #e5e5e5" }}>
      <TraceMonitorPanel></TraceMonitorPanel>
    </div>
  );
});

export default { render };
