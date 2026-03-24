# CrackNuts 整体架构文档

> 最后更新: 2026-03-24
> 版本: 0.22.2
> Python: >= 3.12

---

## 1. 项目概述与定位

CrackNuts 是一个用于控制密码分析硬件设备的 Python 库，专注于**旁路攻击 (Side-Channel Analysis, SCA)**。主要支持两大攻击场景：

- **功耗分析 (Power Analysis)**: 通过采集目标设备执行加密运算时的功耗曲线 (trace)，结合统计方法进行密钥恢复。
- **故障注入 (Glitch/Fault Injection)**: 通过电压/时钟故障注入干扰目标设备运行，观察异常行为以提取密钥信息。

项目同时提供：
- **纯 Python API**: 供脚本和 Notebook 直接调用。
- **Jupyter Widget 交互界面**: 基于 anywidget + 预编译的 React/TypeScript 前端，提供可视化配置、波形预览和采集控制。

**硬件设备型号**:
- **S1**: 基础功耗分析设备（示波器 + NUT 通信接口）
- **G1**: S1 的超集，增加 VCC/GND/Clock Glitch 功能
- **O1**: 继承自 S1，新增型号（代码中存在但功能尚不完整）

---

## 2. 整体架构分层

```
┌──────────────────────────────────────────────────────────────┐
│                      用户接口层 (Public API)                   │
│  cracknuts.__init__: cracker_s1(), cracker_g1(), cracker_o1() │
│  simple_acq(), simple_glitch_acq(), show_panel()              │
│  load_trace_dataset(), discover_devices()                     │
├──────────────────────────────────────────────────────────────┤
│              交互界面层 (jupyter/)                              │
│  anywidget (Python traitlets) + React/TS (预编译 JS/CSS)       │
│  CracknutsPanelWidget (组合面板)                               │
│  TracePanelWidget, ScopePanelWidget, AcquisitionPanelWidget   │
│  WorkbenchG1Panel (Glitch 工作台)                              │
├──────────────────────────────────────────────────────────────┤
│              采集编排层 (acquisition/)                          │
│  Acquisition (模板方法: init → loop(pre_do → do → post_do) →  │
│               finish)                                         │
│  GlitchAcquisition (Acquisition 子类, 集成 glitch 参数遍历)    │
│  ScopeAcquisition (scope/, 独立的示波器采集循环)               │
├──────────────────────────────────────────────────────────────┤
│              设备通信层 (cracker/)                              │
│  CrackerBasic[T] (ABC, CNP 协议 socket 通信)                  │
│  CrackerS1 → CrackerG1 → CrackerO1 (继承链)                  │
│  Operator (守护进程管理通道, 端口 9760)                        │
│  CrackerManager (UDP 广播设备发现, 端口 9769)                  │
│  SSHCracker (Paramiko SSH 远程管理)                           │
├──────────────────────────────────────────────────────────────┤
│              数据存储层 (trace/)                                │
│  TraceDataset (ABC) → ZarrTraceDataset / NumpyTraceDataset    │
│  TracePlot (Plotly Resampler 大数据量绘图)                    │
│  downsample (Numba JIT 加速的 min-max 降采样)                 │
├──────────────────────────────────────────────────────────────┤
│              故障注入层 (glitch/)                               │
│  GlitchGenerateParam + AbstractGlitchParamGenerator           │
│  VCCGlitchParamGenerator / GNDGlitchParamGenerator            │
│  GlitchTestResult (SQLite 结果持久化)                         │
├──────────────────────────────────────────────────────────────┤
│              模拟设备层 (mock/)                                 │
│  MockCracker (TCP 服务器, 模拟 CNP 协议响应)                  │
│  MockOperator                                                 │
└──────────────────────────────────────────────────────────────┘
```

---

## 3. 各模块职责说明

### 3.1 cracker/ — 设备通信层

**核心类继承链**: `CrackerBasic[T]` → `CrackerS1` → `CrackerG1` → `CrackerO1`

#### CrackerBasic (cracker_basic.py)
- 抽象基类，使用 `Generic[T]` 参数化配置类型 (T extends ConfigBasic)
- 管理 TCP socket 连接（端口 9761），线程安全的命令发送锁 `_command_lock`
- 提供 `send_with_command()` / `send_and_receive()` 方法实现 CNP 协议通信
- `connection_status_check` 装饰器保护所有需要连接的方法
- 示波器控制: `osc_single()`, `osc_force()`, `osc_get_analog_wave()`, `osc_is_triggered()`
- NUT 通信接口: UART/SPI/I2C 配置和收发
- 寄存器直读写: `register_read()`, `register_write()` (用于 G1 时钟 glitch)
- 配置管理: `get_current_config()` / `write_config_to_cracker()` 从设备读写二进制配置
- 设备发现: `discover_devices()` 类方法，委托给 `CrackerManager`
- IP 管理: `change_ip()` / `set_device_ip()` 类方法
- SSH Shell: `self.shell` 属性指向 `SSHCracker` 实例

