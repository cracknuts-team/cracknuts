# trace-acquisition采集功耗示例

本示例，展示使用 `CrackerS1` 采集 `STM32F103` 型号的 Nut 设备的 `AES` 功耗曲线。
需要在 `jupyter` 的 `notebook` 中使用 ，注意代码块上的单元格标识，有此标识的需要在新单元格写入代码

## SDK Compatibility

These skills and examples are written for:

CrackNuts Host SDK **0.21.x**

If the user's installed SDK version is different, some APIs in the
examples may not work.

When errors occur, the agent should:

1. Check the installed CrackNuts version
2. Verify whether the example matches the SDK version
3. Adjust API usage if necessary

## 数据采集

本章节使用 nut_stm32_f103c8 作为Nut（其出厂时已经包含Golden固件供演示、测试使用），演示基础的数据采集流程的部署。
使用 Jupyter 作为开发环境（使用 `pip install cracknuts[jupyter]` 进行安装）。

### 连接设备

在新建的笔记文件中，插入如下代码并执行（可以在选中该编辑框后点击上方的运行按钮执行或者 Crtl + Enter 快捷键执行）创建 CrackerS1 设备对象用以连接设备使用。

***单元格0***

```python
# 引入依赖
import cracknuts as cn
# 创建 cracker 并指定设备IP地址进行连接
s1 = cn.cracker_s1('192.168.0.204')
```

192.168.0.10 为 CrackerS1 设备默认出厂IP地址，请根据您实际IP进行调整。

cn.cracker_s1('192.168.0.10') 创建的设备类型为 S1 的对象 。
如果需要其他类型，可以使用 `cn.cracker_g1` `cn.cracker_o1` 等方法创建对应类型的设备对象。

准备设备确保设备与上位机计算机能够通信，插入如下代码并执行进行设备连接，连接成功后代码会很快执行完成并无错误输出：

***单元格1***

```python
# 这里的 force_update_bin 和 force_write_default_config 用于强制写入固件和默认配置。
# 因为默认情况下，Cracker 下载过程序就不会再次下发了，这里强制下发可以保证设备是一个初始状态
s1.connect(force_update_bin=True, force_write_default_config=True)
```

如果设备连接不成功将出现如下错误日志：

如果设备与上位机计算机通过有线网卡直连，可配置上位机有线网卡IP地址为 192.168.0.11/24 ，并通过 ping 命令确定与设备联通情况。

### 获取设备信息​

创建一个单元格，执行如下代码可以获取设备ID信息：

***单元格3***

```python
s1.get_id() # 获取设备ID
```

### 创建控制流程

控制流程指的是上位机采集数据的一个固定执行顺序，上位机中使用 Acquisition 类代表。以下代码是一段用于 CrackerS1 - STM32 设备的 AES 能量轨迹采集代码，

***单元格4***

