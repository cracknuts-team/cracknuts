import marimo

__generated_with = "0.7.20"
app = marimo.App(width="full")


@app.cell
def __(panel):
    panel
    return


@app.cell(hide_code=True)
def __(chart_wave, mo, refresh_button):
    mo.vstack([refresh_button, chart_wave])
    return


@app.cell
def __():
    import marimo as mo
    import altair as alt
    import numpy as np
    from cracknuts.cracker.basic_cracker import CrackerS1
    from cracknuts.acquisition.acquisition import Acquisition
    import cracknuts.solver.trace as nt
    import cracknuts.logger as t_logger
    import logging
    import time
    return (
        Acquisition,
        CrackerS1,
        alt,
        logging,
        mo,
        np,
        nt,
        t_logger,
        time,
    )


@app.cell
def __(mo):
    get_connnection_status, set_connnection_status = mo.state(value='未连接')

    get_nut_voltage_state, set_nut_voltage_state = mo.state(3.3)
    return (
        get_connnection_status,
        get_nut_voltage_state,
        set_connnection_status,
        set_nut_voltage_state,
    )


@app.cell
def __(
    AbsCracker,
    AcquisitionTemplate,
    BasicCracker,
    logging,
    t_logger,
    time,
):
    def init(c: AbsCracker):
        c.cracker_nut_voltage(3300)
        time.sleep(1)
        c.cracker_nut_enable(1)
        time.sleep(2)
        # aes
        # key = '01 00 00 00 00 00 00 10 00 11 22 33 44 55 66 77 88 99 aa bb cc dd ee ff'
        # des
        key = '02 00 00 00 00 00 00 08 88 99 AA BB CC DD EE FF'
        key = key.replace(' ', '')
        key = bytes.fromhex(key)
        data_len = 6
        c.cracker_serial_data(data_len, key)


    def do(c: AbsCracker):
        # aes
        # d = '01 02 00 00 00 00 00 10 00 11 22 33 44 55 66 77 88 99 aa bb cc dd ee ff'
        # l = '00 00 00 00 00 10 62 F6 79 BE 2B F0 D9 31 64 1E 03 9C A3 40 1B B2'
        # l = len(l.split(' '))
        # des
        data = '02 02 00 00 00 00 00 08 88 99 AA BB CC DD EE FF'
        res_sample = '00 00 00 00 00 08 97 9F FF 9B 97 0C A6 A4'

        data_len = len(res_sample.split(' '))
        data = data.replace(' ', '')
        data = bytes.fromhex(data)
        c.cracker_serial_data(data_len, data)

    basic_cracker = BasicCracker()

    t_logger.set_level(logging.DEBUG, basic_cracker)

    def get_acquisition():
        return AcquisitionTemplate.builder().cracker(basic_cracker)._init(init).do(do).build()

    acquisition = get_acquisition()
    t_logger.set_level(logging.DEBUG, acquisition)
    return acquisition, basic_cracker, do, get_acquisition, init


@app.cell
def __(
    acquisition,
    basic_cracker,
    set_connnection_status,
    set_nut_voltage_state,
):
    def connect(ip, port):
        global basic_cracker
        basic_cracker.set_addr(ip, int(port))
        basic_cracker.connect()
        if basic_cracker.get_connection_status():
            set_connnection_status('已连接')
        else:
            set_connnection_status('未连接')
            set_nut_voltage_state(3.3)

    def disconnect(v):
        if basic_cracker:
            basic_cracker.disconnect()
            set_connnection_status('未连接')

    def set_nut_enable(enable):
        if basic_cracker.get_connection_status():
            basic_cracker.cracker_nut_enable(enable)
        else:
            print(f'set_nut_enable {enable}')

    def set_nut_voltage(voltage):
        set_nut_voltage_state(voltage)
        if basic_cracker.get_connection_status():
            basic_cracker.cracker_nut_voltage(int(voltage * 1000))

    def set_nut_interface(interface):
        if basic_cracker.get_connection_status():
            basic_cracker.cracker_nut_interface(interface)

    def set_nut_timeout(timeout):
        if basic_cracker.get_connection_status():
            basic_cracker.cracker_nut_timeout(timeout)

    def set_serial_baud(baud):
        if basic_cracker.get_connection_status():
            basic_cracker.cracker_serial_baud(baud)

    def start_test(v):
        if basic_cracker.get_connection_status():
            acquisition.test(1000)

    def stop(v):
        if basic_cracker.get_connection_status():
            acquisition.stop()

    def start_run(v):
        if basic_cracker.get_connection_status():
            acquisition.run()

    def echo(message):
        # basic_cracker = BasicCracker(('127.0.0.1', 12345))
        # basic_cracker.connect()
        if message:
            return basic_cracker.echo_hex(message)
    return (
        connect,
        disconnect,
        echo,
        set_nut_enable,
        set_nut_interface,
        set_nut_timeout,
        set_nut_voltage,
        set_serial_baud,
        start_run,
        start_test,
        stop,
    )


