import marimo

__generated_with = "0.7.12"
app = marimo.App(width="full")


@app.cell
def __():
    import marimo as mo
    return mo,


@app.cell
def __(mo):
    mo.sidebar(
        [
            mo.md(f"# {mo.icon('lucide:squirrel')} Nut Cracker"),
            mo.nav_menu(
                {
                    "#/": f"{mo.icon('lucide:home')} 主页",
                    "#/settings": f"{mo.icon('lucide:settings')} 设置",
                },
                orientation="vertical",
            ),
        ]
    )
    return


@app.cell
def __(home, mo, setting):
    mo.routes({
        "#/": home,
        "#/settings": setting,
        mo.routes.CATCH_ALL: mo.md("# Home"),
    })
    return


@app.cell
def __(mo):
    home = mo.md(f"""
        # {mo.icon('lucide:squirrel')} Nut Cracker: All In One Analyzer
        ---
        <br/>
        {
        mo.hstack([
                mo.stat(value="100.54", label="Open price", caption="2.4", direction="increase", bordered=True),
                mo.stat(value="100.54", label="Price", caption="--", bordered=True),
                mo.stat(value="100.54", label="Close price", caption="2.4", direction="decrease", bordered=True),
            ], justify="space-around")
        }
        ## {mo.icon('lucide:book-open-text')} 简介
        `Nut Cracker:` 下一代侧信道分析设备，集精准测量、高效分析、先进算法与直观展示于一体，让频谱世界尽在掌握。

        ## {mo.icon('lucide:laptop-minimal')} 参考资料
        - `marimo:` 响应式`Notebook`
        - `zarr`: 高性能多维数组格式
    """)
    return home,


@app.cell
def __(
    button_connect,
    button_disconnect,
    button_run,
    button_stop,
    button_test,
    chart_wave,
    mo,
    nut_enable,
    nut_interface,
    nut_timeout,
    nut_voltage,
    serial_baud,
    serial_odd_eve,
    serial_stop,
    serial_width,
    text_ip,
    text_port,
):
    setting = mo.ui.tabs(
        {
            "📈 曲线选择": mo.ui.file_browser(multiple=False),
            "⚙️ 设置": mo.accordion(
                {
                    "💻 连接": mo.hstack(
                        [
                            text_ip,
                            text_port,
                            mo.hstack([button_connect, button_disconnect]),
                        ]
                    ),
                    "🌰 Nut": mo.vstack(
                        [
                            mo.hstack(
                                [
                                    nut_voltage,
                                    nut_enable,
                                ]
                            ),
                            mo.hstack(
                                [
                                    nut_timeout,
                                    nut_interface,
                                ]
                            ),
                            mo.callout(
                                mo.vstack(
                                    [
                                        mo.hstack(
                                            [
                                                serial_baud,
                                                serial_width,
                                                serial_stop,
                                                serial_odd_eve,
                                            ]
                                        )
                                    ]
                                )
                            ),
                        ]
                    ),
                    "⛏️ 采样": mo.hstack(
                        [
                            nut_voltage,
                            nut_enable,
                        ]
                    ),
                },
                True,
            ),
            "🕹️ 控制面板": mo.vstack(
                [
                    mo.hstack(
                        [button_test, button_run, button_stop],justify='center'
                    ),
                    mo.vstack([chart_wave])
                ]
            ),
        },
    )
    return setting,


@app.cell
def __(mo, np):
    get_wave, set_wave = mo.state(np.array([np.random.random(1000)]))
    return get_wave, set_wave


@app.cell
def __(get_wave, nt):
    trace_data, _ = nt.get_traces_df_from_ndarray(get_wave(), 0, 1, 0, 1000, 1000)
    return trace_data,


@app.cell
def __(alt, mo, trace_data):
    chart_wave = mo.ui.altair_chart(
        alt.Chart(trace_data)
        .mark_line(size=1)
        .encode(x="index:Q", y="value:Q", color="traces:N"),
        chart_selection=False,
    )
    return chart_wave,


@app.cell
def __(
    connect,
    disconnect,
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

    text_ip = mo.ui.text("192.168.0.10")
    text_port = mo.ui.text("8080")

    button_connect = mo.ui.button(
        label="连接", on_change=lambda _: connect(text_ip.value, text_port.value)
    )
    button_disconnect = mo.ui.button(label="断开连接", on_change=disconnect)


    button_test = mo.ui.button(label="测试", on_click=start_test)
    button_run = mo.ui.button(label="运行", on_click=start_run)
    button_stop = mo.ui.button(label="停止", on_click=stop)

    switch_connection = mo.ui.switch()

    nut_enable = mo.ui.dropdown(
        label="Nut使能",
        options={"启用": 1, "停用": 0},
        value="停用",
        on_change=set_nut_enable,
    )

    nut_voltage = mo.ui.number(
        label="Nut电压(V)",
        start=2.0,
        stop=4.4,
        step=0.1,
        on_change=set_nut_voltage,
        value=3.3,
    )

    nut_interface = mo.ui.dropdown(
        label="Nut通讯选择",
        options={"UART": 0, "SPI": 1, "I2C": 2, "CAN": 3},
        allow_select_none=False,
        value="UART",
        on_change=set_nut_interface,
    )
    nut_timeout = mo.ui.number(
        label="Nut通信超时(ms)",
        start=10,
        stop=60000,
        step=100,
        value=10000,
        on_change=set_nut_timeout,
    )
    serial_baud = mo.ui.dropdown(
        label="串口波特率",
        options={"9600": 9600, "115200": 115200, "57600": 57600, "19200": 19200},
        allow_select_none=False,
        value="115200",
        on_change=set_serial_baud,
    )
    serial_width = mo.ui.dropdown(
        label="串口数据位", options={"5": 5, "6": 6, "7": 7, "8": 8}
    )
    serial_stop = mo.ui.dropdown(
        label="串口停止位", options={"1": 0, "1.5": 1, "2": 2}
    )
    serial_odd_eve = mo.ui.dropdown(
        label="串口奇偶", options={"偶校验": 0, "奇校验": 1}
    )
    return (
        button_connect,
        button_disconnect,
        button_run,
        button_stop,
        button_test,
        nut_enable,
        nut_interface,
        nut_timeout,
        nut_voltage,
        serial_baud,
        serial_odd_eve,
        serial_stop,
        serial_width,
        switch_connection,
        text_ip,
        text_port,
    )


@app.cell
def __(mo):
    set_connnection_status,get_connnection_status = mo.state(False)
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
            set_connnection_status("已连接")
        except Exception as e:
            print(e)


    def disconnect(v):
        if basic_cracker:
            basic_cracker.disconnect()
            set_connnection_status("未连接")


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
def __():
    import altair as alt
    import numpy as np
    from nutcracker.cracker.basic_cracker import BasicCracker
    from nutcracker.acquisition.acquisition import Acquisition
    import nutcracker.solver.trace as nt
    import nutcracker.logger as t_logger
    import logging
    return Acquisition, BasicCracker, alt, logging, np, nt, t_logger


if __name__ == "__main__":
    app.run()
