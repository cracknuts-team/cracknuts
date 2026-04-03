# CrackerO1 基础使用示例

本示例演示 CrackerO1 设备的基础使用，包括连接、波形控制、PWM、GPIO 控制、传感器和 EDU 开发板功能等。
需要在 `jupyter` 的 `notebook` 中使用。

> **重要说明**：
> - **连接设备**是执行其他所有功能的前提，必须**首先执行**。
> - 其余各功能模块之间**没有先后顺序关系**，每个代码块都是独立的使用示例，可根据需要选择性执行。

## SDK Compatibility

这些示例适用于：CrackNuts Host SDK **0.21.x**

---

## 连接设备

```python
import cracknuts as cn
```

```python
o1 = cn.cracker_o1('192.168.0.247')  # 这里的IP地址需要替换成目标设备的IP地址
o1.connect(force_update_bin=True, force_write_default_config=True) # 连接设备，并强制更新固件和写入默认配置
```

---

## 数字 GPIO 控制

### 基础操作说明

**功能说明：**
- 演示使用 CrackerO1 的数字接口功能
- pin_id 参数为板子上的丝印名称
- 可配置为输入（1）或输出（0）模式
- 输出高电平时，引脚电压为 3.3V

### 配置为输入模式并读取

```python
# 首先，配置一个数字引脚（例：'a'）为输入模式，然后读取该引脚的状态。
# 如果外部输入高电平，应该打印出1。
o1.digital_pin_mode('a', 1)
print(o1.digital_read('a'))
```

### 配置为输出模式并设置电平

```python
# 接下来，将该引脚配置为输出模式，并设置为高电平，这时测量该引脚的电压应该为3.3V。
o1.digital_pin_mode('a', 0)
o1.digital_write('a', 1)
```

---

## 波形发生器控制（DAC）

### 标准波形说明

**功能说明：**
- 演示如何使用 CrackerO1 的 DAC 功能生成各种标准波形信号
- 每个采样点的值表示 DAC 输出的电压水平
- 相同的参数配置会产生相应的波形

### 正弦波

```python
# 设置频率为8MHz，峰峰值为1.5V，偏置为2V，初相位为0.3
# 这将使DAC输出一个符合这些参数的正弦波信号。
o1.set_waveform_sine(frequency='8m', vpp=1.5, offset=2, phase=0.3)
```

### 方波

```python
# 设置频率为100kHz，峰峰值为1.5V，占空比为80%，偏置为2V
# 这将使DAC输出一个符合这些参数的方波信号。
o1.set_waveform_square(frequency='100k', vpp=1.5, duty=0.8, offset=2)
```

### 三角波

```python
# 设置频率为2MHz，峰峰值为1.6V，偏置为0.8V
# 这将使DAC输出一个符合这些参数的三角波信号。
o1.set_waveform_triangle(frequency='2m', vpp=1.6, offset=0.8)
```

### 锯齿波

```python
# 设置频率为1MHz，峰峰值为2V，偏置为1V，上升沿斜率为0（表示上升沿垂直）
# 这将使DAC输出一个符合这些参数的锯齿波信号。
o1.set_waveform_sawtooth(frequency='1m', vpp=2, offset=1, slope=0)
```

### DC 电平

```python
# 设置输出电压为3V
o1.set_waveform_dc(voltage=3)
```

### 通用波形设置

```python
# 使用基础方法 set_waveform_standard 来设置一个标准波形
# 该方法也是上述 set_waveform_sine、set_waveform_square、set_waveform_triangle 和 set_waveform_sawtooth 方法的底层实现
# 适用于需要更灵活控制波形参数的场景
o1.set_waveform_standard(waveform='sine', frequency=1_000_000, vpp=2.5)
```

### 任意波形说明

**功能说明：**
- 演示如何使用 CrackerO1 的 DAC 功能生成任意波形信号
- 传入一个包含采样点的波形数据列表
- 每个采样点的值表示 DAC 输出的电压水平
- 采样点将被 DAC 按照一定的时间间隔依次输出

### 任意波形列表

