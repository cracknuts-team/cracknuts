import { createRender } from "@anywidget/react";
import React from "react";
import CrackerPanel from "@/CrackerPanel.tsx";

const render = createRender(() => {
  return <CrackerPanel></CrackerPanel>;
});

export default { render };
