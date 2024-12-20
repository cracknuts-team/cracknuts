import { createRender } from "@anywidget/react";
import React from "react";
import TracePanel from "@/TracePanel.tsx";

const render = createRender(() => {
  return (
    <div >
      <TracePanel></TracePanel>
    </div>
  );
});

export default { render };
