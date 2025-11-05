import {createRender, useModelState} from "@anywidget/react";
import React from "react";
import GlitchTestPanel, {GlitchTestPanelOnApplyParam} from "@/GlitchTestPanel.tsx";

const render = createRender(() => {

  const [, setVccGlitchParamGenerator] = useModelState("tl_vcc_glitch_param_generator");

  const onApply = (onApplyParam: GlitchTestPanelOnApplyParam) => {
    console.log(onApplyParam);
    if (onApplyParam.type === 'vcc') {
      setVccGlitchParamGenerator(Object.fromEntries(
        onApplyParam.data.map(item => [item.prop, item.param])
      ));
    } else {
      // gnd clock
    }
  };

  return (
      <GlitchTestPanel onApply={onApply}></GlitchTestPanel>
  );
});

export default {render};
