import React from "react";
import {Tabs, TabsProps} from "antd";
import ConfigCommon, {ConfigCommonProps} from "@/cracker/config/ConfigCommon.tsx";
import ConfigGlitchTest, {ConfigGlitchTestProps} from "@/cracker/config/ConfigGlitchTest.tsx";

interface G1ConfigProps {
  common: ConfigCommonProps;
  glitchTest: ConfigGlitchTestProps
}

const G1Config: React.FC<G1ConfigProps> = ({common, glitchTest}) => {

  const tabItems: TabsProps['items'] = [
    {
      key: '1',
      label: 'Common',
      children: <ConfigCommon
        voltage={common.voltage}
        clock={common.clock}
        uart={common.uart}
        spi={common.spi}
        i2c={common.i2c}
      />
    }, {
    key: '2',
      label: 'Glitch Test',
      children: <ConfigGlitchTest
        onApply={glitchTest.onApply}
      />
    }
  ];

  return (
    <Tabs items={tabItems}/>
  );
};

export default G1Config;
export type {G1ConfigProps};