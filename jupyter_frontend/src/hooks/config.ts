import {useModelState} from "@anywidget/react";
import {ConfigCommonProps} from "@/components/config/ConfigCommon.tsx";
import {ConfigGlitchTestProps, GlitchTestOnApplyParam} from "@/components/config/ConfigGlitchTest.tsx";
import {ConfigOSCProps} from "@/components/config/ConfigOSC.tsx";
import {ConfigGlitchProps} from "@/components/config/ConfigGlitch.tsx";

const useConfigCommonStates: () => ConfigCommonProps = () => {

    // Voltage 模块
    const [nutEnable, setNutEnable] = useModelState<boolean>("nut_enable");
    const [nutClockEnable, setNutClockEnable] = useModelState<boolean>("nut_clock_enable");
    const [nutVoltage, setNutVoltage] = useModelState<number>("nut_voltage");
    const [nutClock, setNutClock] = useModelState<number>("nut_clock");

    // UART 模块
    const [nutUartEnable, setNutUartEnable] = useModelState<boolean>("nut_uart_enable");
    const [nutUartBaudrate, setNutUartBaudrate] = useModelState<number>("nut_uart_baudrate");
    const [nutUartBytesize, setNutUartBytesize] = useModelState<number>("nut_uart_bytesize");
    const [nutUartParity, setNutUartParity] = useModelState<number>("nut_uart_parity");
    const [nutUartStopbits, setNutUartStopbits] = useModelState<number>("nut_uart_stopbits");

    // SPI 模块
    const [nutSpiEnable, setNutSpiEnable] = useModelState<boolean>("nut_spi_enable");
    const [nutSpiSpeed, setNutSpiSpeed] = useModelState<number>("nut_spi_speed");
    const [nutSpiCpol, setNutSpiCpol] = useModelState<number>("nut_spi_cpol");
    const [nutSpiCpha, setNutSpiCpha] = useModelState<number>("nut_spi_cpha");
    const [nutSpiCsnAuto, setNutSpiCsnAuto] = useModelState<boolean>("nut_spi_csn_auto");
    const [nutSpiCsnDelay, setNutSpiCsnDelay] = useModelState<boolean>("nut_spi_csn_delay");

    // I2C 模块
    const [nutI2cEnable, setNutI2cEnable] = useModelState<boolean>("nut_i2c_enable");
    const [nutI2cDevAddr, setNutI2cDevAddr] = useModelState<string>("nut_i2c_dev_addr");
    const [nutI2cSpeed, setNutI2cSpeed] = useModelState<number>("nut_i2c_speed");
    const [nutI2cStretchEnable, setNutI2cStretchEnable] = useModelState<boolean>("nut_i2c_stretch_enable");

    return {
        voltage: {
            enable: nutEnable,
            setEnable: setNutEnable,
            value: nutVoltage,
            setValue: setNutVoltage,
        },
        clock: {
            enable: nutClockEnable,
            setEnable: setNutClockEnable,
            value: nutClock,
            setValue: setNutClock,
        },
        uart: {
            enable: nutUartEnable,
            setEnable: setNutUartEnable,
            baudrate: nutUartBaudrate,
            setBaudrate: setNutUartBaudrate,
            bytesize: nutUartBytesize,
            setBytesize: setNutUartBytesize,
            parity: nutUartParity,
            setParity: setNutUartParity,
            stopbits: nutUartStopbits,
            setStopbits: setNutUartStopbits,
        },
        spi: {
            enable: nutSpiEnable,
            setEnable: setNutSpiEnable,
            speed: nutSpiSpeed,
            setSpeed: setNutSpiSpeed,
            cpol: nutSpiCpol,
            setCpol: setNutSpiCpol,
            cpha: nutSpiCpha,
            setCpha: setNutSpiCpha,
            csnAuto: nutSpiCsnAuto,
            setCsnAuto: setNutSpiCsnAuto,
            csnDelay: nutSpiCsnDelay,
            setCsnDelay: setNutSpiCsnDelay,
        },
        i2c: {
            enable: nutI2cEnable,
            setEnable: setNutI2cEnable,
            devAddr: nutI2cDevAddr,
            setDevAddr: setNutI2cDevAddr,
            speed: nutI2cSpeed,
            setSpeed: setNutI2cSpeed,
            stretch: nutI2cStretchEnable,
            setStretch: setNutI2cStretchEnable,
        },
    };
}

const useConfigGlitchTestStates: () => ConfigGlitchTestProps = () => {
    const [, setGlitchTestParams] = useModelState<GlitchTestOnApplyParam>("glitch_test_params");

    return {
        onApply: setGlitchTestParams
    }
};