#### ConfigBasic / ConfigS1 / ConfigG1
- 纯数据类 (非 dataclass)，通过 `__dict__` 序列化为 JSON
- 包含示波器配置 (通道、增益、采样长度、触发) + NUT 配置 (电压、时钟、接口)
- ConfigG1 额外包含 VCC/GND/Clock Glitch 参数

#### CrackerS1 (cracker_s1.py)
- 实现 `get_default_config()` → ConfigS1
- 实现 `get_current_config()` 从设备读取并解析二进制配置
- 实现 `write_config_to_cracker()` 将配置逐项写入设备
- NUT 电压/时钟控制、UART/SPI/I2C 收发方法

#### CrackerG1 (cracker_g1.py)
- 继承 CrackerS1，增加 Glitch 功能
- VCC Glitch: `glitch_vcc_arm()`, `glitch_vcc_config()`, `glitch_vcc_force()`, `glitch_vcc_normal()`
- GND Glitch: `glitch_gnd_arm()`, `glitch_gnd_config()`, `glitch_gnd_force()`, `glitch_gnd_normal()`
- Clock Glitch: `glitch_clock_normal()`, `glitch_clock_config()`, `glitch_clock_arm()`, `glitch_clock_force()`
- 电压值通过 CSV 映射表 + scipy.interpolate.interp1d 在 DAC code 和电压之间转换
- 时钟通过波形数组 (高低电平序列) 控制，支持预定义频率: 4M/8M/10M/16M/20M/40M/80M

#### CrackerO1 (cracker_o1.py)
- 继承 CrackerS1 (非 G1)，目前代码结构与 S1 类似

#### Operator (operator.py)
- 独立的 TCP 客户端，连接设备守护进程端口 9760
- 控制设备服务进程的启停、固件更新、LED 显示
- 获取设备信息: 型号、序列号、版本、IP 配置

#### CrackerManager (cracker_manager.py)
- UDP 广播设备发现 (CRKR 协议，端口 9769)
- 支持单次扫描 (`discover_once()`) 和后台持续扫描 (`start_discovery()`)
- 设备状态跟踪: ONLINE/OFFLINE，支持回调: discovered/updated/lost
- 也可作为 CLI 工具独立运行 (`python -m cracknuts.cracker.cracker_manager list`)

#### SSHCracker (ssh_client.py)
- Paramiko SSH 客户端封装
- 内置 Ed25519 私钥用于设备认证
- 支持命令执行 (流式输出)、文件上传、上传并执行

#### serial.py
- 通信接口参数的枚举定义: Baudrate, Parity, Stopbits, Bytesize, SpiCpol, SpiCpha, I2cSpeed

### 3.2 acquisition/ — 采集编排层

#### Acquisition (acquisition.py)
- 抽象基类，实现**模板方法模式**的采集生命周期
- **生命周期**: `pre_init()` → `init()` → `_post_init()` → **loop**(pre_do → do → trigger_wait → get_waves → post_do) → `_pre_finish()` → `finish()` → `_post_finish()`
- **运行模式**:
  - `test()` / `test_sync()`: 测试模式，无限循环不存储
  - `run()` / `run_sync()`: 采集模式，指定条数，持久化存储
  - `pause()` / `resume()` / `stop()`: 运行控制
- 通过 `threading.Thread` 实现后台异步运行
- `threading.Event` 实现暂停/恢复
- 状态机: STOPPED(0) → TESTING(1) / RUNNING(2) / GLITCH_TEST_RUNNING(3)，暂停状态为负数
- **观察者回调**: `on_status_changed()`, `on_run_progress_changed()`, `on_wave_loaded()`, `on_config_changed()`
- 触发判断循环: 轮询 `_is_triggered()` 直到触发或超时
- 数据持久化: 自动创建 ZarrTraceDataset 或 NumpyTraceDataset

#### GlitchAcquisition (glitch_acquisition.py)
- 继承 Acquisition，增加 Glitch 参数遍历功能
- `glitch_run()`: 根据参数生成器自动遍历所有 glitch 参数组合
- `pre_do()` 中自动配置当前 glitch 参数到设备
- `_post_do()` 中记录 glitch 测试结果到 SQLite 数据库
- GlitchTestResult / VCCGlitchTestResult: SQLite 数据表存储 glitch 测试结果
- GlitchDoData / GlitchDoStatus: glitch 执行结果数据结构