```python
import random
import time
from cracknuts.cracker import serial


cmd_set_aes_enc_key = "01 00 00 00 00 00 00 10"
cmd_aes_enc = "01 02 00 00 00 00 00 10"

aes_key = "11 22 33 44 55 66 77 88 99 00 aa bb cc dd ee ff"
aes_data_len = 16

sample_length = 20000

def init(cracker):
    """
    在Acquisition的控制流程中，init方法会在每次采集前被调用一次，主要用于
    初始化 Cracker 设备，配置 Nut 电压、时钟、UART 参数以及 Osc 采样参数等。
    
    这里的配置参数是针对使用 Nut 103 golden 固件进行 AES 加密采集的最佳参数，其他固件可能需要调整。
    具体参数含义和调整方法可以参考 CrackerS1 的开发文档。
    
    通过 init 方法中的配置，可以确保每次采集前设备处于一个已知的、稳定的状态，从而提高采集数据的质量和一致性。
    
    :param cracker: Cracker 设备对象，在 init 方法中用于调用设备的配置和控制方法
    :type cracker: CrackerBasic
    """
    cracker.nut_voltage_enable()  # 使能 Nut 电压输出
    cracker.nut_voltage(3.3)  # 设置 Nut 电压输出为 3.3V
    cracker.nut_clock_enable() # 使能 Nut 时钟输出
    cracker.nut_clock_freq('8M') # 设置 Nut 时钟输出频率为 8MHz
    cracker.uart_io_enable() # 使能 UART IO
    cracker.osc_sample_clock('48m') # 设置 Osc 采样时钟为 48MHz
    cracker.osc_sample_length(sample_length) # 设置 Osc 采样长度为 20000
    cracker.osc_trigger_source('N') # 设置 Osc 触发源为 Nut
    cracker.osc_analog_gain('B', 10) # 设置 Osc 通道B 增益为 10倍，该值用户可根据实际采集情况进行调整，直到波形合适为止（此处要以注释的形式给出用户提示）
    cracker.osc_trigger_level(0) # 设置 Osc 触发电平为 0
    cracker.osc_trigger_mode('E') # 设置 Osc 触发模式为边沿触发
    cracker.osc_trigger_edge('U') # 设置 Osc 触发边沿为上升沿
    cracker.uart_config(baudrate=serial.Baudrate.BAUDRATE_115200, bytesize=serial.Bytesize.EIGHTBITS, parity=serial.Parity.PARITY_NONE, stopbits=serial.Stopbits.STOPBITS_ONE) # 设置 UART 参数为 115200 波特率，8 数据位，无校验，1 停止位

    time.sleep(2) # 等待设备稳定
    cmd = cmd_set_aes_enc_key + aes_key # 设置 AES 加密密钥
    status, ret = cracker.uart_transmit_receive(cmd, timeout=1000, rx_count=6) # 发送设置 AES 加密密钥的命令并接收响应
    if status != 0:
        raise Exception("Failed to set AES encryption key") # 如果设置 AES 加密密钥失败，抛出异常

def do(cracker, count):
    """
    在Acquisition的控制流程中，do方法会在每次采集时被调用一次，主要用于向 Cracker 设备发送 AES 加密的数据，并接收加密后的数据。
    """
    plaintext_data = random.randbytes(aes_data_len) # 生成随机的 AES 加密明文数据，长度为 aes_data_len（16字节）
    tx_data = bytes.fromhex(cmd_aes_enc.replace(' ', '')) + plaintext_data # 构造发送给 Cracker 设备的命令数据，包含 AES 加密命令和明文数据
    status, ret = cracker.uart_transmit_receive(tx_data, rx_count= 6 + aes_data_len, is_trigger=True) # 发送 AES 加密命令和明文数据，并接收响应，响应长度为 6 字节的状态信息加上 aes_data_len 字节的密文数据，is_trigger=True 表示该命令会触发 Osc 采集
    if status != 0:
        raise Exception("Failed to perform AES encryption") # 如果 AES 加密操作失败，抛出异常
    if len(ret) != 6 + aes_data_len:
        raise Exception(f"Received unexpected response length: {len(ret)}") # 如果接收到的响应长度不符合预期，抛出异常
    return {
        "plaintext": plaintext_data,
        "ciphertext": ret[-aes_data_len:],
        "key": bytes.fromhex(aes_key)
    }


def finish(cracker):
    """
        在Acquisition的控制流程中，finish方法会在每次采集完成后被调用一次，主要用于执行一些清理操作或者重置设备状态等。
        这里的 finish 方法没有具体的实现内容，因为在这个示例中我们没有需要在采集完成后执行的特定操作。
        但是在实际应用中，您可能需要在 finish 方法中添加一些代码来关闭设备连接、保存日志、重置设备状态或者执行其他清理工作，以确保设备处于一个良好的状态并且资源得到正确释放。
        :param cracker: Cracker 设备对象，在 finish 方法中用于调用设备的控制方法
        :type cracker: CrackerBasic
        :return: None
        :rtype: None
        :raises Exception: 如果在执行 finish 方法时发生错误，抛出异常
    """
    cracker.nut_clock_disable() # 关闭时钟
    cracker.nut_voltage_disable() # 关闭供电
```

***单元格5***