```python
# 设置一个包含40个采样点的波形
# 周期为 40*6.25ns（即250ns），频率为4MHz
# 前20个采样点为3.2V，后20个采样点为0.0V（方波）
o1.set_waveform_arbitrary(
    wave=[
    3.2, 3.2, 3.2, 3.2, 3.2, 3.2, 3.2, 3.2, 3.2, 3.2, 3.2, 3.2, 3.2, 3.2, 3.2, 3.2, 3.2, 3.2, 3.2, 3.2,
    0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0
])
```

### 从文件加载波形

```python
# 演示如何从文件中加载一个波形数据
# 该文件应该包含一系列数值，每个数值表示DAC输出的电压
# 例如：2.5, 2.6, 2.7, ...
# 这些数值将被DAC按照一定的时间间隔依次输出
o1.set_waveform_from_file(file_path=r'wav.txt')
```

---

## 电压测量

```python
# 演示了如何获取CrackerO1的电压信息
# CrackerO1提供了两个方法 get_voltage_a0 和 get_voltage_a1
# 分别用于获取a0和a1引脚的电压值
o1.get_voltage_a0()
o1.get_voltage_a1()
```

---

## 开关状态查询

```python
# 演示了如何获取CrackerO1的开关状态
# CrackerO1上有两组四个开关，分别是pl和ps
# 通过调用 get_switch_status_pl 和 get_switch_status_ps 方法获取开关的当前状态
o1.get_switch_status_pl() # 这将返回pl的两个开关的状态
o1.get_switch_status_ps() # 这将返回ps的两个开关的状态
```

---

## 64x64 LED HUB75 点阵屏显示

**硬件连接要求：**
- LED 屏必须已经连接到 CrackerO1 的 HUB75 接口
- 电源必须正确连接

### 显示文本

```python
# 演示led显示，利用CrackerO1板载的 HUB75 接口控制一块 64x64 的 LED 点阵屏
# 使用 set_led_text 方法在LED屏上显示文本 "Hello World!"
# 参数 y=9, x=3 指定文本的位置
o1.set_led_text('Hello World!', y=9, x=3)
```

### 显示图片

```python
# 使用 set_led_image 方法在LED屏上显示一张图片
# 图片路径需要替换为实际的图片文件路径
o1.set_led_image(r'D:\work\10.document\01.CrackNuts\网站相关内容\logo_2.png')
```

---

## 采集面板（示波器功能）

**功能说明：**
- 演示如何使用CrackerO1的示波器功能来采集和显示波形数据
- 创建一个简单的采集对象后，使用 show_panel 方法将其显示在面板上
- 可以查看 cha 和 chb 的波形数据

```python
acq = cn.simple_acq(o1)
cn.show_panel(acq)
```

---

## PWM 输出

### 风扇控制

**功能说明：**
- 演示如何使用CrackerO1的PWM功能来控制一个「风扇」
- 通过控制占空比来调整风扇的转速
- 占空比越大，风扇转速越快；占空比越小，风扇转速越慢

**硬件连接说明：**
- 风扇模块的VCC引脚应该连接到CMOS开关组的POW_O1上
- 风扇模块的PWM引脚应该连接到gpio29引脚，接收来自CrackerO1的PWM信号
- CMOS开关组的POW_I1引脚应该连接到dc12v引脚
- CMOS开关组的POW_EN1引脚应该连接到gp1引脚，通过控制该引脚来开关风扇电源

```python
# 设置频率为10kHz，占空比为50%
o1.set_pwm(10_000, 0.5)
```

### 电机控制

**功能说明：**
- 演示如何使用CrackerO1的PWM功能来控制一个「电机」
- 可以通过设置频率来控制电机的转速
- 设置占空比为0%可以让电机停止转动

**硬件连接说明：**
- 电机模块的VCC引脚应该连接到CMOS开关组的POW_O1上
- CMOS开关组的POW_I1引脚应该连接到DC12V引脚
- CMOS开关组的POW_EN1引脚应该连接到gp1引脚，通过控制该引脚来开关电机电源
- 电机模块的PWM引脚应该连接到gpio29引脚，接收来自CrackerO1的PWM信号

```python
o1.digital_pin_mode('gp1', 0) # 将gp1引脚配置为输出模式
o1.digital_write('gp1', 1)    # 将gp1引脚设置为高电平，开启电机
o1.set_pwm(600, 0.5)          # 设置频率为600Hz，占空比为50%
```

---

## EDU 开发板功能

