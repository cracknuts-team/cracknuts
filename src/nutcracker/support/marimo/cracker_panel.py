import marimo as mo

_panel_html = '''
<div style="border-radius: 5px; border: 1px solid black; margin: 5px; padding: 5px;">

    <div style="padding: 5px;">
        <button>connect</button>
        <label> IP:
            {text_ip}
        </label>{button_connect}
    </div>
    <div style="padding: 5px;">
        {button_test}
        {button_run}
    </div>
    <div>
        <div style="border-radius: 5px; border: 1px solid black; display: inline-block; margin: 5px; padding: 5px; vertical-align: top; height: 350px;">
            <div style="border: 1px solid black; margin: 5px; padding: 5px;">
                <div>
                    <label for="">NUT电压: <select>
                        <option>11111</option>
                    </select></label>
                    <label for="">供电使能
                        <input type="checkbox"/>
                    </label>
                </div>
                <div>
                    <label for="">NUT时钟: <select>
                        <option>11111</option>
                    </select></label>
                    <label for="">NUT时钟相位:
                        <select>
                            <option>11111</option>
                        </select></label>
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
'''


def get_mo_hmtl():
    return mo.Html(_panel_html)


def get_mo_ui_elements():
    return (
        text_ip := mo.ui.text('192.168.0.10'),
        button_connect := mo.ui.button(label='连接'),

        button_test := mo.ui.button(label='测试'),
        button_run := mo.ui.button(label='运行'),

        input_nut_voltage := mo.ui.dropdown(label='NUT电压', options=['1000']),
        input_nut_enable_power := mo.ui.checkbox(label='NUT使能'),
        input_nut_current := mo.ui.input(label='NUT频率'),
        input_nut_power := mo.ui.input(label='NUT功率'),
        input_nut_frequency := mo.ui.input(label='NUT频率'),
        input_nut_phase := mo.ui.input(label='NUT相位'),
        input_sample_clock := mo.ui.input(label='采样时钟'),
        input_sample_clock_phase:= mo.ui.input(label='采样时钟相位'),
    )
