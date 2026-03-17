# Cracker API 文档

Cracker 模块包含对设备的所有操作，如设备配置、数据传输和采集。

---

## 目录

- [CrackerBasic](#crackerbasic) - 基础设备类
- [CrackerS1](#crackers1) - S1 设备类
- [CrackerG1](#crackerg1) - G1 设备类
- [CrackerO1](#crackero1) - O1 设备类

---

## CrackerBasic

基础设备类，提供 CNP 协议支持、配置管理、固件维护等基本操作。

**继承关系:** `CrackerBasic[T]`

### 构造函数

```python
CrackerBasic(
    address: str | tuple | None = None,
    bin_server_path: str | None = None,
    bin_bitstream_path: str | None = None,
    operator_port: int = None
)
```

**参数:**

- `address` - 设备地址，格式为 `(ip, port)` 或 `"[cnp://]<ip>[:port]"`
- `bin_server_path` - 固件文件路径（通常不需要指定）
- `bin_bitstream_path` - 比特流文件路径（通常不需要指定）
- `operator_port` - 操作端口

### 常用方法

#### 连接管理

| 方法 | 描述 |
|------|------|
| `connect()` | 连接到 Cracker 设备 |
| `disconnect()` | 断开与 Cracker 设备的连接 |
| `reconnect()` | 重新连接设备 |
| `get_connection_status()` | 获取连接状态，返回 `bool` |

#### 地址配置

| 方法 | 描述 |
|------|------|
| `set_address(address)` | 以元组格式设置设备地址 |
| `set_ip_port(ip, port)` | 设置设备 IP 和端口 |
| `set_uri(uri)` | 以 URI 格式设置设备地址 |
| `get_address()` | 获取设备地址，返回 `(ip, port)` |
| `get_uri()` | 获取 URI 格式的设备地址 |
| `change_ip(new_ip, new_mask, new_gateway)` | 更改设备 IP 地址 |

#### 配置管理

| 方法 | 描述 |
|------|------|
| `get_default_config()` | 获取默认配置（抽象方法） |
| `get_current_config()` | 获取当前配置 |
| `write_config_to_cracker(config)` | 同步配置到设备 |
| `dump_config(path)` | 导出配置到 JSON 文件或字符串 |
| `load_config_from_file(path)` | 从 JSON 文件加载配置 |
| `load_config_from_str(json_str)` | 从 JSON 字符串加载配置 |

#### 设备信息

| 方法 | 描述 |
|------|------|
| `get_id()` | 获取设备 ID |
| `get_hardware_model()` | 获取硬件型号 |
| `get_firmware_version()` | 获取固件版本 |
| `get_firmware_info()` | 获取固件信息 |
| `get_bitstream_version()` | 获取比特流版本 |

#### 示波器功能

| 方法 | 描述 |
|------|------|
| `osc_single()` | 单次触发采样 |
| `osc_force()` | 强制产生波形数据 |
| `osc_is_triggered()` | 检查是否触发，返回 `(status, bool)` |
| `osc_get_wave(channel, offset, sample_count)` | 获取波形 |
| `osc_get_analog_wave(channel, offset, sample_count)` | 获取模拟波形 |
| `osc_get_digital_wave(channel, offset, sample_count)` | 获取数字波形 |

#### 日志管理

| 方法 | 描述 |
|------|------|
| `set_logging_level(level)` | 设置日志级别 (debug, info, warning, error) |
| `set_logger_info_payload_max_length(length)` | 设置 info 日志最大 payload 长度 |
| `set_logger_debug_payload_max_length(length)` | 设置 debug 日志最大 payload 长度 |

#### 底层通信

| 方法 | 描述 |
|------|------|
| `send_and_receive(message)` | 发送消息并接收响应 |
| `send_with_command(command, rfu, payload)` | 使用命令发送消息 |
| `get_operator()` | 获取操作对象 |

---

## CrackerS1

继承自 `CrackerBasic`，增加了协议通信支持（I2C、SPI、UART）和 Nut 芯片控制。

### 配置类: ConfigS1

继承自 `ConfigBasic`，增加了以下配置项：

- `nut_enable` - Nut 使能
- `nut_voltage` - Nut 电压 (默认 3.3V)
- `nut_clock_enable` - Nut 时钟使能
- `nut_clock` - Nut 时钟频率 (默认 8000 kHz)
- `nut_timeout` - Nut 超时时间
- `nut_uart_*` - UART 配置
- `nut_spi_*` - SPI 配置
- `nut_i2c_*` - I2C 配置

### Nut 控制

| 方法 | 描述 |
|------|------|
| `nut_voltage(voltage)` | 设置 Nut 电压 |
| `nut_voltage_enable()` | 使能 Nut 电压 |
| `nut_voltage_disable()` | 禁用 Nut 电压 |
| `nut_clock_freq(clock)` | 设置 Nut 时钟频率 |
| `nut_clock_enable()` | 使能 Nut 时钟 |
| `nut_clock_disable()` | 禁用 Nut 时钟 |
| `nut_timeout_ms(timeout)` | 设置 Nut 超时 |
| `nut_reset(polar, time)` | 复位 Nut 芯片 |
| `nut_reset_io_enable(enable)` | 复位 IO 使能 |

### I2C 通信

| 方法 | 描述 |
|------|------|
| `i2c_config(dev_addr, speed, enable_stretch)` | 配置 I2C |
| `i2c_enable()` | 使能 I2C |
| `i2c_disable()` | 禁用 I2C |
| `i2c_reset()` | 复位 I2C |
| `i2c_transmit(tx_data, is_trigger)` | 通过 I2C 发送数据 |
| `i2c_receive(rx_count, is_trigger)` | 通过 I2C 接收数据 |
| `i2c_transceive(tx_data, rx_count, is_trigger)` | 通过 I2C 发送并接收数据 |
| `i2c_transmit_delay_receive(tx_data, delay, rx_count, is_trigger)` | 带延迟的 I2C 发送接收 |

**Trigger 时序图:**

```
is_trigger=True:
TRIG: ───┐            ┌─── HIGH
         |            |
         └────────────┘    LOW
         ┌────────────┐
         │   tx_data  │
         └────────────┘

is_trigger=False:
TRIG: ──────────────────── HIGH
                           LOW
         ┌────────────┐
         │   tx_data  │
         └────────────┘
```

### SPI 通信

| 方法 | 描述 |
|------|------|
| `spi_config(speed, cpol, cpha, csn_auto, csn_delay)` | 配置 SPI |
| `spi_enable()` | 使能 SPI |
| `spi_disable()` | 禁用 SPI |
| `spi_reset()` | 复位 SPI |
| `spi_transmit(tx_data, is_trigger)` | 通过 SPI 发送数据 |
| `spi_receive(rx_count, dummy, is_trigger)` | 通过 SPI 接收数据 |
| `spi_transceive(tx_data, rx_count, dummy, is_trigger)` | 通过 SPI 发送并接收数据 |
| `spi_transmit_delay_receive(tx_data, delay, rx_count, dummy, is_trigger)` | 带延迟的 SPI 发送接收 |
| `spi_transceive_delay_transceive(tx_data1, tx_data2, is_delay, delay, is_trigger)` | 两阶段 SPI 传输 |

### UART 通信

| 方法 | 描述 |
|------|------|
| `uart_config(baudrate, bytesize, parity, stopbits)` | 配置 UART |
| `uart_io_enable()` | 使能 UART IO |
| `uart_io_disable()` | 禁用 UART IO |
| `uart_reset()` | 复位 UART |
| `uart_transmit(tx_data, is_trigger)` | 通过 UART 发送数据 |
| `uart_receive(rx_count, timeout, is_trigger)` | 通过 UART 接收数据 |
| `uart_transmit_receive(tx_data, rx_count, timeout, is_trigger)` | UART 发送接收 |
| `uart_receive_fifo_remained()` | 获取 UART 接收 FIFO 剩余字节数 |
| `uart_receive_fifo_dump()` | 读取 UART 接收 FIFO 中的所有数据 |
| `uart_receive_fifo_clear()` | 清除 UART 接收 FIFO |

### 示波器配置

| 方法 | 描述 |
|------|------|
| `osc_analog_enable(channel)` | 使能模拟通道 |
| `osc_analog_disable(channel)` | 禁用模拟通道 |
| `osc_analog_gain(channel, gain)` | 设置模拟增益 (1-50) |
| `osc_sample_clock(clock)` | 设置采样率 (8M, 12M, 24M, 48M, 65M) |
| `osc_sample_clock_phase(phase)` | 设置采样相位 |
| `osc_sample_delay(delay)` | 设置采样延迟 |
| `osc_sample_length(length)` | 设置采样长度 |
| `osc_trigger_mode(mode)` | 设置触发模式 (EDGE/PATTERN) |
| `osc_trigger_source(source)` | 设置触发源 (Nut/ChA/ChB/Protocol/Reset/Voltage) |
| `osc_trigger_edge(edge)` | 设置触发边沿 (up/down/either) |
| `osc_trigger_level(level)` | 设置触发电平 |

### 寄存器操作

| 方法 | 描述 |
|------|------|
| `register_read(base_address, offset)` | 读取寄存器 |
| `register_write(base_address, offset, data)` | 写入寄存器 |

### 数字 IO

| 方法 | 描述 |
|------|------|
| `digital_pin_mode(pin_num, mode)` | 设置数字 IO 引脚模式 (INPUT/OUTPUT) |
| `digital_read(pin_num)` | 读取数字 IO 引脚电平 |
| `digital_write(pin_num, value)` | 设置数字 IO 引脚电平 |

---

## CrackerG1

继承自 `CrackerS1`，增加了 Glitch (故障注入) 功能。

### 配置类: ConfigG1

继承自 `ConfigS1`，增加了以下配置项：

- `glitch_vcc_*` - VCC Glitch 配置
- `glitch_gnd_*` - GND Glitch 配置
- `glitch_clock_*` - 时钟 Glitch 配置

### Glitch VCC

| 方法 | 描述 |
|------|------|
| `glitch_vcc_normal(voltage)` | 设置 VCC 正常电压 |
| `glitch_vcc_config(wait, level, length, delay, repeat)` | 配置 VCC Glitch |
| `glitch_vcc_arm()` | 设置 VCC Glitch 为 armed 状态 |
| `glitch_vcc_force()` | 强制触发 VCC Glitch |
| `glitch_vcc_reset()` | 重置 VCC Glitch 配置 |

**Glitch 配置时序:**

```
v_normal────┬───────────────────┐       ┌────────────┐       ┌───────
            |       wait        | count |    delay   | count |
            |                   |       |            |       |
            |                   └───────┘            └───────┘ <--------- level voltage
            |                       └────────────────────┘
             Trigger                         repeat
```

**参数说明:**

- `wait` - Glitch 产生前等待时间（时钟个数）
- `level` - Glitch DAC 电压值
- `length` - Glitch 持续时间，单位 10ns
- `delay` - Glitch 之间的延迟
- `repeat` - Glitch 重复次数

### Glitch GND

| 方法 | 描述 |
|------|------|
| `glitch_gnd_normal(voltage)` | 设置 GND 正常电压 |
| `glitch_gnd_config(wait, level, length, delay, repeat)` | 配置 GND Glitch |
| `glitch_gnd_arm()` | 设置 GND Glitch 为 armed 状态 |
| `glitch_gnd_force()` | 强制触发 GND Glitch |
| `glitch_gnd_reset()` | 重置 GND Glitch 配置 |

### Glitch Clock

| 方法 | 描述 |
|------|------|
| `glitch_clock_normal(wave)` | 设置正常时钟波形 |
| `glitch_clock_normal_enable()` | 使能正常时钟 |
| `glitch_clock_normal_disable()` | 禁用正常时钟 |
| `glitch_clock_config(wave, wait, delay, repeat)` | 配置时钟 Glitch |
| `glitch_clock_arm()` | 设置时钟 Glitch 为 armed 状态 |
| `glitch_clock_force()` | 强制触发时钟 Glitch |
| `glitch_clock_reset()` | 重置时钟 Glitch |

### Nut 时钟 (覆盖 S1)

| 方法 | 描述 |
|------|------|
| `nut_clock_freq(clock)` | 设置 Nut 时钟频率 (支持 4M, 8M, 10M, 16M, 20M, 40M, 80M) |

---

## CrackerO1

继承自 `CrackerG1`，增加了波形发生器、LED 显示、PWM、扩展 GPIO 等功能。

### 波形发生器

| 方法 | 描述 |
|------|------|
| `set_waveform_standard(waveform, vpp, frequency, offset, duty, phase)` | 设置标准波形 |
| `set_waveform_sine(frequency, vpp, phase, offset)` | 设置正弦波 |
| `set_waveform_square(frequency, duty, vpp, phase, offset)` | 设置方波 |
| `set_waveform_triangle(frequency, vpp, phase, offset)` | 设置三角波 |
| `set_waveform_sawtooth(frequency, vpp, slope, phase, offset)` | 设置锯齿波 |
| `set_waveform_dc(voltage)` | 设置直流电压 |
| `set_waveform_arbitrary(wave)` | 设置任意波形 |
| `set_waveform_from_file(file_path)` | 从文件加载波形 |

**波形参数:**

- `frequency` - 输出频率 (Hz)，支持数值或字符串如 "1MHz", "10kHz"
- `vpp` - 峰峰值电压 (Volt)
- `phase` - 初始相位 (弧度 rad)
- `offset` - 直流偏置电压 (Volt)
- `duty` - 占空比 (0-1)，仅对方波有效
- `slope` - 上升段占空比 (0-1)，对锯齿波有效

**支持的波形类型:**

- `"dc"` - 直流电压
- `"sine"` - 正弦波
- `"square"` - 方波
- `"triangle"` - 三角波
- `"sawtooth"` - 锯齿波

### LED 显示

| 方法 | 描述 |
|------|------|
| `set_led_text(text, x, y, auto_wrap)` | 设置 LED 文本显示 |
| `set_led_image(image_path, x, y, fit)` | 设置 LED 图片显示 |
| `set_led_content(t, x, y, c, w)` | 设置 LED 内容（底层方法） |

**LED 参数:**

- 屏幕分辨率: 64x64 像素
- 字符规格: 宽 5 像素，高 6 像素，间距 1 像素
- 坐标原点在左上角

### PWM 输出

| 方法 | 描述 |
|------|------|
| `set_pwm(freq, duty_cycle)` | 设置 PWM 输出 (GP29 引脚) |

**参数:**

- `freq` - PWM 频率 (Hz)
- `duty_cycle` - 占空比 (0-1)

### 电压测量

| 方法 | 描述 |
|------|------|
| `get_voltage_a0()` | 获取测量点 A0 电压 |
| `get_voltage_a1()` | 获取测量点 A1 电压 |

### 开关状态

| 方法 | 描述 |
|------|------|
| `get_switch_status(switch_id)` | 获取开关状态 |
| `get_switch_status_pl()` | 获取 PL 开关状态 |
| `get_switch_status_ps()` | 获取 PS 开关状态 |

**返回格式:** `(status, (sw1, sw2))` - sw1 和 sw2 分别为两个状态位，0 表示关闭，1 表示打开

### 扩展数字 IO

| 方法 | 描述 |
|------|------|
| `digital_pin_mode(pin_id, mode)` | 设置数字 IO 引脚模式 |
| `digital_read(pin_id)` | 读取数字 IO 引脚电平 |
| `digital_write(pin_id, value)` | 设置数字 IO 引脚电平 |

**支持的引脚:**

- GP0-GP7
- GP21-GP27
- A (A0-A5)
- A2-A5
- IO2-IO9

---

## 返回值说明

大多数方法返回 `(status, response)` 元组：

- `status` - 协议响应状态码，`0` 表示成功
- `response` - 响应数据，可能为 `None`、`bytes`、`int` 或其他类型

---

## 常量

### 连接状态

```python
CrackerBasic.DISCONNECTED = -2      # 未连接
CrackerBasic.NON_PROTOCOL_ERROR = -1  # 非协议错误
```

### 采样率

```python
65M, 48M, 24M, 12M, 8M  # kHz
```

### 触发源

```python
'N', 'A', 'B', 'P', 'R', 'V'  # 或
'Nut', 'ChA', 'ChB', 'Protocol', 'Reset', 'Voltage'
```

### 触发边沿

```python
'up', 'down', 'either'  # 或
'u', 'd', 'e'           # 或
0, 1, 2
```

### 触发模式

```python
'EDGE', 'PATTERN'  # 或
'E', 'P'           # 或
0, 1
```