> EDU 开发板上定义了一些用于学习的测试电路，这些电路可以通过CrackerO1的GPIO引脚进行交互和控制。主要包括以下模块：
> 1. LED 红绿灯组 - 用来学习状态机和数字输出控制
> 2. 七段数码管 - 使用8个GPIO引脚控制显示，学习数字显示和编码
> 3. 按键输入 - 使用GPIO引脚读取按键状态，学习数字输入和事件触发
> 4. LED 灯珠 - 使用GPIO引脚控制亮灭，学习基本数字输出控制和PWM调光
> 5. 风扇和电机 - 使用GPIO引脚输出PWM信号来控制转速
> 6. LED 流水灯 - 使用GPIO引脚控制一组LED灯珠形成流水效果
> 7. LED 8x8点阵屏 - 使用3个GPIO引脚控制显示
> 8. UART距离传感器 - 使用UART协议进行串行通信
> 9. SPI温度传感器 - 使用SPI协议进行通信
> 10. I2C光线传感器 - 使用I2C协议进行通信
> 11. CMOS开关 - 控制各电路的连接状态和电源开关

### 七段数码管显示

**功能说明：**
- 演示如何使用CrackerO1的数字接口功能来控制EDU开发板上的一个七段数码管显示数字
- 定义七段数码管的引脚连接，配置这些引脚为输出模式
- 定义数字到七段显示的映射关系（digit_map），其中0表示点亮，1表示不点亮
- 循环显示0到9的数字，每个数字显示1秒钟，之后关闭显示并让小数点闪烁

**硬件连接说明：**
- EDU开发板上应该把14pin排线连接到七段数码管模块的控制引脚上

**引脚定义：**
- GPIO_A = 'GP5', GPIO_B = 'GP4', GPIO_C = 'GP7', GPIO_D = 'GP6'
- GPIO_E = 'GP22', GPIO_F = 'GP21', GPIO_G = 'GP24', GPIO_DP = 'GP23'

**显示映射（0表示点亮，1表示不点亮）：**
- 0: 0b0000001, 1: 0b1001111, 2: 0b0010010, 3: 0b0000110, 4: 0b1001100
- 5: 0b0100100, 6: 0b0100000, 7: 0b0001111, 8: 0b0000000, 9: 0b0000100

```python
import time

GPIO_A = 'GP5'
GPIO_B = 'GP4'
GPIO_C = 'GP7'
GPIO_D = 'GP6'
GPIO_E = 'GP22'
GPIO_F = 'GP21'
GPIO_G = 'GP24'
GPIO_DP = 'GP23'

o1.digital_pin_mode(GPIO_A, 'OUTPUT')
o1.digital_pin_mode(GPIO_B, 'OUTPUT')
o1.digital_pin_mode(GPIO_C, 'OUTPUT')
o1.digital_pin_mode(GPIO_D, 'OUTPUT')
o1.digital_pin_mode(GPIO_E, 'OUTPUT')
o1.digital_pin_mode(GPIO_F, 'OUTPUT')
o1.digital_pin_mode(GPIO_G, 'OUTPUT')
o1.digital_pin_mode(GPIO_DP, 'OUTPUT')

# 低电平亮
digit_map = {
    0: 0b0000001,
    1: 0b1001111,
    2: 0b0010010,
    3: 0b0000110,
    4: 0b1001100,
    5: 0b0100100,
    6: 0b0100000,
    7: 0b0001111,
    8: 0b0000000,
    9: 0b0000100,
    -1: 0b11111111
}

pins = [
    GPIO_A,
    GPIO_B,
    GPIO_C,
    GPIO_D,
    GPIO_E,
    GPIO_F,
    GPIO_G,
]

def display_digit(n):
    value = digit_map[n]

    for i, pin in enumerate(pins):
        bit = (value >> (6 - i)) & 1
        o1.digital_write(pin, bit)

    # 小数点默认关闭（高电平）
    o1.digital_write(GPIO_DP, 1)

for i in range(10):
    display_digit(i)
    time.sleep(1)

# 关闭数字显示
display_digit(-1)

# 闪烁
for i in range(10):
    o1.digital_write(GPIO_DP, i%2)
    time.sleep(0.1)
```

### 红绿灯控制

