# CrackerO1 API 参考

本文档仅包含 `0.21_o1_startup.ipynb` 示例中使用的 API。

## 构造函数

### `cn.cracker_o1(address)`

创建 CrackerO1 设备对象。

**参数:**

| 参数 | 类型 | 描述 |
|------|------|------|
| `address` | str | 设备 IP 地址，如 `'192.168.0.23'` |

**示例:**

```python
import cracknuts as cn
o1 = cn.cracker_o1('192.168.0.23')
```

---

## 连接管理

### `connect(force_update_bin=False, force_write_default_config=False)`

连接到 CrackerO1 设备。

**参数:**

| 参数 | 类型 | 默认值 | 描述 |
|------|------|--------|------|
| `force_update_bin` | bool | False | 是否强制更新固件 |
| `force_write_default_config` | bool | False | 是否强制写入默认配置 |

**示例:**

```python
o1.connect(force_update_bin=True, force_write_default_config=True)
```

---

## 设备信息

### `get_hardware_model()`

获取设备硬件型号。

**返回:** 硬件型号字符串

**示例:**

```python
o1.get_hardware_model()
```

---

## 波形发生器

### `set_waveform_sine(frequency, *, vpp=1.0, phase=0.0, offset=None)`

设置正弦波输出。

**参数:**

| 参数 | 类型 | 默认值 | 描述 |
|------|------|--------|------|
| `frequency` | float \| str | - | 输出频率 (Hz)，支持 `'8m'`, `'1MHz'`, `1000000` 等格式 |
| `vpp` | float | 1.0 | 峰峰值电压 (Volts) |
| `phase` | float | 0.0 | 初始相位 (弧度) |
| `offset` | float \| None | None | 直流偏置电压 (Volts)，默认自动设为 vpp/2 |

**返回:** `(status, response)` 元组

**示例:**

```python
o1.set_waveform_sine(frequency='8m', vpp=1.5, offset=2, phase=0.3)
```

---

### `set_waveform_square(frequency, *, duty=0.5, vpp=1.0, phase=0.0, offset=None)`

设置方波输出。

**参数:**

| 参数 | 类型 | 默认值 | 描述 |
|------|------|--------|------|
| `frequency` | float \| str | - | 输出频率 (Hz) |
| `duty` | float | 0.5 | 占空比 (0–1) |
| `vpp` | float | 1.0 | 峰峰值电压 (Volts) |
| `phase` | float | 0.0 | 初始相位 (弧度) |
| `offset` | float \| None | None | 直流偏置电压 (Volts) |

**返回:** `(status, response)` 元组

**示例:**

```python
o1.set_waveform_square(frequency='100k', vpp=1.5, duty=0.8, offset=2)
```

---

### `set_waveform_triangle(frequency, *, vpp=1.0, phase=0.0, offset=None)`

设置三角波输出。

**参数:**

| 参数 | 类型 | 默认值 | 描述 |
|------|------|--------|------|
| `frequency` | float \| str | - | 输出频率 (Hz) |
| `vpp` | float | 1.0 | 峰峰值电压 (Volts) |
| `phase` | float | 0.0 | 初始相位 (弧度) |
| `offset` | float \| None | None | 直流偏置电压 (Volts) |

**返回:** `(status, response)` 元组

**示例:**

```python
o1.set_waveform_triangle(frequency='2m', vpp=1.6, offset=0.8)
```

---

### `set_waveform_sawtooth(frequency, *, vpp=1.0, slope=1.0, phase=0.0, offset=None)`

设置锯齿波输出。

**参数:**

| 参数 | 类型 | 默认值 | 描述 |
|------|------|--------|------|
| `frequency` | float \| str | - | 输出频率 (Hz) |
| `vpp` | float | 1.0 | 峰峰值电压 (Volts) |
| `slope` | float | 1.0 | 上升段占空比 (0–1)，1.0=标准锯齿波，0.5=对称三角波 |
| `phase` | float | 0.0 | 初始相位 (弧度) |
| `offset` | float \| None | None | 直流偏置电压 (Volts) |