@app.cell
def __(
    connect,
    disconnect,
    echo,
    get_nut_voltage_state,
    mo,
    set_nut_enable,
    set_nut_interface,
    set_nut_timeout,
    set_nut_voltage,
    set_serial_baud,
    start_run,
    start_test,
    stop,
):
    # define acquisition ui

    text_ip = mo.ui.text('192.168.0.12')
    text_port = mo.ui.text('8080')

    button_connect = mo.ui.button(label='连接', on_change=lambda _: connect(text_ip.value, text_port.value))
    # button_connect = mo.ui.button(label='连接', on_change=lambda _: set_nut_voltage_state(3.3))
    button_disconnect = mo.ui.button(label='断开连接', on_change=disconnect)

    ### for test
    text_echo_req = mo.ui.text(label='请求')
    get_echo_res, set_echo_res = mo.state(value='')

    button_send_echo_message = mo.ui.button(label='发送回声消息', on_click=lambda _: set_echo_res(echo(text_echo_req.value)))


    get_cracker_id, set_cracker_id = mo.state(value='')
    get_cracker_name, set_cracker_name = mo.state(value='')

    button_test = mo.ui.button(label='测试', on_click=start_test)
    button_run = mo.ui.button(label='运行', on_click=start_run)
    button_stop = mo.ui.button(label='停止', on_click=stop)

    switch_connection = mo.ui.switch()

    nut_enable = mo.ui.dropdown(label='Nut使能', options={'启用': 1, '停用': 0}, value='停用', on_change=set_nut_enable)

    nut_voltage = mo.ui.number(label='Nut电压', start=2.0, stop=4.4, step=0.1, on_change=set_nut_voltage, value=get_nut_voltage_state(), debounce=True, full_width=False)
    nut_interface = mo.ui.dropdown(label='Nut通讯选择', options={'UART': 0, 'SPI': 1, 'I2C': 2, 'CAN': 3}, allow_select_none=False, value='UART', on_change=set_nut_interface)
    nut_timeout = mo.ui.number(label='Nut通信超时', start=10, stop=60000, step=100, value=10000, on_change=set_nut_timeout, debounce=True)
    serial_baud = mo.ui.dropdown(label='串口波特率', options={'9600': 9600, '115200': 115200, '57600': 57600, '19200': 19200}, allow_select_none=False, value='115200', on_change=set_serial_baud)
    serial_width = mo.ui.dropdown(label='串口数据位', value='5', options={'5': 5, '6': 6, '7': 7, '8': 8})
    serial_stop = mo.ui.dropdown(label='串口停止位', value='1', options={'1': 0, '1.5': 1, '2': 2})
    serial_odd_eve = mo.ui.dropdown(label='串口奇偶', value='偶校验', options={'偶校验': 0, '奇校验': 1})

    spi_cpol = mo.ui.dropdown(label='CPOL', value='0', options={'0': 0, '1': 1})
    spi_cpha = mo.ui.dropdown(label='CPHA', value='0', options={'0': 0, '1': 1})
    spi_baud = mo.ui.number(label='数据位长', value=0, start=0, step=1, stop=100)
    spi_freq = mo.ui.number(label='速率', value=0, start=0, step=1, stop=100)
    spi_timeout = mo.ui.number(label='超时', value=0, start=0, step=1, stop=100)

    # i2c_cpol = mo.ui.dropdown(label='CPOL', value='0', options={'0': 0, '1': 1})
    # spi_cpha = mo.ui.dropdown(label='CPHA', value='0', options={'0': 0, '1': 1})
    # spi_baud = mo.ui.number(label='数据位长', value=0, start=0, step=1, stop=100)
    i2c_freq = mo.ui.number(label='速率', value=0, start=0, step=1, stop=100)
    i2c_timeout = mo.ui.number(label='超时', value=0, start=0, step=1, stop=100)

    can_freq = mo.ui.number(label='速率', value=0, start=0, step=1, stop=100)
    can_timeout = mo.ui.number(label='超时', value=0, start=0, step=1, stop=100)

    scrat_sample_rate = mo.ui.dropdown(label='采样率', value='62.5 mHz', options={'62.5 mHz': 52500, '50 mHz': 50000, '25 mHz': 25000, '10 mHz': 100000})
    scrat_sample_phase = mo.ui.number(label='采样时钟相位（ °）', value=0, start=-360, step=10, stop=360)
    scrat_sample_length = mo.ui.number(label='采样长度', value=1024, start=1000, step=1, stop=100000)

    scrat_delay = mo.ui.number(label='延迟时间', value=0, start=-5000, step=100, stop=5000)
    scrat_gain = mo.ui.number(label='采样增益（%）', value=0, start=0, step=5, stop=100)
    return (
        button_connect,
        button_disconnect,
        button_run,
        button_send_echo_message,
        button_stop,
        button_test,
        can_freq,
        can_timeout,
        get_cracker_id,
        get_cracker_name,
        get_echo_res,
        i2c_freq,
        i2c_timeout,
        nut_enable,
        nut_interface,
        nut_timeout,
        nut_voltage,
        scrat_delay,
        scrat_gain,
        scrat_sample_length,
        scrat_sample_phase,
        scrat_sample_rate,
        serial_baud,
        serial_odd_eve,
        serial_stop,
        serial_width,
        set_cracker_id,
        set_cracker_name,
        set_echo_res,
        spi_baud,
        spi_cpha,
        spi_cpol,
        spi_freq,
        spi_timeout,
        switch_connection,
        text_echo_req,
        text_ip,
        text_port,
    )