**功能说明：**
- 演示如何使用CrackerO1的数字接口功能来控制EDU开发板上的红绿灯模块
- 定义红绿灯的引脚连接（分为东、南、西、北四个方向），配置这些引脚为输出模式
- 循环点亮每个灯，持续0.5秒钟，然后关闭它，最后再次调用 all_off 函数确保所有灯都关闭

**硬件连接说明：**
- EDU开发板上应该把14pin排线连接到红绿灯模块的控制引脚上

**引脚定义：**
- 东：E_RED = 'GP26', E_GREEN = 'GP27', E_YELLOW = 'GP28'
- 南：S_GREEN = 'GP24', S_YELLOW = 'GP25', S_RED = 'GP23'
- 西：W_RED = 'GP7', W_GREEN = 'GP21', W_YELLOW = 'GP22'
- 北：N_RED = 'GP4', N_YELLOW = 'GP6', N_GREEN = 'GP5'

```python
import time

# 东
E_RED = 'GP26'
E_GREEN = 'GP27'
E_YELLOW = 'GP28'

# 南
S_GREEN = 'GP24'
S_YELLOW = 'GP25'
S_RED = 'GP23'

# 西
W_RED = 'GP7'
W_GREEN = 'GP21'
W_YELLOW = 'GP22'

# 北
N_RED = 'GP4'
N_YELLOW = 'GP6'
N_GREEN = 'GP5'


# 设置 GPIO 模式
pins = [
    E_RED, E_YELLOW, E_GREEN,
    S_YELLOW, S_GREEN, S_RED,
    W_RED, W_YELLOW, W_GREEN,
    N_RED, N_YELLOW, N_GREEN
]

for p in pins:
    o1.digital_pin_mode(p, 'OUTPUT')


def all_off():
    for p in pins:
        o1.digital_write(p, 1)


all_off()
for _ in range(5):
    for p in pins:
        o1.digital_write(p, 0)
        time.sleep(0.5)
        o1.digital_write(p, 1)
all_off()
```

### LED 流水灯

**功能说明：**
- 演示如何使用CrackerO1的数字接口功能来控制EDU开发板上的流水灯模块，形成一个流水灯效果
- 定义LED灯珠的引脚连接，配置这些引脚为输出模式
- 循环点亮每个灯：从左到右、从右到左、两端向中间、中间向两端等多种方式显示

**硬件连接说明：**
- EDU开发板上应该把14pin排线连接到流水灯模块的控制引脚上

**引脚对应：**
- 'GP4' (D8), 'GP5' (D9), 'GP6' (D10), 'GP7' (D11)
- 'GP21' (D12), 'GP22' (D13), 'GP23' (D14), 'GP24' (D15)

**逻辑说明：**
- 0 = 亮，1 = 灭（低电平有效）

```python
import time

# LED 引脚 (GPIOXX -> GPXX)
LED_PINS = [
    'GP4',   # D8
    'GP5',   # D9
    'GP6',   # D10
    'GP7',   # D11
    'GP21',  # D12
    'GP22',  # D13
    'GP23',  # D14
    'GP24',  # D15
]

# 初始化 GPIO
for p in LED_PINS:
    o1.digital_pin_mode(p, 'OUTPUT')
    o1.digital_write(p, 1)   # 默认灭 (1=灭)


def all_off():
    for p in LED_PINS:
        o1.digital_write(p, 1)


def light(index):
    all_off()
    o1.digital_write(LED_PINS[index], 0)  # 0 = 亮


# 循环运行
for _ in range(2):

    # 左 -> 右
    for i in range(8):
        light(i)
        time.sleep(0.15)

    # 右 -> 左
    for i in range(7, -1, -1):
        light(i)
        time.sleep(0.15)

    # 两端 -> 中间
    for i in range(4):
        all_off()
        o1.digital_write(LED_PINS[i], 0)
        o1.digital_write(LED_PINS[7-i], 0)
        time.sleep(0.2)

    # 中间 -> 两端
    for i in range(3, -1, -1):
        all_off()
        o1.digital_write(LED_PINS[i], 0)
        o1.digital_write(LED_PINS[7-i], 0)
        time.sleep(0.2)

all_off()
```

### LED 灯珠

**功能说明：**
- 演示如何使用CrackerO1的数字接口功能来控制EDU开发板上的LED灯珠，形成闪烁效果
- 实现快速闪烁、慢速闪烁、渐进式加速闪烁等多种效果
- 结束后保持LED熄灭

