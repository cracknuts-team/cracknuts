---
name: cracknuts-intro
description: Provide a concise introduction to the CrackNuts project and its components, and summarize host SDK installation and initial setup steps from official CrackNuts docs. Use when asked to介绍CrackNuts、项目组成/部署方式、上位机SDK安装/环境准备、或需要快速上手说明。
---

# CrackNuts 项目简介与上位机安装

## 任务目标

- 输出一段清晰、简洁的 CrackNuts 项目简介（用途、能力、组成、部署特点）。
- 根据官方文档补充上位机 SDK 安装与初始使用说明。

## 关键事实

- CrackNuts 面向芯片安全分析，覆盖侧信道分析与故障注入两类能力。
- 组成三部分：`CrackNuts` 软件、`Cracker` 设备、`Nuts` 目标板。
- 细节请在需要时读取 `references/intro.md`。

## 上位机安装与初始使用

1. 优先从 `references/installation.md` 提炼安装步骤与依赖信息。
   - 若该文件缺失或内容为空，向用户索取页面内容或授权联网重新抓取。
2. 安装完成后补充 “上位机使用指南” 中的快速启动与命令行入口：
   - `cracknuts lab` 启动 Jupyter Lab
   - `cracknuts tutorials` 打开教程
   - `cracknuts create -t [template name] -n [new notebook name]` 创建新笔记
   - `cracknuts config set lab.workspace` 设置默认工作目录
3. 如需举例，给出最小可行的 Python 连接设备片段（仅在用户明确要求代码示例时提供）。

## 输出模板

1. 简介：1-2 段介绍用途 + 能力范围。
2. 组成：软件 / 设备 / 目标板三要素。
3. 部署：PoE 优势与适用场景。
4. 安装：提炼 Host SDK 安装步骤（操作系统支持、依赖、安装命令/包管理器）。
5. 快速启动：`cracknuts` 命令与 Jupyter 使用入口。

## 参考资料

- `references/intro.md`：官方简介要点与组成/部署信息
- `references/installation.md`：Host SDK 安装步骤与依赖
- `references/support.md`：官方支持渠道与问题反馈路径
