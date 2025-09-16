import React from "react";
import {Tabs, TabsProps} from "antd";
import ConfigCommonPanel, {ConfigCommonPanelProps} from "@/cracker/ConfigCommonPanel.tsx";

interface G1ConfigPanelProps {
  common: ConfigCommonPanelProps;
}

const G1ConfigPanel: React.FC<G1ConfigPanelProps> = ({common}) => {

  const tabItems: TabsProps['items'] = [
    {
      key: '1',
      label: 'Common',
      children: <ConfigCommonPanel
        voltage={common.voltage}
        clock={common.clock}
        uart={common.uart}
        spi={common.spi}
        i2c={common.i2c}
      />
    }
  ];

  return (
    <Tabs items={tabItems}/>
  );
};

export default G1ConfigPanel;