**硬件连接说明：**
- LED灯珠的VCC引脚应该连接到CMOS开关组的POW_O1上
- CMOS开关组的POW_I1引脚应该连接到DC12V引脚
- CMOS开关组的POW_EN1引脚应该连接到gp1引脚，通过控制该引脚的高低电平来控制LED灯珠的电源开关

```python
import time

LED_GPIO = 'GP1'

o1.digital_pin_mode(LED_GPIO, 'OUTPUT')


def on():
    o1.digital_write(LED_GPIO, 1)  # 亮


def off():
    o1.digital_write(LED_GPIO, 0)  # 灭


# 整个效果循环 3 次
for _ in range(1):

    # 快速闪三下
    for _ in range(3):
        on()
        time.sleep(0.15)
        off()
        time.sleep(0.15)

    time.sleep(0.4)

    # 慢闪两下
    for _ in range(2):
        on()
        time.sleep(0.5)
        off()
        time.sleep(0.5)

    time.sleep(0.6)

    # 渐快闪烁
    delays = [0.5, 0.4, 0.3, 0.2, 0.1]

    for d in delays:
        on()
        time.sleep(d)
        off()
        time.sleep(d)

# 结束后保持熄灭
off()
```

### 按钮

**功能说明：**
- 演示如何使用CrackerO1的数字接口功能来读取EDU开发板上的按键状态
- 定义按键的引脚连接，配置这些引脚为输入模式
- 进入一个循环，在60秒内持续读取按键状态，打印出每个按键是被按下还是未按下的状态
- 使用 clear_output 来清除之前的输出，每次更新按键状态时只显示最新的状态信息

**按键逻辑说明：**
- 按键通常是「低电平有效」的
- 按键被按下时，GPIO引脚被拉低（0）
- 按键未被按下时，引脚保持高电平（1）

**引脚定义：**
- BTN1 = 'GP3', BTN2 = 'GP2', BTN3 = 'GP1', BTN4 = 'GP0'

```python
import time
from IPython.display import clear_output

# 按键 GPIO
BTN1 = 'GP3'
BTN2 = 'GP2'
BTN3 = 'GP1'
BTN4 = 'GP0'

BUTTONS = [BTN1, BTN2, BTN3, BTN4]
BUTTON_NAMES = ['BTN1', 'BTN2', 'BTN3', 'BTN4']

# 初始化输入模式
for btn in BUTTONS:
    o1.digital_pin_mode(btn, 'INPUT')

start_time = time.time()
while time.time() - start_time < 60:
    clear_output(wait=True)
    for i, btn in enumerate(BUTTONS):
        r, val = o1.digital_read(btn)
        print(f"button {btn} value {'按下' if not val else '未按'}")
    time.sleep(0.05)  # 50ms 检测一次
```

### I2C 光照传感器

**功能说明：**
- 演示如何使用CrackerO1的I2C功能来读取EDU开发板上的光线传感器数据
- 初始化光线传感器，然后持续读取40次光照值

**I2C配置说明：**
- 设备地址：0x23
- 通信速度：FAST_400K

```python
from IPython.display import clear_output
import time
from cracknuts.cracker import serial

o1.i2c_config(dev_addr=0x23, speed=serial.I2cSpeed.FAST_400K)
o1.i2c_enable()
# 初始化光线感应器
o1.i2c_transceive(tx_data='01', rx_count=1)
o1.i2c_transceive(tx_data='10', rx_count=0)

# 读取数值

for _ in range(40):
    clear_output(wait=True)
    r, v = o1.i2c_transceive(tx_data='21', rx_count=2)
    if v and len(v) == 2:
        raw_value = (v[0] << 8) | v[1]
        print(f"{(raw_value / 1.2):.2f} lx")
    time.sleep(0.5)
```

### SPI 温度传感器

**功能说明：**
- 演示如何使用CrackerO1的SPI功能来读取EDU开发板上的温度传感器数据
- 温度传感器芯片为 MAX31856

**SPI配置说明：**
- MAX31856 需要使用 SPI 模式 1（CPOL_LOW, CPHA_HIGH）
- 寄存器地址及掩码：
  - CR0 = 0x00（控制寄存器0）
  - CR1 = 0x01（控制寄存器1）
  - LTCBH = 0x0C（温度数据寄存器高字节）
  - WRITE = 0x80, READ = 0x7F