@app.cell
def __(get_nut_voltage_state):
    get_nut_voltage_state()
    return


@app.cell
def __(
    button_connect,
    button_disconnect,
    button_run,
    button_send_echo_message,
    button_stop,
    button_test,
    can_freq,
    can_timeout,
    get_connnection_status,
    get_cracker_id,
    get_cracker_name,
    get_echo_res,
    i2c_freq,
    i2c_timeout,
    mo,
    nut_enable,
    nut_interface,
    nut_timeout,
    nut_voltage,
    scrat_delay,
    scrat_gain,
    scrat_sample_length,
    scrat_sample_phase,
    scrat_sample_rate,
    serial_baud,
    serial_odd_eve,
    serial_stop,
    serial_width,
    spi_baud,
    spi_cpha,
    spi_cpol,
    spi_timeout,
    text_echo_req,
    text_ip,
    text_port,
):
    panel = mo.Html(f'''
    <div style="border-radius: 5px; border: 1px solid black; margin: 5px; padding: 5px;">

        <div style="padding: 5px;">
            IP: {text_ip} PORT {text_port} {button_connect} {button_disconnect}
            <span>{get_connnection_status()}</span>
            <span>{get_cracker_id()}</span>
            <span>{get_cracker_name()}</span>
        </div>
        <!-- <span>文本回声测试：</span>{text_echo_req} {button_send_echo_message} {get_echo_res()} -->
        <div style="padding: 5px;">
            {button_test}
            {button_run}
            {button_stop}
        </div>
        <div>
        <div>

        </div>
            <div style="border-radius: 5px; border: 1px solid black; display: inline-block; margin: 5px; padding: 5px; vertical-align: top; height: 350px;">
                <div style="border: 1px solid black; margin: 5px; padding: 5px;">
                    <div>
                        {nut_voltage}V | &nbsp;&nbsp;&nbsp; {nut_enable}
                    </div>
                    <div>

                    </div>
                </div>
                <div style="border: 1px solid black; margin: 5px; padding: 5px;">
                    <div>
                        <div style="padding: 5px; display: inline-block">{scrat_sample_rate}</div>
                        <div style="padding: 5px; display: inline-block">{scrat_sample_phase}</div>
                    </div>
                    <div>
                        <div style="padding: 5px; display: inline-block">{scrat_sample_length}</div>
                        <div style="padding: 5px; display: inline-block">{scrat_delay}</div>
                    </div>
                    <div>
                        <div style="padding: 5px; display: inline-block">{scrat_gain}</div>
                    </div>
                </div>
            </div>

            <div style="border-radius: 5px; border: 1px solid black; display: inline-block; margin: 5px; padding: 5px; vertical-align: top; height: 350px;">
                <div style="padding: 5px;">
                    {nut_interface} {nut_timeout} ms
                </div>
                <div>
                    <div style="border: 1px solid black; display: inline-block; margin: 5px; width: 200px;">
                        <div style="border-bottom: 1px solid black; padding: 5px;">UART</div>
                        <div style="padding: 5px;">{serial_baud}</div>
                        <div style="padding: 5px;">{serial_width}</div>
                        <div style="padding: 5px;">{serial_stop}</div>
                        <div style="padding: 5px;">{serial_odd_eve}</div>
                    </div>
                    <div style="border: 1px solid black; display: inline-block; margin: 5px;">
                        <div style="border-bottom: 1px solid black; padding: 5px;">SPI</div>
                        <div style="padding: 5px;">{spi_cpol}</div>
                        <div style="padding: 5px;">{spi_cpha}</div>
                        <div style="padding: 5px;">{spi_baud}</div>
                        <div style="padding: 5px;">{spi_timeout}</div>
                    </div>
                </div>
                <div>
                    <div style="border: 1px solid black; display: inline-block; margin: 5px;">
                        <div style="border-bottom: 1px solid black; padding: 5px;">I2C</div>
                        <div style="padding: 5px;">{i2c_freq}</div>
                        <div style="padding: 5px;">{i2c_timeout}</div>
                    </div>
                    <!--
                    <div style="border: 1px solid black; display: inline-block; margin: 5px;">
                        <div style="border-bottom: 1px solid black; padding: 5px;">CAN</div>
                        <div style="padding: 5px;">{can_freq}</div>
                        <div style="padding: 5px;">{can_timeout}</div>
                    </div>
                    -->
                </div>
            </div>
        </div>
    </div>
    ''')
    return panel,


@app.cell
def __(mo, np):
    get_wave, set_wave = mo.state(np.array([np.random.random(1000)]))
    return get_wave, set_wave


@app.cell
def __(acquisition, refresh_button, set_wave):
    # for marimo loop refresh wave data.
    refresh_button

    set_wave(acquisition.get_last_wave())
    return


@app.cell
def __(get_wave, nt):
    trace_data, _ = nt.get_traces_df_from_ndarray(get_wave(), 0, 1, 0, 1000, 1000)
    return trace_data,


@app.cell
def __(alt, mo, trace_data):
    chart_wave = mo.ui.altair_chart(alt.Chart(trace_data).mark_line(size=1).encode(
        x = 'index:Q',
        y = 'value:Q',
        color = 'traces:N'
    ), chart_selection=False)
    return chart_wave,


@app.cell
def __(mo):
    refresh_button = mo.ui.refresh(
        options=["1s", "3s", "5s"],
        default_interval="1s",
    )
    return refresh_button,


@app.cell
def __(mo):
    mo.ui.number(start=1, stop=10).style({'color': 'red', 'width': '10px;'})
    return


if __name__ == "__main__":
    app.run()
