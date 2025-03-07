import marimo

__generated_with = "0.7.8"
app = marimo.App(width="medium")


@app.cell
def __():
    import marimo as mo
    return mo,


@app.cell
def __(mo):
    get_connnection_status, set_connnection_status = mo.state(value='未连接')
    return get_connnection_status, set_connnection_status


@app.cell
def __(set_connnection_status):
    from cracknuts.cracker.cracker_s1 import CrackerS1


    def connect(addr):
        global basic_cracker
        ip, port = addr.split(':')
        basic_cracker = CrackerS1((ip, int(port)))
        basic_cracker.connect()
        set_connnection_status('已连接')

    def disconnect(v):
        if basic_cracker:
            basic_cracker.disconnect()
            set_connnection_status('未连接')

    basic_cracker = None
    return CrackerS1, basic_cracker, connect, disconnect


@app.cell
def __(basic_cracker):
    def echo(message):
        # basic_cracker = BasicCracker(('127.0.0.1', 12345))
        # basic_cracker.connect()
        if message:
            return basic_cracker.echo_hex(message)

    # echo(text_echo_req.value)
    return echo,


@app.cell
def __(connect, disconnect, echo, mo):
    text_ip = mo.ui.text('192.168.0.10:8080')

    button_connect = mo.ui.button(label='连接', on_change=lambda _: connect(text_ip.value))
    button_disconnect = mo.ui.button(label='断开连接', on_change=disconnect)

    ### for test
    text_echo_req = mo.ui.text(label='请求')
    get_echo_res, set_echo_res = mo.state(value='')

    button_send_echo_message = mo.ui.button(label='发送回声消息', on_click=lambda _: set_echo_res(echo(text_echo_req.value)))


    get_cracker_id, set_cracker_id = mo.state(value='')
    get_cracker_name, set_cracker_name = mo.state(value='')

    button_test = mo.ui.button(label='测试')
    button_run = mo.ui.button(label='运行')

    switch_connection = mo.ui.switch()
    return (
        button_connect,
        button_disconnect,
        button_run,
        button_send_echo_message,
        button_test,
        get_cracker_id,
        get_cracker_name,
        get_echo_res,
        set_cracker_id,
        set_cracker_name,
        set_echo_res,
        switch_connection,
        text_echo_req,
        text_ip,
    )


@app.cell
def __(get_connnection_status):
    get_connnection_status()
    return


@app.cell
def __(
    button_connect,
    button_disconnect,
    button_run,
    button_send_echo_message,
    button_test,
    get_connnection_status,
    get_cracker_id,
    get_cracker_name,
    get_echo_res,
    mo,
    switch_connection,
    text_echo_req,
    text_ip,
):
    mo.Html(f'''
    <div style="border-radius: 5px; border: 1px solid black; margin: 5px; padding: 5px;">

        <div style="padding: 5px;">
            <button>connect</button>
            <label> IP:
                {text_ip}
            </label>
            {button_connect}
            {button_disconnect}
            <span>{get_connnection_status()}</span>
            <span>{get_cracker_id()}</span>
            <span>{get_cracker_name()}</span>
        </div>
        <div style="padding: 5px;">
            {button_test}
            {button_run}
        </div>
        <div>
        <div>
        <span>文本回声测试：</span>{text_echo_req} {button_send_echo_message} {get_echo_res()}
        </div>
            <div style="border-radius: 5px; border: 1px solid black; display: inline-block; margin: 5px; padding: 5px; vertical-align: top; height: 350px;">
                <div style="border: 1px solid black; margin: 5px; padding: 5px;">
                    <div>
                        <label for="">NUT电压: <select>
                            <option>11111</option>
                        </select></label>
                        <label for="">供电使能
                            {switch_connection}
                        </label>
                    </div>
                    <div>
                        <label for="">NUT时钟: <select>
                            <option>11111</option>
                        </select></label>
                        <label for="">NUT时钟相位:
                            <input type="number"/></label>
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
                    <label>通信超时:
                        <select>
                            <option>213123</option>
                        </select>
                    </label>
                </div>
                <div>
                    <div style="border: 1px solid black; display: inline-block; margin: 5px; width: 150px;">
                        <div style="border-bottom: 1px solid black; padding: 5px;">UART</div>
                        <div style="padding: 5px;"><label>Baud: <select>
                            <option>123</option>
                        </select></label></div>
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
    return


@app.cell
def __():
    return


if __name__ == "__main__":
    app.run()
