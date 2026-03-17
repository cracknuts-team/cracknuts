# Acquisition API 文档

Acquisition 模块用于控制 Trace 采集流程，支持同步/异步采集、测试模式、故障注入采集等功能。

---

## 目录

- [快速开始](#快速开始)
- [Acquisition](#acquisition) - 基础采集类
- [AcquisitionBuilder](#acquisitionbuilder) - 构建器
- [GlitchAcquisition](#glitchacquisition) - 故障注入采集
- [参数生成器](#参数生成器)
- [配置类](#配置类)

---

## 快速开始

### 基本采集流程

```python
from cracknuts import CrackerS1
from cracknuts.acquisition import Acquisition

cracker = CrackerS1()
cracker.set_addr('192.168.0.13', 8080)
cracker.connect()

# 定义初始化函数
def init(c):
    c.nut_voltage(3300)
    c.nut_enable(1)

# 定义采集函数
def do(c):
    # 执行业务逻辑并返回数据
    return {"plaintext": plaintext, "ciphertext": ciphertext}

# 使用构建器创建采集任务
acq = Acquisition.builder() \
    .cracker(cracker) \
    .init(init) \
    .do(do) \
    .build()

# 同步运行采集
acq.run_sync(trace_count=50000)
```

### 使用 GlitchAcquisition

```python
from cracknuts.cracker import CrackerG1
from cracknuts.acquisition import GlitchAcquisition
from cracknuts.glitch import VCCGlitchParamGenerator, GlitchGenerateParam

cracker = CrackerG1()
cracker.connect()

# 定义 glitch 参数生成器
glitch_params = VCCGlitchParamGenerator(
    normal=GlitchGenerateParam(mode=GlitchGenerateParam.Mode.FIXED, start=3300, end=3300, step=0, count=1),
    wait=GlitchGenerateParam(mode=GlitchGenerateParam.Mode.INCREASE, start=1, end=100, step=1, count=1),
    glitch=GlitchGenerateParam(mode=GlitchGenerateParam.Mode.INCREASE, start=1000, end=2000, step=10, count=1),
    count=GlitchGenerateParam(mode=GlitchGenerateParam.Mode.FIXED, start=1, end=1, step=0, count=1),
    repeat=GlitchGenerateParam(mode=GlitchGenerateParam.Mode.FIXED, start=1, end=1, step=0, count=1),
    interval=GlitchGenerateParam(mode=GlitchGenerateParam.Mode.FIXED, start=0, end=0, step=0, count=1),
)

# 使用 simple 方法快速创建
acq = GlitchAcquisition.simple(
    cracker=cracker,
    init_func=lambda c: init_glitch(c),
    do_func=lambda c, count: do_glitch(c, count),
    trace_count=1000
)
acq.set_glitch_test_params({"type": "vcc", "data": [...]})
acq.glitch_run()
```

---

## Acquisition

Trace 采集过程控制类。

### 常量

| 常量 | 值 | 描述 |
|------|-----|------|
| `STATUS_STOPPED` | 0 | 已停止 |
| `STATUS_TESTING` | 1 | 测试模式运行中 |
| `STATUS_RUNNING` | 2 | 正式运行中 |
| `STATUS_GLITCH_TEST_RUNNING` | 3 | 故障注入测试运行中 |
| `DO_ERROR_HANDLER_STRATEGY_EXIT` | 0 | 错误时立即退出 |
| `DO_ERROR_HANDLER_STRATEGY_CONTINUE_UNTIL_MAX_ERROR_COUNT` | 1 | 错误达到最大次数后退出 |

### 构造函数

```python
Acquisition(
    cracker: CrackerBasic,
    trace_count: int = 1000,
    sample_length: int = -1,
    sample_offset: int = 0,
    data_plaintext_length: int = None,
    data_ciphertext_length: int = None,
    data_key_length: int = None,
    data_extended_length: int = None,
    trigger_judge_wait_time: float = 0.01,
    trigger_judge_timeout: float = 1.0,
    do_error_handler_strategy: int = DO_ERROR_HANDLER_STRATEGY_EXIT,
    do_error_max_count: int = -1,
    file_format: str = "zarr",
    file_path: str = "auto",
    trace_fetch_interval: float = 0,
)
```

**参数说明:**

| 参数 | 类型 | 默认值 | 描述 |
|------|------|--------|------|
| `cracker` | `CrackerBasic` | 必填 | Cracker 设备对象 |
| `trace_count` | `int` | 1000 | 采集 trace 数量 |
| `sample_length` | `int` | -1 | 采样长度，-1 表示使用设备当前配置 |
| `sample_offset` | `int` | 0 | 采样偏移 |
| `data_plaintext_length` | `int` | None | 明文数据长度 |
| `data_ciphertext_length` | `int` | None | 密文数据长度 |
| `data_key_length` | `int` | None | 密钥数据长度 |
| `data_extended_length` | `int` | None | 扩展数据长度 |
| `trigger_judge_wait_time` | `float` | 0.01 | 触发判断等待时间（秒） |
| `trigger_judge_timeout` | `float` | 1.0 | 触发判断超时时间（秒） |
| `do_error_handler_strategy` | `int` | 0 | 错误处理策略 |
| `do_error_max_count` | `int` | -1 | 最大错误次数，-1 表示不限制 |
| `file_format` | `str` | "zarr" | 数据保存格式 ("zarr" 或 "numpy") |
| `file_path` | `str` | "auto" | 数据保存路径，"auto" 表示自动创建时间戳目录 |
| `trace_fetch_interval` | `float` | 0 | 测试模式采集中获取 trace 的间隔时间 |

### 属性

| 属性 | 类型 | 描述 |
|------|------|------|
| `trace_count` | `int` | 采集数量 |
| `sample_length` | `int` | 采样长度 |
| `sample_offset` | `int` | 采样偏移 |
| `trigger_judge_wait_time` | `float` | 触发判断等待时间 |
| `trigger_judge_timeout` | `float` | 触发判断超时时间 |
| `do_error_max_count` | `int` | 最大错误次数 |
| `file_format` | `str` | 数据保存格式 |
| `file_path` | `str` | 数据保存路径 |
| `trace_fetch_interval` | `float` | trace 获取间隔 |

### 运行方法

#### run()

后台运行采集任务。

```python
acq.run(
    count=1000,
    sample_length=1024,
    sample_offset=0,
    trigger_judge_wait_time=0.01,
    trigger_judge_timeout=1.0,
    do_error_max_count=10,
    do_error_handler_strategy=0,
    file_format="zarr",
    file_path="auto"
)
```

#### run_sync()

同步运行采集任务（阻塞）。

```python
acq.run_sync(
    count=50000,
    sample_length=1024,
    sample_offset=0,
    trigger_judge_wait_time=0.01,
    trigger_judge_timeout=1.0,
    do_error_max_count=-1,
    do_error_handler_strategy=0,
    file_format="zarr",
    file_path="auto"
)
```

#### test()

后台运行测试模式。

```python
acq.test(
    sample_length=1024,
    sample_offset=0,
    trigger_judge_wait_time=0.01,
    trigger_judge_timeout=1.0,
    do_error_max_count=10,
    do_error_handler_strategy=0,
    trace_fetch_interval=2.0
)
```

#### test_sync()

同步运行测试模式（阻塞）。

```python
acq.test_sync(
    count=-1,
    sample_length=1024,
    sample_offset=0,
    trigger_judge_wait_time=0.01,
    trigger_judge_timeout=1.0,
    do_error_max_count=10,
    do_error_handler_strategy=0
)
```

### 控制方法

| 方法 | 描述 |
|------|------|
| `pause()` | 暂停采集 |
| `resume()` | 恢复采集 |
| `stop()` | 停止采集 |

### 状态查询

| 方法 | 描述 |
|------|------|
| `get_status()` | 获取当前状态 |
| `is_running()` | 是否正在运行 |
| `get_last_wave()` | 获取最后一次采集的波形 |

### 回调方法

| 方法 | 描述 |
|------|------|
| `on_status_changed(callback)` | 状态变化回调 |
| `on_run_progress_changed(callback)` | 进度变化回调 |
| `on_wave_loaded(callback)` | 波形加载完成回调 |
| `on_config_changed(listener)` | 配置变化监听 |

### 配置方法

| 方法 | 描述 |
|------|------|
| `dump_config(path)` | 导出配置到 JSON |
| `load_config_from_file(path)` | 从文件加载配置 |
| `load_config_from_str(json_str)` | 从字符串加载配置 |

### 生命周期方法（需子类实现）

```python
# 初始化，在采集开始前调用一次
def init(self):
    # 初始化 Cracker 设备
    self.cracker.nut_voltage(3300)
    self.cracker.nut_enable(1)

# 执行，每次采集循环调用
def do(self, count: int) -> dict[str, bytes]:
    # 执行业务逻辑
    return {
        "plaintext": plaintext_data,
        "ciphertext": ciphertext_data,
        "key": key_data,       # 可选
        "extended": ext_data   # 可选
    }

# 结束，采集完成后调用
def finish(self):
    # 清理资源
    self.cracker.nut_disable()
```

---

## AcquisitionBuilder

用于构建 Acquisition 的辅助类。

### 构造函数

```python
AcquisitionBuilder()
```

### 方法

| 方法 | 描述 |
|------|------|
| `cracker(cracker)` | 指定 Cracker 设备 |
| `init(init_function)` | 设置初始化函数 |
| `do(do_function)` | 设置执行函数 |
| `finish(finish_function)` | 设置完成函数 |
| `build(**kwargs)` | 构建 Acquisition 对象 |

### 使用示例

```python
acq = Acquisition.builder() \
    .cracker(cracker) \
    .init(lambda c: init_func(c)) \
    .do(lambda c, count: do_func(c, count)) \
    .build(trace_count=1000)
```

---

## GlitchAcquisition

继承自 `Acquisition`，增加了故障注入（Glitch）功能。

### 构造函数

```python
GlitchAcquisition(
    cracker: CrackerG1,
    trace_count: int = 1000,
    shadow_trace_count: int = 1000,
    sample_length: int = -1,
    sample_offset: int = 0,
    ...
)
```

**新增参数:**

| 参数 | 类型 | 默认值 | 描述 |
|------|------|--------|------|
| `shadow_trace_count` | `int` | 1000 | 阴影采集数量 |

### 属性

| 属性 | 类型 | 描述 |
|------|------|------|
| `shadow_trace_count` | `int` | 阴影采集数量 |

### 特有方法

| 方法 | 描述 |
|------|------|
| `glitch_run(...)` | 运行故障注入采集 |
| `glitch_test_sync(...)` | 同步运行故障注入测试 |
| `set_glitch_params(param_generator)` | 设置故障注入参数生成器 |
| `set_glitch_test_params(param)` | 设置故障注入测试参数 |
| `get_glitch_test_params()` | 获取故障注入测试参数 |
| `on_glitch_result_added(callback)` | 故障结果添加回调 |

### 静态方法

```python
GlitchAcquisition.simple(
    cracker: CrackerG1,
    init_func: Callable[[CrackerG1], None],
    do_func: Callable[[CrackerG1, int], dict[str, bytes]],
    finish_func: Callable[[CrackerG1], None],
    **kwargs
) -> Acquisition
```

快速创建 GlitchAcquisition 实例的简便方法。

---

## 参数生成器

### GlitchGenerateParam

故障注入参数配置类。

```python
GlitchGenerateParam(
    mode: GlitchGenerateParam.Mode,
    start: float,
    end: float,
    step: float,
    count: int
)
```

**模式 (Mode):**

| 模式 | 值 | 描述 |
|------|-----|------|
| `INCREASE` | 0 | 递增 |
| `DECREASE` | 1 | 递减 |
| `RANDOM` | 2 | 随机 |
| `FIXED` | 3 | 固定值 |

### VCCGlitchParamGenerator

VCC 故障注入参数生成器。

```python
VCCGlitchParamGenerator(
    normal: GlitchGenerateParam,  # 正常电压
    wait: GlitchGenerateParam,    # 等待时间
    glitch: GlitchGenerateParam,  # 故障电压
    count: GlitchGenerateParam,   # 故障持续时间
    repeat: GlitchGenerateParam, # 重复次数
    interval: GlitchGenerateParam # 间隔时间
)
```

### GNDGlitchParamGenerator

GND 故障注入参数生成器，继承自 `VCCGlitchParamGenerator`。

---

## 数据类

### AcqProgress

采集进度类。

```python
AcqProgress(finished: int, total: int)
```

**属性:**

- `finished` - 已完成数量
- `total` - 总数量

### GlitchDoStatus

故障注入状态枚举。

```python
GLITCHED = 0    # 成功注入故障
NOT_GLITCHED = 1 # 未注入故障
NO_RETURN = 2    # 无返回
ERROR = 3        # 错误
```

### GlitchDoData

故障注入采集数据类。

```python
GlitchDoData(
    plaintext: bytes = None,
    ciphertext: bytes = None,
    key: bytes = None,
    extended: bytes = None,
    glitch_status: GlitchDoStatus = GlitchDoStatus.NOT_GLITCHED
)
```

### AcquisitionConfig

采集配置数据类。

```python
AcquisitionConfig(
    trace_count: int = 1,
    sample_length: int = 1024,
    sample_offset: int = 0,
    trigger_judge_timeout: float = 0.005,
    trigger_judge_wait_time: float = 0.05,
    do_error_max_count: int = 1,
    file_path: str = "",
    file_format: str = "zarr"
)
```

---

## 文件格式

### Zarr 格式

采集数据保存为 Zarr 格式目录，包含：

- 波形数据 (traces)
- 元数据 (metadata.json)

### NumPy 格式

采集数据保存为 NumPy 的 `.npy` 格式。

---

## 错误处理

### 错误策略

- `DO_ERROR_HANDLER_STRATEGY_EXIT` (0): 执行函数出错时立即退出
- `DO_ERROR_HANDLER_STRATEGY_CONTINUE_UNTIL_MAX_ERROR_COUNT` (1): 达到最大错误次数后退出

### 超时处理

- `trigger_judge_timeout`: 触发判断超时时间，如果在超时时间内未触发，则跳过当前次采集
- `trigger_judge_wait_time`: 触发判断轮询间隔时间
