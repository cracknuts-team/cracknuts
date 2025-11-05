import React from "react";
import {Tabs, TabsProps} from "antd";
import ConfigCommon from "@/components/config/ConfigCommon.tsx";
import ConfigGlitchTest from "@/components/config/ConfigGlitchTest.tsx";
import ConfigOSC from "@/components/config/ConfigOSC.tsx";
import ConfigGlitch from "@/components/config/ConfigGlitch.tsx";


interface G1ConfigInternalProps {
    isGlitchTestShow: (show: boolean) => void;
}

const G1Config: React.FC<G1ConfigInternalProps> = ({isGlitchTestShow}) => {

    const tabItems: TabsProps['items'] = [{
        key: 'Common',
        label: 'Common',
        children: <ConfigCommon/>
    }, {
        key: 'OSC',
        label: 'OSC',
        children: <ConfigOSC/>
    }, {
        key: 'Glitch',
        label: 'Glitch',
        children: <ConfigGlitch/>
    }, {
        key: 'GlitchTest',
        label: 'Glitch Test',
        children: <ConfigGlitchTest/>
    }];

    return (
        <Tabs
            items={tabItems}
            onChange={(key) => {
                // isGlitchTestShow(key === 'GlitchTest');
                isGlitchTestShow(key === 'GlitchTest')
            }}
        />
    );
};

export default G1Config;