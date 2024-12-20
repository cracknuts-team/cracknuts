import { createRender } from "@anywidget/react";
import React from "react";
import ScopePanel from "@/ScopePanel.tsx";

const render = createRender(() => {
  return (
    <div style={{ padding: 10, border: "1px solid #e5e5e5" }}>
      <ScopePanel></ScopePanel>
    </div>
  );
});

export default { render };
