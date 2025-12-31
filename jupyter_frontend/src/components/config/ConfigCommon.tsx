import {Button, Checkbox, Col, Form, Input, InputNumber, Row, Select, Space, Tooltip} from "antd";
import {FormattedMessage, useIntl} from "react-intl";
import React, {ChangeEvent} from "react";
import {useModelState} from "@anywidget/react";


const [NUT_VOLTAGE_MIN, NUT_VOLTAGE_MAX] = [-10, 10]

const ConfigCommon: React.FC = () => {

    const intl = useIntl();

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

    const voltage = {
        enable: nutEnable,
        setEnable: setNutEnable,
        value: nutVoltage,
        setValue: setNutVoltage,
    }
    const clock = {
        enable: nutClockEnable,
        setEnable: setNutClockEnable,
        value: nutClock,
        setValue: setNutClock,
    }
    const uart = {
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
    }
    const spi = {
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
    }
    const i2c = {
        enable: nutI2cEnable,
        setEnable: setNutI2cEnable,
        devAddr: nutI2cDevAddr,
        setDevAddr: setNutI2cDevAddr,
        speed: nutI2cSpeed,
        setSpeed: setNutI2cSpeed,
        stretch: nutI2cStretchEnable,
        setStretch: setNutI2cStretchEnable,
    }

    return (
        <Row>
            <Col span={24}>
                <Form layout={"inline"}>
                    <Form.Item>
                        <Checkbox
                            checked={voltage.enable}
                            onChange={() => {
                                voltage.setEnable(!voltage.enable);
                            }}
                        >
                            <FormattedMessage id={"cracker.config.nut.power"}/>
                        </Checkbox>
                        <InputNumber style={{width: 90}}
                                     disabled={!voltage.enable}
                                     addonAfter="V"
                                     step="0.1"
                                     stringMode
                                     size={"small"}
                                     min={NUT_VOLTAGE_MIN}
                                     max={NUT_VOLTAGE_MAX}
                                     value={voltage.value}
                                     parser={(v) => {
                                         return Number(v);
                                     }}
                                     onChange={(v) => {
                                         voltage.setValue(Number(v));
                                     }}
                                     changeOnWheel
                        />
                    </Form.Item>
                    <Form.Item>
                        <Checkbox checked={clock.enable} onChange={() => {
                            clock.setEnable(!clock.enable)
                        }}>
                            <FormattedMessage id={"cracker.config.nut.clock"}/>
                        </Checkbox>
                        <Space.Compact>
                            <Select
                                disabled={!clock.enable}
                                size={"small"}
                                options={[
                                    {value: 80000, label: "80 M"},
                                    {value: 40000, label: "40 M"},
                                    {value: 20000, label: "20 M"},
                                    {value: 16000, label: "16 M"},
                                    {value: 12000, label: "12 M"},
                                    {value: 10000, label: "10 M"},
                                    {value: 8000, label: "8  M"},
                                    {value: 4000, label: "4  M"},
                                ]}
                                value={clock.value}
                                onChange={clock.setValue}
                                style={{width: 80}}
                            ></Select>
                            <Button style={{pointerEvents: "none", opacity: 1, cursor: "default"}}
                                    size={"small"}>Hz</Button>
                        </Space.Compact>
                    </Form.Item>
                    <Form.Item style={{marginRight: 1}}>
                        <Checkbox id={"cracker_config_uart_enable"} checked={uart.enable} onChange={() => {
                            uart.setEnable(!uart.enable);
                        }}><FormattedMessage id={"cracker.config.nut.uart.enable"}/></Checkbox>
                    </Form.Item>
                    <Form.Item label={intl.formatMessage({id: "cracker.config.nut.uart.baudrate"})}>
                        <Space.Compact>
                            <Select id={"cracker_config_uart_baudrate"} size={"small"} style={{minWidth: 90}}
                                    disabled={!uart.enable} value={uart.baudrate}
                                    onChange={uart.setBaudrate} options={[
                                {value: 0, label: "9600"},
                                {value: 1, label: "19200"},
                                {value: 2, label: "38400"},
                                {value: 3, label: "57600"},
                                {value: 4, label: "115200"},
                                {value: 5, label: "1000000"},
                            ]}/>
                        </Space.Compact>
                    </Form.Item>
                    <Form.Item label={intl.formatMessage({id: "cracker.config.nut.uart.bytesize"})}>
                        <Space.Compact>
                            <Select id={"cracker_config_uart_bytesize"} size={"small"} style={{minWidth: 90}}
                                    disabled={!uart.enable}
                                    value={uart.bytesize} onChange={uart.setBytesize} options={[
                                {value: 5, label: "5"},
                                {value: 6, label: "6"},
                                {value: 7, label: "7"},
                                {value: 8, label: "8"},
                            ]}/>
                        </Space.Compact>
                    </Form.Item>
                    <Form.Item label={intl.formatMessage({id: "cracker.config.nut.uart.parity"})}>
                        <Space.Compact>
                            <Select id={"cracker_config_uart_parity"} size={"small"} style={{minWidth: 90}}
                                    disabled={!uart.enable}
                                    value={uart.parity} onChange={uart.setParity} options={[
                                {value: 0, label: intl.formatMessage({id: "cracker.config.nut.uart.parity.none"})},
                                {value: 1, label: intl.formatMessage({id: "cracker.config.nut.uart.parity.even"})},
                                {value: 2, label: intl.formatMessage({id: "cracker.config.nut.uart.parity.odd"})},
                                {value: 3, label: intl.formatMessage({id: "cracker.config.nut.uart.parity.mark"})},
                                {value: 4, label: intl.formatMessage({id: "cracker.config.nut.uart.parity.space"})},
                            ]}/>
                        </Space.Compact>
                    </Form.Item>
                    <Form.Item label={intl.formatMessage({id: "cracker.config.nut.uart.stopbits"})}>
                        <Space.Compact>
                            <Select id={"cracker_config_uart_stopbits"} size={"small"} style={{minWidth: 90}}
                                    disabled={!uart.enable}
                                    value={uart.stopbits} onChange={uart.setStopbits} options={[
                                {value: 0, label: "1"},
                                {value: 1, label: "1.5"},
                                {value: 2, label: "2"},
                            ]}/>
                        </Space.Compact>
                    </Form.Item>
                    <Form.Item style={{marginRight: 1}}>
                        <Checkbox id={"cracker_config_spi_enable"} checked={spi.enable} onChange={() => {
                            spi.setEnable(!spi.enable)
                        }}>
                            <FormattedMessage id={"cracker.config.nut.spi.enable"}/>
                        </Checkbox>
                    </Form.Item>
                    <Tooltip
                        title={spi.enable ? "设置SPI Speed 会根据根据您输入的数值自动转换SCK的整数倍，并反推出真实速率，可能导致您输入的和预想值不一致，这个需要回车后下发数据" : null}>
                        <Form.Item label={intl.formatMessage({id: "cracker.config.nut.spi.speed"})}>
                            <InputNumber precision={2} id={"cracker_config_spi_speed"} value={spi.speed}
                                         onPressEnter={(e) => {
                                             spi.setSpeed(Number((e.target as HTMLInputElement).value))
                                         }} controls={false}
                                         size={"small"} disabled={!spi.enable}/>
                        </Form.Item>
                    </Tooltip>
                    <Form.Item label={intl.formatMessage({id: "cracker.config.nut.spi.cpol"})}>
                        <Space.Compact>
                            <Select id={"cracker_config_spi_cpol"} size={"small"} style={{minWidth: 90}}
                                    disabled={!spi.enable}
                                    value={spi.cpol} onChange={spi.setCpol} options={[
                                {value: 0, label: intl.formatMessage({id: "cracker.config.nut.spi.cpol.low"})},
                                {value: 1, label: intl.formatMessage({id: "cracker.config.nut.spi.cpol.high"})},
                            ]}/>
                        </Space.Compact>
                    </Form.Item>
                    <Form.Item label={intl.formatMessage({id: "cracker.config.nut.spi.cpha"})}>
                        <Space.Compact>
                            <Select id={"cracker_config_spi_cpha"} size={"small"} style={{minWidth: 90}}
                                    disabled={!spi.enable}
                                    value={spi.cpha} onChange={spi.setCpha} options={[
                                {value: 0, label: intl.formatMessage({id: "cracker.config.nut.spi.cpha.low"})},
                                {value: 1, label: intl.formatMessage({id: "cracker.config.nut.spi.cpha.high"})},
                            ]}/>
                        </Space.Compact>
                    </Form.Item>
                    <Tooltip
                        title={spi.enable ? intl.formatMessage({id: "cracker.config.nut.spi.autoSelect.tooltip"}) : null}>
                        <Form.Item style={{marginRight: 1}}>
                            <Checkbox id={"cracker_config_spi_auto_select"} checked={spi.csnAuto} onChange={() => {
                                spi.setCsnAuto(!spi.csnAuto)
                            }} disabled={!spi.enable}>
                                <FormattedMessage id={"cracker.config.nut.spi.autoSelect"}/>
                            </Checkbox>
                        </Form.Item>
                    </Tooltip>

                    <Tooltip
                        title={spi.enable ? intl.formatMessage({id: "cracker.config.nut.spi.csnDly.tooltip"}) : null}>

                        <Form.Item style={{marginRight: 1}}>
                            <Checkbox id={"cracker_config_spi_csn_dly"} checked={spi.csnDelay} onChange={() => {
                                spi.setCsnDelay(!spi.csnDelay)
                            }} disabled={!spi.enable}>
                                <FormattedMessage id={"cracker.config.nut.spi.csnDly"}/>
                            </Checkbox>
                        </Form.Item>
                    </Tooltip>
                    <Form.Item style={{marginRight: 1}}>
                        <Checkbox id={"cracker_config_i2c_enable"} checked={i2c.enable} onChange={() => {
                            i2c.setEnable(!i2c.enable)
                        }}>
                            <FormattedMessage id={"cracker.config.nut.i2c.enable"}/>
                        </Checkbox>
                    </Form.Item>
                    <Form.Item label={intl.formatMessage({id: "cracker.config.nut.i2c.dev_addr"})}>
                        <Input id={"cracker_config_i2c_dev_addr"} value={i2c.devAddr}
                               onChange={(e: ChangeEvent<HTMLInputElement>) => i2c.setDevAddr(e.target.value)}
                               disabled={!i2c.enable} size={"small"} style={{width: 90}}/>
                    </Form.Item>
                    <Form.Item label={intl.formatMessage({id: "cracker.config.nut.i2c.speed"})}>
                        <Space.Compact>
                            <Select id={"cracker_config_i2c_speed"} size={"small"} style={{minWidth: 90}}
                                    disabled={!i2c.enable}
                                    value={i2c.speed} onChange={i2c.setSpeed} options={[
                                {value: 0, label: "100K"},
                                {value: 1, label: "400K"},
                                {value: 2, label: "1M"},
                                {value: 3, label: "3400K"},
                                {value: 4, label: "5M"},
                            ]}/>
                        </Space.Compact>
                    </Form.Item>
                    <Tooltip
                        title={i2c.enable ? intl.formatMessage({id: "cracker.config.nut.i2c.stretchEnable.tooltip"}) : null}>
                        <Form.Item style={{marginRight: 1}}>
                            <Checkbox id={"cracker_config_i2c_stretch_enable"} checked={i2c.stretch} onChange={() => {
                                i2c.setStretch(!i2c.stretch)
                            }} disabled={!i2c.enable}>
                                <FormattedMessage id={"cracker.config.nut.i2c.stretchEnable"}/>
                            </Checkbox>
                        </Form.Item>
                    </Tooltip>
                </Form>
            </Col>
        </Row>
    );
};

export default ConfigCommon;