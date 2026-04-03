---
name: cracknuts-cracker-o1-usage
description: Usage guide for CrackNuts CrackerO1 device
---

# CrackerO1 设备使用指南

## Overview

CrackerO1 是 CrackNuts 系列中用于教学的开发板，他集成了多种功能模块，适合初学者学习硬件控制和安全研究。通过连接 CrackerO1 设备，用户可以使用 Python 代码控制波形发生器、PWM 输出、寄存器操作、电压测量、示波器控制、Glitch Clock、数字 GPIO、UART/SPI 通信、LED 显示等功能。

## Workflow

1. 连接设备并确认设备信息（必须首先执行）。
2. 根据需要选择执行以下独立功能模块：
   - 波形发生器控制（正弦波、方波、三角波、锯齿波、DC、任意波形）
   - PWM 输出（风扇和电机控制）
   - 寄存器操作
   - 电压测量
   - 示波器控制
   - Glitch Clock
   - 数字 GPIO 控制
   - UART/SPI/I2C 通信
   - LED 显示（文本和图片）
   - LED HUB75 点阵屏控制
   - 开关状态查询
   - 采集面板
3. EDU 开发板教学功能：
   - 七段数码管显示
   - 红绿灯控制
   - LED 流水灯
   - LED 闪烁控制
   - 按键检测
   - I2C 光照传感器
   - SPI 温度传感器
   - UART 距离传感器
   - LED 8x8 点阵矩阵

## Examples

- `examples/cracker_o1_basic_usage.md` - CrackerO1 基础使用示例（基于 SDK 0.21.x）

## References

- `references/edu_board.md` - EDU_EV_V1 教学开发板技术参考手册（硬件功能分区、GPIO 映射、跳线逻辑及制板参数）
- `references/api_reference.md` - CrackerO1 SDK API 完整参考文档

## Notes

- 代码示例推荐在 Jupyter Notebook 中使用。