#### __init__.py — 工厂函数
- `simple_acq()`: 接受 init/do/finish 三个 lambda，动态创建 Acquisition 匿名子类
- `simple_glitch_acq()`: 接受 init/do/finish 三个 lambda，动态创建 GlitchAcquisition 匿名子类
- 这是推荐的用户 API，避免用户手动继承 Acquisition 类

### 3.3 trace/ — 数据存储层

#### TraceDataset (trace.py)
- 抽象基类，定义曲线数据集的统一接口
- 支持高级索引: `dataset[channel_slice, trace_slice]` 返回 (traces, data)
- `trace_data`, `trace`, `data` 属性返回 `TraceDatasetData` 代理对象，支持二级切片
- TraceIndexFilter: 描述通道+曲线索引的过滤器，用于前端交互

#### ZarrTraceDataset
- Zarr v2 格式存储 (目录层级)
- **目录结构**:
  ```
  dataset.zarr/
    0/              ← origin 分组 (兼容旧版)
      0/            ← 通道 0
        traces      ← (trace_count, sample_count) int16
        plaintext   ← (trace_count, plaintext_len) int8
        ciphertext  ← (trace_count, ciphertext_len) int8
        key         ← (trace_count, key_len) int8
        extended    ← (trace_count, extended_len) int8
      1/            ← 通道 1
    aligned/        ← 对齐后的数据 (预留)
    attrs           ← 元数据 JSON
  ```
- Chunk 策略: 每个 chunk 一条曲线，单个 chunk 最大 50MB

#### NumpyTraceDataset
- NumPy .npy 文件格式存储
- 使用独立的 .npy 文件存放各数组

#### ScarrTraceDataset
- 兼容 Scarr 格式的数据集读取 (导入时存在)

#### TracePlot (plot.py)
- 使用 plotly-resampler 的 FigureWidgetResampler 进行大数据量曲线绘制
- 支持 shift (偏移)、zoom 操作

#### downsample.py
- Numba JIT 编译的 min-max 降采样算法
- 用于前端波形显示时的数据压缩

### 3.4 jupyter/ — 交互界面层

#### 架构概述
- 基于 **anywidget** 框架: Python 端使用 traitlets 定义同步属性，前端为预编译的 JS/CSS 文件
- 前端源码目前**不在仓库内**，编译产物位于 `jupyter/static/` 目录
- 前端文件: `CrackNutsPanelWidget.js`, `ScopePanelWidget.js`, `TracePanelWidget.js`, `AcquisitionPanelWidget.js`, `CrackerS1PanelWidget.js`, `CrackerG1Widget.js`, `GlitchTestPanelWidget.js`, `GlitchTestResultAnalysisWidget.js`

#### 面板类体系

**MsgHandlerPanelWidget (panel.py)**
- 最底层基类，继承 `anywidget.AnyWidget`
- 实现消息总线: `reg_msg_handler(source, event, handler)` 注册前端消息回调
- 消息格式: `{source: str, event: str, args: dict}`

**CrackerPanelWidget (cracker_s1_panel.py)**
- 使用 traitlets 声明所有 cracker 配置属性 (tag(sync=True) 自动同步前端)
- `read_config_from_cracker()`: 从设备读取配置并更新 traitlets
- `write_config_to_cracker()`: 将 traitlets 值写入设备
- `listen_cracker_config()`: 使用 ConfigProxy 代理实现双向同步
- `on_trait_change()`: traitlets observe 机制，前端修改自动写入设备

**AcquisitionPanelWidget (acquisition_panel.py)**
- 采集面板，管理 Acquisition 对象的配置和状态
- 注册消息处理: test/run/stop/pause/resume 按钮事件
- 采集状态和进度通过 traitlets 同步到前端

**ScopePanelWidget (scope_panel.py)**
- 示波器面板，管理 ScopeAcquisition 对象
- 波形数据通过 buffers (二进制通道) 传送到前端
- 支持 normal/single/repeat 三种采集模式

**CracknutsPanelWidget (cracknuts_panel.py)**
- **组合面板**: 多重继承 CrackerPanelWidget + AcquisitionPanelWidget + ScopePanelWidget + MsgHandlerPanelWidget
- 是主要的用户界面入口
- 工作区配置文件管理: `.config/<notebook_name>.json` 存储配置

**WorkbenchG1Panel (workbench_g1_panel.py)**
- G1 Glitch 工作台面板
- 管理 GlitchAcquisition，支持 glitch 参数配置和 glitch_run

**TracePanelWidget (trace_panel.py)**
- 曲线查看面板，支持 TraceDataset 的可视化浏览
- 使用 downsample 降采样后通过 buffers 发送到前端

