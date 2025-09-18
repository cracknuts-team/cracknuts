import React from "react";
import {Tabs, TabsProps} from "antd";
import ConfigCommon, {ConfigCommonProps} from "@/components/config/ConfigCommon.tsx";
import ConfigGlitchTest, {ConfigGlitchTestProps} from "@/components/config/ConfigGlitchTest.tsx";
import ConfigOSC, {ConfigOSCProps} from "@/components/config/ConfigOSC.tsx";
import ConfigGlitch, {ConfigGlitchProps} from "@/components/config/ConfigGlitch.tsx";

interface G1ConfigProps {
    common: ConfigCommonProps;
    osc: ConfigOSCProps
    glitch: ConfigGlitchProps
    glitchTest: ConfigGlitchTestProps
}

const G1Config: React.FC<G1ConfigProps> = ({common, osc, glitch, glitchTest}) => {

    const tabItems: TabsProps['items'] = [{
        key: 'Common',
        label: 'Common',
        children: <ConfigCommon
            voltage={common.voltage}
            clock={common.clock}
            uart={common.uart}
            spi={common.spi}
            i2c={common.i2c}
        />
    }, {
        key: 'OSC',
        label: 'OSC',
        children: <ConfigOSC
            sample={osc.sample}
            trigger={osc.trigger}
        />
    }, {
        key: 'Glitch',
        label: 'Glitch',
        children: <ConfigGlitch
            vcc={glitch.vcc}
            gnd={glitch.gnd}
            clock={glitch.clock}
        />
    }, {
        key: 'GlitchTest',
        label: 'Glitch Test',
        children: <ConfigGlitchTest
            onApply={glitchTest.onApply}
        />
    }];

    return (
        <Tabs items={tabItems}/>
    );
};

export default G1Config;
export type {G1ConfigProps};