**工作流程：**
1. 停止转换：`write_reg(CR0, 0x00)`
2. 配置为K型热电偶 + 4倍采样平均：`write_reg(CR1, 0x20 | 0x03)`
3. 启动自动转换 + 50Hz滤波：`write_reg(CR0, 0x80 | 0x01)`
4. 读取三个字节数据，右移5位，处理符号位后乘以0.0078125得到温度

```python
from cracknuts.cracker.serial import SpiCpol, SpiCpha
import time
from IPython.display import clear_output

# device
spi = o1

# SPI init (MAX31856 requires SPI Mode 1)
spi.spi_config(
    speed=10000,
    cpol=SpiCpol.SPI_CPOL_LOW,
    cpha=SpiCpha.SPI_CPHA_HIGH,
    csn_auto=True
)
spi.spi_enable()

# registers
CR0 = 0x00
CR1 = 0x01
LTCBH = 0x0C

# SPI command masks
WRITE = 0x80
READ  = 0x7F


def write_reg(reg, val):
    addr = reg | WRITE
    tx = f"{addr:02x}{val:02x}"
    spi.spi_transmit(tx, False)


def read_regs(reg, n):
    addr = reg & READ
    tx = f"{addr:02x}"
    _, rx = spi.spi_transmit_delay_receive(tx_data=tx, delay=1000, rx_count=n, is_trigger=False)
    return rx


def init():
    # stop conversion
    write_reg(CR0, 0x00)

    # K-type thermocouple + 4 sample average
    write_reg(CR1, 0x20 | 0x03)

    # auto conversion + 50Hz filter
    write_reg(CR0, 0x80 | 0x01)


def read_temp():
    b1, b2, b3 = read_regs(LTCBH, 3)

    v = (b1 << 16) | (b2 << 8) | b3
    v >>= 5

    if v & 0x40000:
        v |= 0xFFF80000

    return v * 0.0078125


# run
init()

for i in range (40):
    clear_output(wait=True)
    t = read_temp()
    print(f"{t:.2f} °C")
    time.sleep(0.5)
```

### UART 距离传感器

**功能说明：**
- 演示如何使用CrackerO1的UART功能来读取EDU开发板上的距离传感器数据
- 设置传感器的发送周期为500ms，然后持续读取20次距离值

**UART配置说明：**
- 波特率：9600

```python
from cracknuts.cracker.serial import Baudrate
from IPython.display import clear_output

o1.uart_config(baudrate=Baudrate.BAUDRATE_9600)
o1.uart_io_enable()

# 设置发送周期为 500ms
o1.uart_transmit_receive(tx_data='s2-500#'.encode(), rx_count=10)

for _ in range(20):
    clear_output(wait=True)
    o1.uart_receive_fifo_clear()
    s, r = o1.uart_receive(rx_count=10)
    v = r.decode().split('\r\r\n')
    print(f"The distance is {v[0]}")
    time.sleep(0.5)
```

### LED 8x8 点阵屏

#### Jupyter 版本说明

**功能说明：**
- 演示如何使用CrackerO1的数字接口功能来控制EDU开发板上的LED 8x8点阵屏显示图案
- 定义点阵屏的引脚连接，配置这些引脚为输出模式
- 定义 shift_bit 和 shift_16bit 函数，用于将数据通过串行方式发送到点阵屏的控制芯片（通常是74HC595或类似的移位寄存器）
- shift_16bit 函数中，高8位控制行，低8位控制列

**硬件连接说明：**
- EDU开发板上应该把14pin排线连接到led 8x8矩阵模块的控制引脚上

**重要说明：**
- 由于上位机与点阵屏之间的通信频率较低，在Jupyter中运行不会形成稳定的图像显示
- 这里只是演示了数据发送的方式
- 如需稳定显示，请参考下一部分「设备上执行版本」的示例

**引脚定义：**
- DATA = "GP4", CLK = "GP6", LATCH = "GP5"