#### ConfigProxy (ui_sync.py)
- 代理模式实现 cracker config 与 widget traitlets 的双向同步
- 拦截 `__setattr__`: 写入 config 属性时自动同步到 widget traitlets

### 3.5 glitch/ — 故障注入层

#### GlitchGenerateParam
- 描述单个参数的遍历规则: mode(INCREASE/DECREASE/RANDOM/FIXED), start, end, step, count

#### AbstractGlitchParamGenerator
- 在构造时调用 `_build()` 生成所有参数组合 (笛卡尔积)
- `next()` 顺序返回下一个参数组合，循环复用

#### VCCGlitchParamGenerator / GNDGlitchParamGenerator
- 6 个参数维度: normal, wait, glitch, count, repeat, interval
- 使用 `itertools.product` 生成所有组合

### 3.6 scope/ — 示波器模块

#### ScopeAcquisition (scope_acquisition.py)
- 独立于 Acquisition 的示波器采集循环
- 三种模式: normal(连续触发), single(等待触发), repeat(超时后强制触发)
- 在独立线程中运行，通过状态变量控制

### 3.7 mock/ — 模拟设备层

#### MockCracker (mock_cracker.py)
- TCP 服务器，模拟 CNP 协议设备响应
- 使用 `@_handler(command)` 装饰器注册命令处理函数
- 生成随机波形数据用于测试
- 支持缓存接收到的 payload 以便验证

#### MockOperator (mock_operator.py)
- 模拟 Operator 守护进程 (尚需确认内容)

### 3.8 utils/

#### hex_util.py
- 十六进制格式化工具，用于日志中的字节矩阵显示

#### user_config.py
- 用户配置管理 (如语言设置)

### 3.9 其他目录

