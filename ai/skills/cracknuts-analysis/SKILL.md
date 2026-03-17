---
name: cracknuts-analysis
description: CrackNuts 功耗曲线侧信道分析技能。指导在 Jupyter 中加载 .zarr 数据集，使用 scarr 做 CPA 分析、输出候选密钥与相关性峰值验证。具体操作示例见 examples。
---

# CrackNuts Trace Analysis

## Overview

用于对 CrackNuts 采集回来的功耗曲线数据做侧信道分析（CPA），输出候选密钥并做相关性峰值验证与可视化。

## Workflow

1. 在 Jupyter 中指定 `.zarr` 数据集路径并加载。
2. 配置 `scarr`：`TraceHandler` + `CPA` + `SboxWeight`。
3. 运行 `container.run()` 得到候选密钥与相关性结果。
4. 通过峰值排序与可视化验证候选正确性。

## Examples

- `examples/stm32f103-aes.md` STM32F103 + AES 侧信道分析完整示例（含数据加载、CPA、候选密钥、相关性绘图）。