```python
import time

DATA = "GP4"
CLK = "GP6"
LATCH = "GP5"

def led595_init():
    o1.digital_pin_mode(DATA, "OUTPUT")
    o1.digital_pin_mode(CLK, "OUTPUT")
    o1.digital_pin_mode(LATCH, "OUTPUT")
    o1.digital_write(DATA, 0)
    o1.digital_write(CLK, 0)
    o1.digital_write(LATCH, 0)

def shift_bit(bit):
    o1.digital_write(DATA, bit)
    o1.digital_write(CLK, 1)
    o1.digital_write(CLK, 0)

def shift_16bit(value):
    for i in range(15, -1, -1):
        shift_bit((value >> i) & 1)
    o1.digital_write(LATCH, 1)
    o1.digital_write(LATCH, 0)


def display_matrix(matrix, t):
    s = time.time()
    while True:
        if time.time() -s > t:
            return
        s = time.time()
        for row in range(8):
            data = matrix[row]          # 列数据
            row_sel = 1 << row          # 行选择

            # 高8位控制行，低8位控制列
            value = (row_sel << 8) | data
            _s = time.time()
            shift_16bit(value)
        time.sleep(0.001)           # 矩阵扫描延时


# 显示矩阵图(频率较低，效果为逐行扫描）
display_matrix(
    [
        0b00000000,
        0b00000000,
        0b00000000,
        0b00000000,
        0b00000000,
        0b00000000,
        0b00000000,
        0b00000000,
    ], 2
)
```

#### 设备上执行版本说明

**重要说明：**
- 这段代码需要保存到文件当中，然后通过CrackerO1的文件传输功能将其上传到设备上
- 最后在CrackerO1的Python环境中执行该文件来运行代码
- 这样可以直接访问AXI寄存器来控制GPIO引脚，从而实现对LED点阵屏的稳定显示
- **不是在本地jupyter环境中运行的，而是要保存成一个.py文件上传到CrackerO1设备上运行的**

**AXI寄存器说明：**
- BASE_ADDR = 0x43C10000（AXI基地址）
- GPIO_DIR_OFFSET = 0x194C（GPIO方向寄存器，0=输出，1=输入）
- GPIO_OUT_OFFSET = 0x1950（GPIO输出寄存器，0=低，1=高）

**第一部分：创建 8x8led.py 文件**

保存以下内容为 `8x8led.py`：

