---
name: cracknuts-acquisition
description: Guide CrackNuts power/side‑channel trace acquisition, including Jupyter setup, device connection, acquisition workflow, dataset saving and viewing. Use when users ask about CrackNuts 功耗波形采集、trace acquisition、Cracker 连接与采集流程、或需要采集示例代码。
---

# CrackNuts 功耗波形采集

## Overview

提供 CrackNuts 侧信道功耗采集的标准流程与示例，包含上位机 Jupyter 准备、Cracker 连接、采集流程定义、面板控制、数据保存与查看。
注意：代码示例推荐在 Jupyter Notebook 中使用，以使用CrackNuts提供的交互式面板进行实时调整和监控。注意示例代码中的单元格标识，他标识推荐在Jupyter中创建的单元格，按照顺序执行以完成采集流程。

## Workflow

1. 准备 Jupyter 环境并创建 Notebook。
2. 连接 Cracker 设备并确认设备信息。
3. 定义采集流程（`init` + `do`）与参数配置。
4. 使用采集控制面板进行实时监控与采集。
5. 保存与加载数据集，查看/裁剪波形区间。

## Example

- `examples/trace-acq-stm32f10-aes.md` 中包含使用 `CrackerS1` 采集 `STM32F103` Nut 的 `AES` 功耗曲线的示例流程与代码。

## Notes

- 由于采集初始阶段或者说在Nut及Cracker参数调整阶段需要调整诸如Nut接收的指令、Cracker采集的数据点长度、曲线数量、增益等信息，建议在Jupyter中使用面板进行实时调整和监控，直到调整到合适的参数后再正式开始采集并保存数据。