- **firmware/**: 设备固件镜像文件
- **template/**: 项目模板
- **tutorials/**: 教程文件
- **glitch/voltage_map/**: DAC code <-> 电压 CSV 映射表 (vcc.csv, gnd.csv, clk.csv)

---

## 4. 核心数据流

### 4.1 功耗分析采集流程

```
用户代码                    Acquisition             CrackerS1          设备 (FPGA)
   │                           │                      │                   │
   │  simple_acq(cracker,      │                      │                   │
   │    init, do, finish)      │                      │                   │
   │  acq.run(count=1000)      │                      │                   │
   │ ─────────────────────────>│                      │                   │
   │                           │  init()              │                   │
   │                           │ ──────────────────> (用户 init_func)     │
   │                           │                      │                   │
   │                           │  ┌─ LOOP ──────────────────────────────┐│
   │                           │  │ pre_do()           │                ││
   │                           │  │  osc_single() ────>│ ── CNP ──────>││
   │                           │  │                    │                ││
   │                           │  │ do(count)          │                ││
   │                           │  │ ──────────────> (用户 do_func)      ││
   │                           │  │                    │ uart/spi ────>││
   │                           │  │                    │ <── response ─││
   │                           │  │                    │                ││
   │                           │  │ trigger_wait_loop  │                ││
   │                           │  │  is_triggered() ──>│ ── CNP ──────>││
   │                           │  │                    │                ││
   │                           │  │ get_waves()        │                ││
   │                           │  │  osc_get_analog ──>│ ── CNP ──────>││
   │                           │  │                    │ <── wave data ─││
   │                           │  │                    │                ││
   │                           │  │ dataset.set_trace()│                ││
   │                           │  │  (Zarr 写入)       │                ││
   │                           │  └────────────────────────────────────┘│
   │                           │  finish()             │                │
   │                           │ ──────────────────> (用户 finish_func) │
   │                           │  dataset.dump()       │                │
```

### 4.2 Glitch 测试流程

```
用户代码                 GlitchAcquisition        CrackerG1           设备
   │                           │                      │                 │
   │  acq.set_glitch_params    │                      │                 │
   │    (VCCGlitchParamGen)    │                      │                 │
   │  acq.glitch_run()         │                      │                 │
   │ ─────────────────────────>│                      │                 │
   │                           │  pre_init()          │                 │
   │                           │   创建 SQLite DB     │                 │
   │                           │                      │                 │
   │                           │  ┌─ LOOP ───────────────────────────┐ │
   │                           │  │ pre_do()           │              │ │
   │                           │  │  param_gen.next() ─┐              │ │
   │                           │  │  glitch_vcc_config ─>│ ── CNP ──>│ │
   │                           │  │  osc_single() ─────>│ ── CNP ──>│ │
   │                           │  │                    │              │ │
   │                           │  │ do(count) ─> (用户 do_func 触发)  │ │
   │                           │  │                    │              │ │
   │                           │  │ _post_do()         │              │ │
   │                           │  │  result.add(param, data)          │ │
   │                           │  └──────────────────────────────────┘ │
```

### 4.3 Jupyter Widget 数据流

```
React/TS 前端                 Python Widget                  Cracker 设备
   │                              │                              │
   │  traitlet 变更 (sync=True)   │                              │
   │ <──────────────────────────> │                              │
   │                              │                              │
   │  model.send({source, event}) │                              │
   │ ────────────────────────────>│  _msg_handle()               │
   │                              │  reg_msg_handler callback    │
   │                              │  ──────────────────────────> │
   │                              │  <── response ────────────── │
   │  model.set('traitlet', val)  │                              │
   │ <────────────────────────────│                              │
   │                              │                              │
   │  Binary buffers (波形数据)    │                              │
   │ <────────────────────────────│ osc_get_analog_wave()        │
   │                              │  downsampled Int16Array      │
```

**通信机制**:
1. **traitlets 同步**: 使用 `tag(sync=True)` 标记的属性自动在 Python 和 JS 之间双向同步（anywidget 内置）
2. **自定义消息**: 前端通过 `model.send()` 发送 `{source, event, args}` 格式消息，Python 端通过 `reg_msg_handler()` 注册处理函数
3. **Binary buffers**: 波形数据通过 anywidget 的 buffers 通道以二进制格式传输（Int16Array），避免 JSON 序列化开销
4. **ConfigProxy**: 实现 cracker config 属性变更到 widget traitlet 的自动同步，反方向通过 traitlet observe 实现

---

## 5. 关键设计模式及其应用

### 5.1 模板方法模式 (Template Method)
**应用位置**: `Acquisition._do_run()`

核心采集循环固化在基类中：
```
pre_init() → init() → _post_init() →
  loop(pre_do → do → trigger_wait → get_waves → post_do) →
_pre_finish() → finish() → _post_finish()
```
用户只需实现 `init()`, `do()`, `finish()` 三个抽象方法。

### 5.2 策略模式 (Strategy)
**应用位置**:
- `CrackerBasic` 抽象类定义统一接口，S1/G1/O1 提供不同实现
- `AbstractGlitchParamGenerator` 定义参数生成策略，VCC/GND/Clock 分别实现

### 5.3 工厂函数模式
**应用位置**: `simple_acq()`, `simple_glitch_acq()`

动态创建匿名子类，将 lambda 函数包装为 Acquisition 实例：
```python
class AnonymousAcquisition(Acquisition):
    def init(self): init_func(cracker)
    def do(self, count): return do_func(cracker, count)
    def finish(self): finish_func(cracker)
```

### 5.4 观察者模式 (Observer)
**应用位置**:
- `Acquisition`: `on_status_changed()`, `on_run_progress_changed()`, `on_wave_loaded()`, `on_config_changed()`
- `CrackerManager`: `on_discovered()`, `on_updated()`, `on_lost()`
- anywidget `on_msg()` 消息总线
- traitlets `observe()` 属性变更监听

### 5.5 代理模式 (Proxy)
**应用位置**: `ConfigProxy` (ui_sync.py)
- 拦截 config 属性写入，自动同步到 widget traitlets
- 拦截 config 属性读取，直接转发到底层 config 对象

### 5.6 装饰器模式
**应用位置**:
- `@connection_status_check`: 保护需要设备连接的方法
- `@_handler(command)`: MockCracker 命令路由注册

---

## 6. CNP 通信协议结构

### 6.1 协议概述
CNP (CrackNuts Protocol) 是一个简单的二进制请求-响应协议，基于 TCP 传输。

### 6.2 请求消息格式
```
┌─────────────────────────────────────────┬─────────┐
│              Request Header              │         │
│ Magic │Version│Dir│Command│ RFU │ Length │ Payload │
│  4B   │  2B   │1B │  2B   │ 2B  │  4B   │$Length  │
│'CRAK' │   1   │'S'│       │     │       │         │
└─────────────────────────────────────────┴─────────┘
Format: ">4sH1sHHI" (big-endian, 15 bytes header)
```

### 6.3 响应消息格式
```
┌──────────────────────────────────────┬─────────┐
│           Response Header             │         │
│ Magic │Version│Dir│Status│  Length   │ Payload │
│  4B   │  2B   │1B │ 2B  │   4B     │$Length  │
│'CRAK' │   1   │'R'│     │          │         │
└──────────────────────────────────────┴─────────┘
Format: ">4sH1sHI" (big-endian, 13 bytes header)
```

### 6.4 状态码
| Code   | 名称                  | 说明 |
|--------|-----------------------|------|
| 0x0000 | STATUS_OK             | 成功 |
| 0x0001 | STATUS_BUSY           | 设备忙 |
| 0x8000 | STATUS_ERROR          | 通用错误 |
| 0x8001 | COMMAND_UNSUPPORTED   | 命令不支持 |
| 0x8002 | NUT_TIMEOUT           | NUT 执行超时 |
| 0x8003 | ANALOG_CHANNEL_NONE_DATA | 模拟通道无数据 |
| 0x8004 | DIGITAL_CHANNEL_NONE_DATA | 数字通道无数据 |

### 6.5 命令分组
| 范围        | 功能             |
|-------------|------------------|
| 0x0001-0x0007 | 通用命令 (配置、名称、版本、寄存器读写) |
| 0x0100-0x012F | 示波器模拟/数字通道 + 采样配置 |
| 0x0150-0x0153 | 触发配置 |
| 0x0200-0x0206 | NUT 基础控制 (使能、电压、时钟、复位) |
| 0x0220-0x022A | UART 接口 |
| 0x0230-0x023F | SPI 接口 |
| 0x0240-0x024D | I2C 接口 |
| 0x0250-0x025A | CAN 接口 |
| 0x0260-0x0266 | UART (新版) |
| 0x0310-0x0314 | Glitch VCC (G1) |
| 0x0320-0x0324 | Glitch GND (G1) |
| 0x0330-0x0337 | Glitch Clock (G1) |

### 6.6 设备发现协议 (CRKR)
独立于 CNP 的 UDP 广播协议，用于局域网设备发现和 IP 管理：
- 端口: 9769
- Magic: `CRKR`
- 命令: DISCOVER(1), SET_IP(2), ACK(3)
- Header: `"!4sBBHIHH"` (4B magic + 1B version + 1B cmd + 2B reserved + 4B txid + 2B payload_len + 2B reserved)

### 6.7 Operator 协议
复用 CNP 消息格式，端口 9760，命令码:
| Code   | 功能 |
|--------|------|
| 0x0001 | START_SERVER |
| 0x0002 | STOP_SERVER |
| 0x0003 | GET_STATUS |
| 0x0004 | UPDATE_SERVER |
| 0x0005 | UPDATE_BITSTREAM |
| 0x0006 | SET_IP |
| 0x0007 | GET_IP |
| 0x0009 | GET_MODEL |
| 0x000A | GET_SN |
| 0x000B | GET_VERSION |
| 0x000C | GET_SERVER_VERSION |
| 0x000D | SET_LED |

---

## 7. 公开 API 设计

### 7.1 顶层导出 (cracknuts.__init__)

```python
# 设备创建
cracker_s1(address) -> CrackerS1
cracker_g1(address) -> CrackerG1
cracker_o1(address) -> CrackerO1
new_cracker(address, model=None)  # deprecated

# 采集创建
simple_acq(cracker, init_func, do_func, finish_func, **kwargs) -> Acquisition
simple_glitch_acq(cracker, init_func, do_func, finish_func, **kwargs) -> GlitchAcquisition

# Jupyter 面板
show_panel(acq) -> Widget

# 数据加载
load_trace_dataset(path) -> TraceDataset

# 设备发现
discover_devices() -> list[dict]

# 版本
version() -> str
```

### 7.2 典型用户工作流

```python
import cracknuts as cn

# 1. 创建设备
cracker = cn.cracker_s1("192.168.0.10")
cracker.connect()

# 2. 创建采集
acq = cn.simple_acq(
    cracker,
    init_func=lambda c: (c.nut_enable(), c.nut_voltage(3.3)),
    do_func=lambda c, i: {"plaintext": pt, "ciphertext": c.spi_transceive(pt)},
    finish_func=lambda c: c.nut_disable(),
    trace_count=1000,
)

# 3a. 脚本模式
acq.run_sync()

# 3b. Jupyter 模式
cn.show_panel(acq)  # 显示交互面板

# 4. 分析
dataset = cn.load_trace_dataset("./dataset/20240101120000.zarr")
traces = dataset.trace[0, :]  # 通道0所有曲线
```

---

## 8. 测试策略

### 8.1 现有测试
测试文件位于 `tests/` 目录，使用 pytest 框架：

- **cracker/**: `test_operator.py`, `test_cracker_s1.py`, `test_cracker_whit_device.py`, `test_basic_cracker.py`
- **acquisition/**: `test_acquistion.py`, `test_acq_with_mock.py`
- **trace/**: `test_tracedataset.py`
- **logger/**: `test_logger.py`
- **utils/**: 辅助工具
- **基准测试**: `zarr_benchmark.py`, `downsample_benchmark.py`, `zarr_speed_test.py`

### 8.2 测试方式
- **MockCracker**: TCP 服务器模拟设备，在 `conftest.py` 中启动，用于无硬件时的集成测试
- **设备测试**: `test_cracker_whit_device.py` 需要实际硬件连接
- 当前缺少系统性的单元测试覆盖

### 8.3 测试改进空间
- Jupyter widget 层完全没有测试
- 前端 JS 部分无测试基础设施
- glitch 参数生成器缺少独立单元测试
- 缺少 CI/CD 配置

---

## 9. 潜在的架构问题与改进点

### 9.1 设计问题

#### P1: CracknutsPanelWidget 多重继承过度复杂
`CracknutsPanelWidget` 同时继承 `CrackerPanelWidget`, `AcquisitionPanelWidget`, `ScopePanelWidget`, `MsgHandlerPanelWidget` 四个类。MRO (方法解析顺序) 复杂，traitlet 属性名冲突风险高，且增加新面板功能时继承链难以扩展。

**建议**: 改用组合模式，将各子面板作为独立组件组合使用。

#### P2: 配置类缺乏类型安全
`ConfigBasic` / `ConfigS1` / `ConfigG1` 使用普通属性而非 `dataclass` 或 `TypedDict`，没有类型验证。`load_from_json()` 直接通过 `__dict__` 写入，可能引入非法字段。

**建议**: 迁移到 `@dataclass` 或 Pydantic model，增加序列化/反序列化验证。

#### P3: Acquisition 类职责过重
`Acquisition._do_run()` 方法超过 150 行，集成了参数合并、状态管理、数据集创建、采集循环、触发等待、数据存储等多个职责。

**建议**: 提取 DatasetFactory, TriggerWaiter, AcquisitionStateMachine 等子组件。

#### P4: GlitchAcquisition._build_glitch_param_generator() 大量重复代码
VCC 和 GND 参数解析逻辑几乎完全相同（约 120 行重复），仅 JSON key 有微小差异 (`"data"` vs `"params"`)。

**建议**: 提取通用解析方法，消除重复。

### 9.2 耦合风险

#### P5: 前端源码不在仓库
编译后的 JS/CSS 文件在 `jupyter/static/` 目录，但 React/TypeScript 源码不在此仓库中。这导致：
- 无法在同一 PR 中同时审查前后端变更
- 前端构建流程不透明
- 前后端接口契约仅靠约定维护

#### P6: CrackerG1 Clock Glitch 使用寄存器直写
Clock Glitch 不通过 CNP 命令，而是直接使用 `register_write()` 操作硬编码地址 (0x43C10000 + offset)。这绕过了协议抽象层，硬件变更时需要同步修改多处代码。

#### P7: cracker_g1.py 模块级副作用
`cracker_g1.py` 在模块加载时立即读取 CSV 文件并构建插值函数。如果 CSV 文件缺失或格式变更，import 即失败。

### 9.3 性能隐患

#### P8: 采集循环中重复调用 get_current_config()
`ScopeAcquisition._get_waves()` 每次调用都执行 `self._cracker.get_current_config()`，这是一次完整的 CNP 请求。在高频采集时浪费带宽。

**建议**: 缓存配置，仅在配置变更时刷新。

#### P9: GlitchTestResult 使用 SQLite 同步写入
每次 glitch 测试结果都执行 `INSERT + COMMIT`，在大量参数组合时成为 I/O 瓶颈。

**建议**: 批量写入或使用 WAL 模式配合延迟提交（已配置 WAL，但每条 commit 仍然频繁）。

#### P10: Zarr v2 版本锁定
`pyproject.toml` 锁定 `zarr>=2.18.0,<3.0.0`，无法使用 Zarr v3 的性能改进和新 API。

### 9.4 可扩展性

#### P11: 新设备型号添加需要修改多处
添加新 Cracker 型号需要：修改 `cracker/__init__.py` 工厂函数 + `cracknuts/__init__.py` 导出 + `jupyter/__init__.py` 面板路由 + 新建对应 Panel 类 + 前端组件。

**建议**: 引入注册机制，新型号通过注册而非修改已有代码来集成。

#### P12: 缺少 Glitch Clock 参数生成器
`GNDGlitchParamGenerator` 是 `VCCGlitchParamGenerator` 的空子类（无任何重写）。Clock Glitch 参数生成器标记为 `...` 待实现。`_build_glitch_param_generator()` 中 clock 分支为空。

### 9.5 代码质量

#### P13: 文档字符串 copy-paste 错误
`cracker_g1()` 和 `cracker_o1()` 工厂函数的 docstring 都写着 "Creates and returns a CrackerS1 instance"。

#### P14: 属性命名不一致
`TraceDataset.adata_plaintext_length` 疑似 typo（应为 `data_plaintext_length`）。

#### P15: _loop_without_log() 整个方法被注释
`Acquisition._loop_without_log()` 几乎完全注释掉，属于死代码。

#### P16: 硬编码的 SSH 私钥
`SSHCracker` 和 `ssh_client.py` 模块顶层都内嵌了相同的 Ed25519 私钥。虽然这是设备出厂密钥非用户机密，但仍不适合直接写在源码中。

---

## 10. 依赖关系

### 10.1 核心依赖 (pyproject.toml)
| 包 | 版本范围 | 用途 |
|----|----------|------|
| numpy | >=2.0.0,<3.0.0 | 数组计算 |
| zarr | >=2.18.0,<3.0.0 | 曲线数据存储 |
| anywidget | >=0.9.0,<1.0.0 | Jupyter Widget 框架 |
| pandas | >=2.0.0,<3.0.0 | DAC 电压映射 CSV 读取 |
| scipy | >=1.16.0,<2.0.0 | 插值函数 |
| numba | >=0.63.0,<1.0.0 | 降采样 JIT 加速 |
| paramiko | >=4.0.0 | SSH 连接 |
| click | >=8.0.0,<9.0.0 | CLI |
| pillow | >=12.0.0,<13.0.0 | 图像处理 |
| packaging | >=24.0 | 版本解析 |

### 10.2 可选依赖
| 包 | 用途 |
|----|------|
| plotly-resampler | 大数据量曲线绘制 (TracePlot) |
| jupyter + ipykernel | Jupyter 环境 |

---

## 11. 文件结构快速参考

```
src/cracknuts/
├── __init__.py              # 顶层 API 导出
├── __main__.py              # CLI 入口 (click)
├── logger.py                # 日志配置
├── cracker/
│   ├── __init__.py          # 工厂函数: cracker_s1/g1/o1
│   ├── protocol.py          # CNP 协议定义 + 消息构建/解析
│   ├── cracker_basic.py     # 设备抽象基类 + ConfigBasic
│   ├── cracker_s1.py        # S1 实现 + ConfigS1
│   ├── cracker_g1.py        # G1 实现 + ConfigG1 + Glitch 命令
│   ├── cracker_o1.py        # O1 实现
│   ├── operator.py          # Operator 守护进程客户端
│   ├── cracker_manager.py   # UDP 设备发现 + IP 管理
│   ├── ssh_client.py        # SSH 客户端 + SSHCracker
│   └── serial.py            # 通信接口枚举
├── acquisition/
│   ├── __init__.py          # 工厂函数: simple_acq/simple_glitch_acq
│   ├── acquisition.py       # 采集基类 (模板方法)
│   └── glitch_acquisition.py # Glitch 采集 + SQLite 结果
├── trace/
│   ├── __init__.py          # load_trace_dataset()
│   ├── trace.py             # TraceDataset / ZarrTraceDataset / NumpyTraceDataset
│   ├── plot.py              # TracePlot (plotly-resampler)
│   └── downsample.py        # Numba min-max 降采样
├── jupyter/
│   ├── __init__.py          # show_panel() + display_xxx_panel()
│   ├── panel.py             # MsgHandlerPanelWidget (消息总线基类)
│   ├── ui_sync.py           # ConfigProxy (双向同步)
│   ├── cracknuts_panel.py   # CracknutsPanelWidget (主面板)
│   ├── cracker_s1_panel.py  # CrackerPanelWidget
│   ├── cracker_g1_panel.py  # CrackerG1Widget
│   ├── acquisition_panel.py # AcquisitionPanelWidget
│   ├── scope_panel.py       # ScopePanelWidget
│   ├── trace_panel.py       # TracePanelWidget
│   ├── glitch_test_panel.py # GlitchTestPanelWidget
│   ├── glitch_test_result_analysis_panel.py
│   ├── workbench_g1_panel.py # G1 Glitch 工作台
│   ├── config/config_glitch.py
│   └── static/              # 预编译前端 JS/CSS
├── glitch/
│   └── param_generator.py   # Glitch 参数生成器
├── scope/
│   └── scope_acquisition.py # 示波器采集
├── mock/
│   ├── mock_cracker.py      # Mock 设备
│   └── mock_operator.py     # Mock Operator
├── utils/
│   ├── hex_util.py          # 十六进制工具
│   └── user_config.py       # 用户配置
├── firmware/                # 固件文件
├── template/                # 项目模板
├── tutorials/               # 教程
└── glitch/voltage_map/      # DAC 电压映射 CSV
```