```python
import time
import os
import mmap
import struct

class Axi:
    """AXI 内存映射访问类，用于直接读写 AXI 寄存器"""

    AXI_PATH = "/dev/mem"

    def __init__(self, base_addr: int, size: int):
        self.base_addr = base_addr
        self.size = size

        self.fd = os.open(self.AXI_PATH, os.O_RDWR | os.O_SYNC)

        self.mem = mmap.mmap(
            self.fd,
            size,
            mmap.MAP_SHARED,
            mmap.PROT_READ | mmap.PROT_WRITE,
            offset=base_addr
        )

    def read_register(self, offset: int) -> int:
        if offset >= self.size:
            raise ValueError(
                f"AXI invalid offset {offset}, total size: {self.size}"
            )

        data = self.mem[offset:offset+4]
        return struct.unpack("<I", data)[0]

    def write_register(self, offset: int, value: int):
        if offset >= self.size:
            raise ValueError(
                f"AXI invalid offset {offset}, total size: {self.size}"
            )

        self.mem[offset:offset+4] = struct.pack("<I", value)



# AXI 基地址
BASE_ADDR = 0x43C10000
SIZE = 0x10000

# GPIO 寄存器偏移
GPIO_DIR_OFFSET = 0x194C
GPIO_OUT_OFFSET = 0x1950

# GPIO 对应位
GP4 = 4
GP5 = 5
GP6 = 6

# 初始化 AXI
axi = Axi(BASE_ADDR, SIZE)

# GPIO 模拟 digital_pin_mode / digital_write
def pin_mode(bit: int, mode: str):
    """设置 GPIO 模式"""
    dir_val = axi.read_register(GPIO_DIR_OFFSET)
    if mode.upper() == "OUTPUT":
        dir_val &= ~(1 << bit)
    else:
        dir_val |= (1 << bit)
    axi.write_register(GPIO_DIR_OFFSET, dir_val)

def digital_write(bit: int, value: int):
    """设置 GPIO 电平"""
    out_val = axi.read_register(GPIO_OUT_OFFSET)
    if value:
        out_val |= (1 << bit)
    else:
        out_val &= ~(1 << bit)
    axi.write_register(GPIO_OUT_OFFSET, out_val)


# 初始化 595
def led595_init():
    for bit in [GP4, GP5, GP6]:
        pin_mode(bit, "OUTPUT")
        digital_write(bit, 0)

def shift_bit(bit):
    digital_write(GP4, bit)
    digital_write(GP6, 1)
    digital_write(GP6, 0)

def shift_16bit(value):
    for i in range(15, -1, -1):
        shift_bit((value >> i) & 1)
    digital_write(GP5, 1)
    digital_write(GP5, 0)


def display_matrix(matrix, t):
    s = time.time()
    while True:
        if time.time() - s > t:
            return
        s = time.time()
        for row in range(8):
            data = matrix[row]
            row_sel = 1 << row
            value = (row_sel << 8) | data
            shift_16bit(value)
        time.sleep(0.001)


if __name__ == "__main__":
    led595_init()
    digits = {
        0: [0b11000011, 0b10111101, 0b10011101, 0b10101101, 0b10110101, 0b10111001, 0b10111101, 0b11000011],
        1: [0b11100111, 0b11100011, 0b11100111, 0b11100111, 0b11100111, 0b11100111, 0b11100111, 0b10000001],
        2: [0b11000011, 0b10111101, 0b10111111, 0b11011111, 0b11110111, 0b11111011, 0b11101111, 0b10000001],
        3: [0b11000011, 0b10111101, 0b10111111, 0b11000111, 0b10111111, 0b10111111, 0b10111101, 0b11000011],
        4: [0b11011111, 0b11001111, 0b11010111, 0b11011011, 0b11011101, 0b10000001, 0b11011111, 0b11011111],
        5: [0b10000001, 0b11111101, 0b11111101, 0b11000001, 0b10111111, 0b10111111, 0b10111101, 0b11000011],
        6: [0b11000011, 0b10111101, 0b11111101, 0b11000001, 0b10111101, 0b10111101, 0b10111101, 0b11000011],
        7: [0b10000001, 0b10111111, 0b11011111, 0b11101111, 0b11110111, 0b11111011, 0b11111101, 0b11111101],
        8: [0b11000011, 0b10111101, 0b10111101, 0b11000011, 0b10111101, 0b10111101, 0b10111101, 0b11000011],
        9: [0b11000011, 0b10111101, 0b10111101, 0b10000011, 0b10111111, 0b10111111, 0b10111101, 0b11000011]
    }
    for i in range(10):
        display_matrix(digits[i], 2)
    display_matrix([0b11111111] * 9, 1)
```

**第二部分：从 Jupyter 上传并执行脚本**

```python
# 将本地的 8x8led.py 文件上传到 CrackerO1 设备的 /tmp 目录下
o1.shell.upload("8x8led.py", "/tmp/8x8led.py")

# 在 CrackerO1 设备上执行上传的脚本
o1.shell.run("python3 /tmp/8x8led.py")
```

---

## 寄存器操作

### 写入寄存器

```python
o1.register_write(base_address=0x43c10000, offset=0x1810, data=4)
o1.register_write(base_address=0x43c10000, offset=0x1814, data=4)
```

### 启动控制

```python
o1.register_write(base_address=0x43c10000, offset=0x180c, data=1)
```

### 读取寄存器

```python
v = o1.register_read(base_address=0x43c10000, offset=0x180c)[1]
print(int.from_bytes(v))
```

---

## UART 通信

```python
from cracknuts.cracker import serial

# 配置 UART 参数
o1.uart_config(baudrate=serial.Baudrate.BAUDRATE_115200)
o1.uart_io_enable()
```

```python
# 发送并接收数据
o1.uart_transmit_receive(tx_data='11 22 33 44', rx_count=4)[1].hex(' ')
```

```python
# 禁用 UART IO
o1.uart_io_disable()
```

---

## SPI 通信

```python
from cracknuts.cracker import serial

# 配置 SPI
o1.spi_config(1000, cpha=serial.SpiCpha.SPI_CPHA_HIGH, cpol=serial.SpiCpol.SPI_CPOL_HIGH)
o1.spi_enable()
```

```python
# SPI 发送接收
o1.spi_transceive(tx_data='11 22 33 44', rx_count=4)
```

```python
# 禁用 SPI
o1.spi_disable()
```
