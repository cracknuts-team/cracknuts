# Host SDK 安装

来源：`https://cracknuts.io/docs/getting-started/host-sdk-installation`（版本：0.19.0，抓取时间：2026-03-12）

## 概览

- 上位机 SDK 基于 Python，默认集成 Jupyter，并内置设备控制与数据采集组件。
- 也可在非 Jupyter 环境下使用标准 Python 脚本控制设备。
- 具备基础 Python 编程知识即可使用。
- 安装方式两种：快速命令安装，或 PIP 安装。

## 快速命令安装

适用场景：系统中没有 Python 环境或没有虚拟环境时推荐。

安装后自动执行：

- 安装 Miniconda（若已安装则复用）
- 创建名为 `cracknuts` 的 Conda 虚拟环境，指定 Python 版本为 `12.3`
- 安装 CrackNuts 依赖（最新稳定版）
- 创建两个桌面快捷方式：`CrackNuts` 和 `CrackNuts Tutorials`

支持系统：Windows / Linux。macOS 将在后续版本支持。

国内用户可使用“国内网络推荐脚本”，自动配置 conda 与 pip 镜像以加速下载。

**Windows PowerShell**

```powershell
curl https://raw.githubusercontent.com/cracknuts-team/cracknuts/refs/heads/main/install/win-install.ps1 -o "cracknuts-win-install.ps1"; powershell -ExecutionPolicy Bypass -File ".\cracknuts-win-install.ps1"; del "cracknuts-win-install.ps1"
```

国内网络推荐脚本：

```powershell
curl https://gitee.com/cracknuts-team/cracknuts/raw/main/install/install.ps1 -o "cracknuts-win-install.ps1"; powershell -ExecutionPolicy Bypass -File ".\cracknuts-win-install.ps1" -EnableChinaConfig; del "cracknuts-win-install.ps1"
```

**Linux Shell**

```sh
curl -sSL https://raw.githubusercontent.com/cracknuts-team/cracknuts/refs/heads/main/install/install.sh | bash
```

国内网络推荐脚本：

```sh
curl -sSL https://gitee.com/cracknuts-team/cracknuts/raw/main/install/install.sh | bash -s -- --china-config
```

**macOS**

```text
TODO
```

## PIP 安装

建议使用虚拟环境安装，避免污染系统 Python。

环境需要：

- Python 3.12.5 或以上
- 如需在已有 Jupyter 环境中使用，Jupyter 版本需满足以下最低要求

```
IPython          : 8.28.0
ipykernel        : 6.29.5
ipywidgets       : 8.1.5
jupyter_client   : 8.6.3
jupyter_core     : 5.7.2
jupyter_server   : 2.14.2
jupyterlab       : 4.2.5
nbclient         : 0.10.0
nbconvert        : 7.16.4
nbformat         : 5.10.4
notebook         : 7.2.2
traitlets        : 5.14.3
```

安装：

```sh
pip install cracknuts[jupyter]
```

如果已在现有 Jupyter 环境中使用，仅安装核心库：

```sh
pip install cracknuts
```

安装成功后可执行：

```sh
cracknuts welcome
```

## 更新

```sh
pip install -U cracknuts[jupyter]
```

若国内镜像缺少最新版本，可指定 pypi：

```sh
pip install -i https://pypi.org/simple -U cracknuts[jupyter]
```
