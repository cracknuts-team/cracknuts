import marimo

__generated_with = "0.7.0"
app = marimo.App(width="medium")


@app.cell
def __(panel):
    panel
    return


@app.cell
def __(chart_wave, mo, refresh_button):
    mo.vstack([refresh_button, chart_wave])
    return


@app.cell
def __():
    import marimo as mo
    import altair as alt
    import numpy as np
    from nutcracker.cracker.basic_cracker import BasicCracker
    from nutcracker.acquisition.acquisition import Acquisition
    import nutcracker.solver.trace as nt
    import nutcracker.logger as t_logger
    import logging
    return Acquisition, BasicCracker, alt, logging, mo, np, nt, t_logger


@app.cell
def __(mo):
    get_connnection_status, set_connnection_status = mo.state(value='未连接')
    return get_connnection_status, set_connnection_status


@app.cell
def __(
    Acquisition,
    BasicCracker,
    basic_cracker,
    logging,
    set_connnection_status,
    t_logger,
):
    # define acquisition, basic cracker device and other function call in marimo loop.

    basic_cracker = BasicCracker()
    acquisition = Acquisition(basic_cracker)

    t_logger.set_level(logging.DEBUG, basic_cracker)

    def connect(ip, port):
        global basic_cracker
        basic_cracker.set_addr(ip, int(port))
        try:
            basic_cracker.connect()
            set_connnection_status('已连接')
        except Exception as e:
            print(e)

    def disconnect(v):
        if basic_cracker:
            basic_cracker.disconnect()
            set_connnection_status('未连接')

    def set_nut_enable(enable):
        basic_cracker.cracker_nut_enable(enable)

    def set_nut_voltage(voltage):
        basic_cracker.cracker_nut_voltage(int(voltage * 1000))

    def set_nut_interface(interface):
        basic_cracker.cracker_nut_interface(interface)

    def set_nut_timeout(timeout):
        basic_cracker.cracker_nut_timeout(timeout)

    def set_serial_baud(baud):
        basic_cracker.cracker_serial_baud(baud)

    def start_test(v):
        acquisition.test()

    def stop(v):
        acquisition.stop()

    def start_run(v):
        acquisition.run()

    def echo(message):
        # basic_cracker = BasicCracker(('127.0.0.1', 12345))
        # basic_cracker.connect()
        if message:
            return basic_cracker.echo_hex(message)
    return (
        acquisition,
        basic_cracker,
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

    text_ip = mo.ui.text('192.168.0.10')
    text_port = mo.ui.text('8080')

    button_connect = mo.ui.button(label='连接', on_change=lambda _: connect(text_ip.value, text_port.value))
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

    nut_voltage = mo.ui.number(label='Nut电压', start=2.0, stop=4.4, step=0.1, on_change=set_nut_voltage, value=3.3)
    nut_interface = mo.ui.dropdown(label='Nut通讯选择', options={'UART': 0, 'SPI': 1, 'I2C': 2, 'CAN': 3}, allow_select_none=False, value='UART', on_change=set_nut_interface)
    nut_timeout = mo.ui.number(label='Nut通信超时', start=10, stop=60000, step=100, value=10000, on_change=set_nut_timeout)
    serial_baud = mo.ui.dropdown(label='串口波特率', options={'9600': 9600, '115200': 115200, '57600': 57600, '19200': 19200}, allow_select_none=False, value='115200', on_change=set_serial_baud)
    serial_width = mo.ui.dropdown(label='串口数据位', options={'5': 5, '6': 6, '7': 7, '8': 8})
    serial_stop = mo.ui.dropdown(label='串口停止位', options={'1': 0, '1.5': 1, '2': 2})
    serial_odd_eve = mo.ui.dropdown(label='串口奇偶', options={'偶校验': 0, '奇校验': 1})
    return (
        button_connect,
        button_disconnect,
        button_run,
        button_send_echo_message,
        button_stop,
        button_test,
        get_cracker_id,
        get_cracker_name,
        get_echo_res,
        nut_enable,
        nut_interface,
        nut_timeout,
        nut_voltage,
        serial_baud,
        serial_odd_eve,
        serial_stop,
        serial_width,
        set_cracker_id,
        set_cracker_name,
        set_echo_res,
        switch_connection,
        text_echo_req,
        text_ip,
        text_port,
    )


@app.cell
def __(
    button_connect,
    button_disconnect,
    button_run,
    button_send_echo_message,
    button_stop,
    button_test,
    get_connnection_status,
    get_cracker_id,
    get_cracker_name,
    get_echo_res,
    mo,
    nut_enable,
    nut_interface,
    nut_timeout,
    nut_voltage,
    serial_baud,
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
        <span>文本回声测试：</span>{text_echo_req} {button_send_echo_message} {get_echo_res()}
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
                        <div style="padding: 5px; display: inline-block"><label for="">采样时钟: <select>
                            <option>11111</option>
                        </select></label></div>
                        <div style="padding: 5px; display: inline-block"><label for="">采样时钟相位: <select>
                            <option>11111</option>
                        </select></label></div>
                    </div>
                    <div>
                        <div style="padding: 5px; display: inline-block"><label for="">采样点数: <select>
                            <option>11111</option>
                        </select></label></div>
                        <div style="padding: 5px; display: inline-block"><label for="">延时点数: <select>
                            <option>11111</option>
                        </select></label></div>
                    </div>
                    <div>
                        <div style="padding: 5px; display: inline-block"><label for="">采样增益: <select>
                            <option>11111</option>
                        </select></label></div>
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
                        <div style="padding: 5px;"><label>Size: <select>
                            <option>123</option>
                        </select></label></div>
                        <div style="padding: 5px;"><label>Stop: <select>
                            <option>123</option>
                        </select></label></div>
                    </div>
                    <div style="border: 1px solid black; display: inline-block; margin: 5px; width: 150px;">
                        <div style="border-bottom: 1px solid black; padding: 5px;">SPI</div>
                        <div style="padding: 5px;"><label>CPOL: <select>
                            <option>123</option>
                        </select></label></div>
                        <div style="padding: 5px;"><label>CPHA: <select>
                            <option>123</option>
                        </select></label></div>
                        <div style="padding: 5px;"><label>BAUD: <select>
                            <option>123</option>
                        </select></label></div>
                    </div>
                </div>
                <div>
                    <div style="border: 1px solid black; display: inline-block; margin: 5px; width: 150px;">
                        <div style="border-bottom: 1px solid black; padding: 5px;">I2C</div>
                        <div style="padding: 5px;"><label>CPOL: <select>
                            <option>123</option>
                        </select></label></div>
                        <div style="padding: 5px;"><label>CPHA: <select>
                            <option>123</option>
                        </select></label></div>
                        <div style="padding: 5px;"><label>BAUD: <select>
                            <option>123</option>
                        </select></label></div>
                    </div>
                    <div style="border: 1px solid black; display: inline-block; margin: 5px; width: 150px;">
                        <div style="border-bottom: 1px solid black; padding: 5px;">CAN</div>
                        <div style="padding: 5px;"><label>CPOL: <select>
                            <option>123</option>
                        </select></label></div>
                        <div style="padding: 5px;"><label>CPHA: <select>
                            <option>123</option>
                        </select></label></div>
                        <div style="padding: 5px;"><label>BAUD: <select>
                            <option>123</option>
                        </select></label></div>
                    </div>
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