```
# 定义 Acquisition 控制流程，传入 init、do、finish 方法
acq = cn.simple_acq(cracker=s1, init_func=init, do_func=do, finish_func=finish)
# 定义采集控制面板并显示
p = cn.show_panel(acq)
# 这个之后将在当前cell下显示采集控制面板，您也可以在其他单元格中使用 cn.panel(acq) 来显示该控制面板
p
```

### 能量曲线采集

在 Cracker采集控制面板 界面，点击连接后界面将展示设备的ID、名称、版本信息，并且激活下方的配置面板和波形监控面板。

点击测试按钮，即可对设备进行实时调试（监控波形，需要打开监控开关），确保采集到正确的波形数据：

在调整到合适的参数后（在按照上述代码进行采集并使用NUT 103 golden 固件时，无需调整已是最好的效果），停止测试模式，点击运行按钮即可开始采集并保存波形数据。
采集到的能量轨迹曲线文件会保存到当前目录下的 dataset 文件夹中：如 `dataset/20251110104451.zarr`，以时间戳命名的 zarr 格式文件。

至此，恭喜您，您已经成功使用 CrackNuts 采集到了能量轨迹波形数据。

默认情况下随 Cracker 配套的 Nut(smt32_f103c8） 已经烧录了 HIS.elf 固件，其他更多可用的固件可到 <https://pan.baidu.com/s/1PXyKqeTfemepZ-wD9gDwYQ?pwd=2cda> 的 NutGolden 文件夹进行下载。

### 能量曲线使用

采集到的能量曲线数据存储格式默认位 zarr 格式，并且在 CrackNuts 增加了额外的数据，具体数据格式如下：

```
数组格式说明
MyData.zarr/                        <-- [根目录]
│
├── origin/ (或者 "0")               <-- [一级分组] 数据集类型 (兼容旧名 "0")
│   │
│   ├── 0/                          <-- [二级分组] 通道 0
│   │   ├── trace                   [Array] (该通道的波形数据)
│   │   ├── plaintext               [Array]
│   │   ├── ciphertext              [Array]
│   │   ├── key                     [Array]
│   │   └── ...                     [Array]
│   │
│   └── 1/                          <-- [二级分组] 通道 1 (如果有双通道采集)
│       ├── trace                   [Array]
│       ├── plaintext               [Array]
│       ├── ciphertext              [Array]
│       ├── key                     [Array]
│       └── ...
│
├── aligned/                        <-- [一级分组] 处理后的数据集
│   │
│   ├── 0/                          <-- [二级分组] 对应通道 0 的对齐数据
│   │   ├── trace                   [Array] (对齐后的波形)
│   │   └── ...
│   │
│   └── 1/
│      └── ...
├── ...
└── attrs
```

采集到的能量曲线数据默认存储在Jupyter notebook的同级目录的dataset目录下，以时间戳命名，一下代码是显示当前目录下最新的曲线文件

***单元格5***

```python
import os
import glob
from cracknuts.trace import ZarrTraceDataset

# 查找 dataset 目录下最新的 zarr 文件
zarr_files = glob.glob('dataset/*.zarr')

if not zarr_files:
    print("暂无曲线数据")
    zd = None
else:
    # 按修改时间排序，取最新的
    latest_zarr = max(zarr_files, key=os.path.getmtime)
    print(f"加载最新曲线文件：{latest_zarr}")
    zd = ZarrTraceDataset.load(latest_zarr)
    print("加载完成")

zd.plot() if zd is not None else print("暂无曲线数据")
```

如果要打开指定的曲线文件，可以用如下的代码

***单元格7(可选，默认不用写)***

```python
from cracknuts.trace import ZarrTraceDataset

# 加载 zarr 格式的能量曲线数据，路径请根据实际情况调整
zd = ZarrTraceDataset.load(r'dataset/20251110104451.zarr')
zd.plot() # 如下函数可以打开一个交互式的曲线查看器，支持缩放、平移等交互操作。注意这行代码一定要在单元格的最后，因为需要显示jupyter的widget，这个是jupyter的机制
```