**返回:** `(status, response)` 元组

**示例:**

```python
o1.set_waveform_sawtooth(frequency='1m', vpp=2, offset=1, slope=0)
```

---

### `set_waveform_standard(waveform, vpp, *, frequency=None, offset=None, duty=0.5, phase=0.0)`

设置标准波形输出（通用接口）。

**参数:**

| 参数 | 类型 | 默认值 | 描述 |
|------|------|--------|------|
| `waveform` | str | - | 波形类型：`'dc'`, `'sine'`, `'square'`, `'triangle'`, `'sawtooth'` |
| `vpp` | float | - | 峰峰值电压 (Volts) |
| `frequency` | float \| str \| None | None | 输出频率 (Hz)，DC 波形可省略 |
| `offset` | float \| None | None | 直流偏置电压 (Volts) |
| `duty` | float | 0.5 | 占空比/斜率参数 |
| `phase` | float | 0.0 | 初始相位 (弧度) |

**返回:** `(status, response)` 元组

**示例:**

```python
o1.set_waveform_standard(waveform='sine', frequency=1_000_000, vpp=2.5)
```

---

### `set_waveform_dc(voltage)`

设置直流电压输出。

**参数:**

| 参数 | 类型 | 描述 |
|------|------|------|
| `voltage` | float | 输出直流电压 (Volts) |

**返回:** `(status, response)` 元组

**示例:**

```python
o1.set_waveform_dc(voltage=3)
```

---

### `set_waveform_arbitrary(wave, wave_clk_div=1)`

设置任意波形输出。

**参数:**

| 参数 | 类型 | 默认值 | 描述 |
|------|------|--------|------|
| `wave` | list[float] | - | 电压采样点序列 (Volts)，每个点周期 100ns (10MHz 采样率) |
| `wave_clk_div` | int | 1 | 时钟分频系数 (1-256) |

**返回:** `(status, response)` 元组

**示例:**

```python
o1.set_waveform_arbitrary(wave=[3.2, 3.2, 3.2, 3.2, 3.2, 0.0, 0.0, 0.0, 0.0, 0.0])
```

---

### `set_waveform_from_file(file_path)`

从文件加载波形数据。

**参数:**

| 参数 | 类型 | 描述 |
|------|------|------|
| `file_path` | str | 波形数据文件路径，支持逗号或换行分隔的数值 |

**返回:** `(status, response)` 元组

**示例:**

```python
o1.set_waveform_from_file(file_path=r'C:\Users\Desktop\wav.txt')
```

---

## PWM 输出

### `set_pwm(freq, duty_cycle)`

设置 GP29 引脚的 PWM 输出。

**参数:**

| 参数 | 类型 | 描述 |
|------|------|------|
| `freq` | float \| int | PWM 频率 (Hz) |
| `duty_cycle` | float | 占空比 (0–1) |

**返回:** `(status, response)` 元组

**示例:**

```python
o1.set_pwm(10_000, 0.5)  # 10kHz, 50% 占空比
o1.set_pwm(600, 0.0)     # 关闭
```

---

## LED 显示

### `set_led_text(text, x=0, y=0, auto_wrap=True)`

设置 LED 文本显示。

**参数:**

| 参数 | 类型 | 默认值 | 描述 |
|------|------|--------|------|
| `text` | str | - | 要显示的文本 (ASCII) |
| `x` | int | 0 | X 坐标 (像素) |
| `y` | int | 0 | Y 坐标 (像素)，表示文本基线位置 |
| `auto_wrap` | bool | True | 是否自动换行 |

**示例:**

```python
o1.set_led_text('Hello World!', y=9, x=3)
```

---

### `set_led_image(image_path, x=0, y=0, fit=True)`

设置 LED 图片显示。

**参数:**

| 参数 | 类型 | 默认值 | 描述 |
|------|------|--------|------|
| `image_path` | str | - | 图片文件路径 (PNG, JPEG 等) |
| `x` | int | 0 | X 坐标 (像素) |
| `y` | int | 0 | Y 坐标 (像素) |
| `fit` | bool | True | 是否强制缩放到 64x64 像素 |