const useOscConfigStates: () => ConfigOSCProps = () => {
    // Sample
    const [oscSampleClock, setOscSampleClock] = useModelState<number>("osc_sample_clock");
    const [oscSamplePhase, setOscSamplePhase] = useModelState<number>("osc_sample_phase");
    const [oscSampleLength, setOscSampleLength] = useModelState<number>("osc_sample_length");
    const [oscSampleDelay, setOscSampleDelay] = useModelState<number>("osc_sample_delay");

    // Channels
    const [channelAEnable, setChannelAEnable] = useModelState<boolean>("osc_channel_0_enable");
    const [channelBEnable, setChannelBEnable] = useModelState<boolean>("osc_channel_1_enable");
    const [channelAGain, setChannelAGain] = useModelState<number>("osc_channel_0_gain");
    const [channelBGain, setChannelBGain] = useModelState<number>("osc_channel_1_gain");

    // Trigger
    const [oscTriggerSource, setOscTriggerSource] = useModelState<number>("osc_trigger_source");
    const [oscTriggerMode, setOscTriggerMode] = useModelState<number>("osc_trigger_mode");
    const [oscTriggerEdge, setOscTriggerEdge] = useModelState<number>("osc_trigger_edge");
    const [oscTriggerEdgeLevel, setOscTriggerEdgeLevel] = useModelState<number>("osc_trigger_edge_level");

    return {
        sample: {
            rate: oscSampleClock,
            setRate: setOscSampleClock,
            phase: oscSamplePhase,
            setPhase: setOscSamplePhase,
            length: oscSampleLength,
            setLength: setOscSampleLength,
            delay: oscSampleDelay,
            setDelay: setOscSampleDelay,
            channelA: {
                enable: channelAEnable,
                setEnable: setChannelAEnable,
                gain: channelAGain,
                setGain: setChannelAGain,
            },
            channelB: {
                enable: channelBEnable,
                setEnable: setChannelBEnable,
                gain: channelBGain,
                setGain: setChannelBGain,
            },
        },
        trigger: {
            source: oscTriggerSource,
            setSource: setOscTriggerSource,
            mode: oscTriggerMode,
            setMode: setOscTriggerMode,
            edge: oscTriggerEdge,
            setEdge: setOscTriggerEdge,
            edgeLevel: oscTriggerEdgeLevel,
            setEdgeLevel: setOscTriggerEdgeLevel,
        },
    };
}


const useGlitchStates: () => ConfigGlitchProps = () => {
    const [glitchVCCNormalVoltage, setGlitchVCCNormalVoltage] = useModelState<number>("glitch_vcc_normal_voltage");
    const [glitchVCCWait, setGlitchVCCWait] = useModelState<number>("glitch_vcc_wait");
    const [glitchVCCGlitchVoltage, setGlitchVCCGlitchVoltage] = useModelState<number>("glitch_vcc_glitch_voltage");
    const [glitchVCCCount, setGlitchVCCCount] = useModelState<number>("glitch_vcc_count");
    const [glitchVCCRepeat, setGlitchVCCRepeat] = useModelState<number>("glitch_vcc_repeat");
    const [glitchVCCDelay, setGlitchVCCDelay] = useModelState<number>("glitch_vcc_delay");

    const [glitchGNDNormalVoltage, setGlitchGNDNormalVoltage] = useModelState<number>("glitch_gnd_normal_voltage");
    const [glitchGNDWait, setGlitchGNDWait] = useModelState<number>("glitch_gnd_wait");
    const [glitchGNDGlitchVoltage, setGlitchGNDGlitchVoltage] = useModelState<number>("glitch_gnd_glitch_voltage");
    const [glitchGNDCount, setGlitchGNDCount] = useModelState<number>("glitch_gnd_count");
    const [glitchGNDRepeat, setGlitchGNDRepeat] = useModelState<number>("glitch_gnd_repeat");
    const [glitchGNDDelay, setGlitchGNDDelay] = useModelState<number>("glitch_gnd_delay");

    return {
        vcc: {
            normalVoltage: glitchVCCNormalVoltage,
            setNormalVoltage: setGlitchVCCNormalVoltage,

            wait: glitchVCCWait,
            setWait: setGlitchVCCWait,

            glitchVoltage: glitchVCCGlitchVoltage,
            setGlitchVoltage: setGlitchVCCGlitchVoltage,

            count: glitchVCCCount,
            setCount: setGlitchVCCCount,

            repeat: glitchVCCRepeat,
            setRepeat: setGlitchVCCRepeat,

            delay: glitchVCCDelay,
            setDelay: setGlitchVCCDelay,
        },
        gnd: {
            normalVoltage: glitchGNDNormalVoltage,
            setNormalVoltage: setGlitchGNDNormalVoltage,

            wait: glitchGNDWait,
            setWait: setGlitchGNDWait,

            glitchVoltage: glitchGNDGlitchVoltage,
            setGlitchVoltage: setGlitchGNDGlitchVoltage,

            count: glitchGNDCount,
            setCount: setGlitchGNDCount,

            repeat: glitchGNDRepeat,
            setRepeat: setGlitchGNDRepeat,

            delay: glitchGNDDelay,
            setDelay: setGlitchGNDDelay,
        }
    };
};


export {useConfigCommonStates, useOscConfigStates, useGlitchStates, useConfigGlitchTestStates,};