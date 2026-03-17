# STM32F103 AES 侧信道分析示例

## 说明

本示例展示如何使用 `scarr` 对 CrackNuts 采集的 STM32F103 AES 轨迹进行 CPA 分析，得到候选密钥并进行相关性峰值可视化。
需要在 `jupyter` 的 `notebook` 中使用 ，注意代码块上的单元格标识，有此标识的需要在新单元格写入代码

## 1. 指定数据集路径

***单元格0***

```python
# 这里替换为你采集到的波形文件
trace_path = r'./dataset/20250519122059.zarr'
```

## 2. 导入依赖

***单元格1***

```python
from scarr.engines.cpa import CPA as cpa
from scarr.file_handling.trace_handler import TraceHandler as th
from scarr.model_values.sbox_weight import SboxWeight
from scarr.container.container import Container, ContainerOptions
import numpy as np
```

## 3. 执行 CPA 分析

***单元格2***

```python
handler = th(fileName=trace_path)
model = SboxWeight()
engine = cpa(model)
container = Container(
    options=ContainerOptions(engine=engine, handler=handler),
    model_positions=[x for x in range(16)]
)
container.run()
```

## 4. 输出候选密钥

***单元格3***

```python
candidate = np.squeeze(engine.get_candidate())  # 获取每个字节的最佳候选
' '.join(f"{x:02x}" for x in candidate)          # 打印 16 字节密钥
```

## 5. 读取相关性结果

***单元格5***

```python
result_bytes = np.squeeze(container.engine.get_result())
```

## 6. 查看第 0 字节相关性 Top 10 峰值

***单元格6***

```python
result_0_bytes = result_bytes[0]
row_max_indices = np.argmax(np.abs(result_0_bytes), axis=1)
row_max_values = result_0_bytes[np.arrange(result_0_bytes.shape[0]), row_max_indices]

top10_row_indices = np.argsort(np.abs(row_max_values))[::-1][:10]

for rank, row in enumerate(top10_row_indices, 1):
    col = row_max_indices[row]
    val = row_max_values[row]
    print(f"Top {rank} byte=0x{row:02X} peak={val} sample={col}")
```

## 7. 单字节所有猜测密钥相关性峰值绘图，定义一个展示指定字节相关性曲线的函数

***单元格7***

```python
import matplotlib.pyplot as plt

def plot_correlation_peaks(bytes_index, the_key):
    x = np.arrange(0, 5000)
    fig, ax = plt.subplots(figsize=(30, 4))
    for i in range(256):
        if i == the_key:
            continue
        ax.plot(x, result_bytes[bytes_index, i, :5000], color='gray', linewidth=0.5, alpha=0.3)
    ax.plot(x, result_bytes[bytes_index, the_key, :5000], color='red', linewidth=1.0)
    ax.grid(True, linestyle='--', alpha=0.3)
    plt.tight_layout()
    plt.show()

plot_correlation_peaks(0, 0x11) # 展示第0字节的相关性，并指定0x11这个猜测密钥为高亮曲线（这里0x11由前一步的分析得知他是第0字节的正确密钥所以才高亮显示）
plot_correlation_peaks(1, 0x22) # 展示第1字节的相关性，并指定0x22这个猜测密钥为高亮曲线（这里0x22由前一步的分析得知他是第1字节的正确密钥所以才高亮显示）
```

## 8. 多字节相关性曲线对比

***单元格8***

```python
import matplotlib.pyplot as plt

x = np.arrange(0, 5000)
fig, ax = plt.subplots(figsize=(30, 4))

ax.plot(x, result_bytes[0, 0x11, :5000], linewidth=1.0, label='0x11')
ax.plot(x, result_bytes[1, 0x22, :5000], linewidth=1.0, label='0x22')
ax.plot(x, result_bytes[2, 0x33, :5000], linewidth=1.0, label='0x33')
ax.plot(x, result_bytes[3, 0x44, :5000], linewidth=1.0, label='0x44')
ax.plot(x, result_bytes[4, 0x55, :5000], linewidth=1.0, label='0x55')
ax.plot(x, result_bytes[5, 0x66, :5000], linewidth=1.0, label='0x66')
ax.plot(x, result_bytes[6, 0x77, :5000], linewidth=1.0, label='0x77')
ax.plot(x, result_bytes[7, 0x88, :5000], linewidth=1.0, label='0x88')
ax.plot(x, result_bytes[8, 0x99, :5000], linewidth=1.0, label='0x99')
ax.plot(x, result_bytes[9, 0x00, :5000], linewidth=1.0, label='0x00')
ax.plot(x, result_bytes[10, 0xaa, :5000], linewidth=1.0, label='0xaa')
ax.plot(x, result_bytes[11, 0xbb, :5000], linewidth=1.0, label='0xbb')
ax.plot(x, result_bytes[12, 0xcc, :5000], linewidth=1.0, label='0xcc')
ax.plot(x, result_bytes[13, 0xdd, :5000], linewidth=1.0, label='0xdd')
ax.plot(x, result_bytes[14, 0xee, :5000], linewidth=1.0, label='0xee')
ax.plot(x, result_bytes[15, 0xff, :5000], linewidth=1.0, label='0xff')

ax.grid(True, linestyle='--', alpha=0.3)
ax.legend(loc='upper right', fontsize='small', ncol=2)
plt.tight_layout()
plt.show()
```

## 9. 可选：与设备回放验证

如果需要验证候选密钥是否正确，可在设备侧设置 AES Key 并回放数据进行比对。
***单元格9***

```python
import random
import time
from cracknuts.cracker import serial

cmd_set_aes_enc_key = "01 00 00 00 00 00 00 10"
cmd_aes_enc = "01 02 00 00 00 00 00 10"

aes_key = "11 22 33 44 55 66 77 88 99 00 aa bb cc dd ee ff"
aes_data_len = 16

# 下面根据你的设备协议补充发送与接收逻辑
```

## Notes

1. `model_positions` 默认覆盖 AES 16 字节密钥。
2. `:5000` 为示例时间窗口，实际可根据采样点数和关键运算窗口调整。