**示例:**

```python
o1.set_led_image(r'D:\work\logo_2.png')
```

---

## 开关状态

### `get_switch_status_pl()`

获取 PL 开关状态。

**返回:** `(status, (sw1, sw2))` 元组，sw1/sw2 为 0(断开) 或 1(闭合)

**示例:**

```python
o1.get_switch_status_pl()
```

---

### `get_switch_status_ps()`

获取 PS 开关状态。

**返回:** `(status, (sw1, sw2))` 元组，sw1/sw2 为 0(断开) 或 1(闭合)

**示例:**

```python
o1.get_switch_status_ps()
```

---

## 电压测量

### `get_voltage_a0()`

获取测量点 A0 电压。

**返回:** `(status, voltage)` 元组，voltage 单位为 Volts

**示例:**

```python
print(o1.get_voltage_a0())
```

---

### `get_voltage_a1()`

获取测量点 A1 电压。

**返回:** `(status, voltage)` 元组，voltage 单位为 Volts

**示例:**

```python
print(o1.get_voltage_a1())
```

---

## 数字 GPIO

### `digital_pin_mode(pin_id, mode)`

设置数字 IO 引脚模式。

**参数:**

| 参数 | 类型 | 描述 |
|------|------|------|
| `pin_id` | str | 引脚标识：GP0-GP7, GP21-GP27, A, A2-A5, IO2-IO9 |
| `mode` | int \| str | 模式：1 或 `'INPUT'` = 输入，0 或 `'OUTPUT'` = 输出 |

**返回:** `(status, response)` 元组

**示例:**

```python
o1.digital_pin_mode('a', 1)        # 输入模式
o1.digital_pin_mode('a', 'INPUT')  # 同上
o1.digital_pin_mode('a', 0)        # 输出模式
```

---

### `digital_read(pin_id)`

读取数字 IO 引脚电平状态。

**参数:**

| 参数 | 类型 | 描述 |
|------|------|------|
| `pin_id` | str | 引脚标识 |

**返回:** `(status, level)` 元组，level 为 0(低) 或 1(高)

**示例:**

```python
print(o1.digital_read('a'))
```

---

### `digital_write(pin_id, value)`

设置数字 IO 引脚电平。

**参数:**

| 参数 | 类型 | 描述 |
|------|------|------|
| `pin_id` | str | 引脚标识 |
| `value` | int | 电平：1 = 高，0 = 低 |

**返回:** `(status, response)` 元组

**示例:**

```python
o1.digital_write('a', 1)  # 高电平
```

---

## I2C 通信

### `i2c_config(dev_addr, speed)`

配置 I2C 参数。

**参数:**

| 参数 | 类型 | 描述 |
|------|------|------|
| `dev_addr` | int | 设备地址，如 `0x23` |
| `speed` | serial.I2cSpeed | 速率，如 `serial.I2cSpeed.FAST_400K` |

**返回:** `(status, response)` 元组

**示例:**

```python
from cracknuts.cracker import serial
o1.i2c_config(dev_addr=0x23, speed=serial.I2cSpeed.FAST_400K)
```

---

### `i2c_enable()`

使能 I2C。

**返回:** `(status, response)` 元组

**示例:**

```python
o1.i2c_enable()
```

---

### `i2c_transceive(tx_data, rx_count)`

I2C 发送并接收数据。

**参数:**

| 参数 | 类型 | 描述 |
|------|------|------|
| `tx_data` | str | 发送数据，如 `'01'` |
| `rx_count` | int | 接收字节数 |

**返回:** `(status, response)` 元组

**示例:**

```python
r, v = o1.i2c_transceive(tx_data='21', rx_count=2)
```

---

## SPI 通信

### `spi_config(speed, cpol, cpha, csn_auto=True)`

配置 SPI 参数。

**参数:**

