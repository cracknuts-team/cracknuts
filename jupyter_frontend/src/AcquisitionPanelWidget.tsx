import { createRender } from "@anywidget/react";
import React from "react";
import AcquisitionPanel from "./AcquisitionPanel";

const render = createRender(() => {
  return <AcquisitionPanel></AcquisitionPanel>;
});

export default { render };
