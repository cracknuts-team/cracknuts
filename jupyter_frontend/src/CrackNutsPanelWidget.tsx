import { createRender } from "@anywidget/react";
import { TraceMonitorPanel } from "@/TracePanel.tsx";
import React, { useState } from "react";
import CrackerPanel from "@/CrackerPanel.tsx";

const render = createRender(() => {
  const [connected, setConnected] = useState(false);

  return (
    <div style={{ padding: 20, border: "1px solid #e5e5e5", borderRadius: 15 }}>
      <CrackerPanel hasAcquisition={true} connectStatusChanged={(s) => {setConnected(s)}}></CrackerPanel>
      <TraceMonitorPanel disable={!connected}></TraceMonitorPanel>
    </div>
  );
});

export default { render };
