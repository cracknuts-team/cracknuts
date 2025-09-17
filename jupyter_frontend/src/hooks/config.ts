import {useModelState} from "@anywidget/react";
import {ConfigCommonProps} from "@/cracker/config/ConfigCommon.tsx";
import {ConfigGlitchTestProps} from "@/cracker/config/ConfigGlitchTest.tsx";
import {GlitchTestPanelOnApplyParam} from "@/GlitchTestPanel.tsx";
import {ConfigOSCProps} from "@/cracker/config/ConfigOSC.tsx";

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
  const [,setGlitchTestParams] = useModelState<GlitchTestPanelOnApplyParam>("glitch_test_params");

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



export {useConfigCommonStates, useConfigGlitchTestStates, useOscConfigStates};