| 参数 | 类型 | 描述 |
|------|------|------|
| `speed` | int | 速率 (Hz)，如 `10000` |
| `cpol` | SpiCpol | 时钟极性，如 `SpiCpol.SPI_CPOL_LOW` |
| `cpha` | SpiCpha | 时钟相位，如 `SpiCpha.SPI_CPHA_HIGH` |
| `csn_auto` | bool | 片选自动模式 |

**返回:** `(status, response)` 元组

**示例:**

```python
from cracknuts.cracker.serial import SpiCpol, SpiCpha
o1.spi_config(speed=10000, cpol=SpiCpol.SPI_CPOL_LOW, cpha=SpiCpha.SPI_CPHA_HIGH, csn_auto=True)
```

---

### `spi_enable()`

使能 SPI。

**返回:** `(status, response)` 元组

**示例:**

```python
o1.spi_enable()
```

---

### `spi_transmit(tx_data, is_trigger)`

SPI 发送数据。

**参数:**

| 参数 | 类型 | 描述 |
|------|------|------|
| `tx_data` | str | 发送数据，如 `'8000'` |
| `is_trigger` | bool | 是否触发采集 |

**返回:** `(status, response)` 元组

**示例:**

```python
o1.spi_transmit(tx, False)
```

---

### `spi_transmit_delay_receive(tx_data, delay, rx_count, is_trigger)`

SPI 发送后延迟接收。

**参数:**

| 参数 | 类型 | 描述 |
|------|------|------|
| `tx_data` | str | 发送数据 |
| `delay` | int | 延迟时间 |
| `rx_count` | int | 接收字节数 |
| `is_trigger` | bool | 是否触发采集 |

**返回:** `(status, response)` 元组

**示例:**

```python
_, rx = o1.spi_transmit_delay_receive(tx_data=tx, delay=1000, rx_count=n, is_trigger=False)
```

---

## UART 通信

### `uart_config(baudrate)`

配置 UART 参数。

**参数:**

| 参数 | 类型 | 描述 |
|------|------|------|
| `baudrate` | Baudrate | 波特率，如 `Baudrate.BAUDRATE_9600` |

**返回:** `(status, response)` 元组

**示例:**

```python
from cracknuts.cracker.serial import Baudrate
o1.uart_config(baudrate=Baudrate.BAUDRATE_9600)
```

---

### `uart_io_enable()`

使能 UART IO。

**返回:** `(status, response)` 元组

**示例:**

```python
o1.uart_io_enable()
```

---

### `uart_transmit_receive(tx_data, rx_count)`

UART 发送并接收数据。

**参数:**

| 参数 | 类型 | 描述 |
|------|------|------|
| `tx_data` | bytes \| str | 发送数据 |
| `rx_count` | int | 接收字节数 |

**返回:** `(status, response)` 元组

**示例:**

```python
o1.uart_transmit_receive(tx_data='s2-500#'.encode(), rx_count=10)
```

---

### `uart_receive_fifo_clear()`

清除 UART 接收 FIFO。

**返回:** `(status, response)` 元组

**示例:**

```python
o1.uart_receive_fifo_clear()
```

---

### `uart_receive(rx_count)`

UART 接收数据。

**参数:**

| 参数 | 类型 | 描述 |
|------|------|------|
| `rx_count` | int | 接收字节数 |

**返回:** `(status, response)` 元组

**示例:**

```python
s, r = o1.uart_receive(rx_count=10)
```

---

## 采集面板

### `cn.simple_acq(cracker)`

创建简单采集对象。

**参数:**

| 参数 | 类型 | 描述 |
|------|------|------|
| `cracker` | CrackerO1 | Cracker 设备对象 |

**返回:** Acquisition 对象

**示例:**

```python
acq = cn.simple_acq(o1)
```

---

### `cn.show_panel(acq)`

显示采集控制面板。

**参数:**

| 参数 | 类型 | 描述 |
|------|------|------|
| `acq` | Acquisition | 采集对象 |

**示例:**

```python
cn.show_panel(acq)
```

---

## 返回值说明

大多数方法返回 `(status, response)` 元组：

- `status` - 协议响应状态码，`0` 表示成功
- `response` - 响应数据，可能为 `None`、`bytes`、`int` 或其他类型
