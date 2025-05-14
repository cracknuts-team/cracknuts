<p align="center">
  <img src="docs/static/logo.svg" alt=""/>
</p>

<p align="center">
    <a href="https://pypi.org/project/cracknuts/"><img src="https://img.shields.io/pypi/v/cracknuts.svg" /></a>
    <a href="https://github.com/cracknuts-team/cracknuts/blob/main/LICENSE"><img src="https://img.shields.io/github/license/cracknuts-team/cracknuts.svg" /></a>
    <a href="https://github.com/cracknuts-team/cracknuts/releases"><img alt="GitHub release" src="https://img.shields.io/github/release/cracknuts-team/cracknuts.svg"></a>
</p>

本仓库是`CrackNuts`项目中`Cracker`设备的控制与分析Python库。

## 安装

执行`pip install cracknuts`或`pip install cracknuts[jupyter]`，如果你在[Jupyter](https://jupyter.org/)中开发。

安装后运行`cracknuts welcome`，它将打印`cracknuts`的欢迎内容和版本信息。

```text
   ______                           __      _   __           __
  / ____/   _____  ____ _  _____   / /__   / | / /  __  __  / /_   _____
 / /       / ___/ / __ `/ / ___/  / //_/  /  |/ /  / / / / / __/  / ___/
/ /___    / /    / /_/ / / /__   / ,<    / /|  /  / /_/ / / /_   (__  )
\____/   /_/     \__,_/  \___/  /_/|_|  /_/ |_/   \__,_/  \__/  /____/

Welcome to CrackNuts(0.17.0)! 🎉

Here are some commands to get you started:

1. cracknuts tutorials - Open the tutorials to learn more about CrackNuts.
2. cracknuts lab - Launch Jupyter Lab for interactive analysis.
3. cracknuts --help - View detailed command options and usage instructions.

For more information, visit:
- Official website: https://cracknuts.io
- GitHub repository: https://github.com/cracknuts-team/cracknuts
- API documentation: https://api.cracknuts.io

Enjoy exploring CrackNuts! If you need assistance, feel free to check the documentation or ask for help.
```

以上步骤没有错误后，既是安装成功，你可以开始使用`CrackNuts`进行研究和学习。

或者，你可以使用快速安装脚本进行安装。它将安装`Miniconda`并创建一个名为`cracknuts`的环境，同时在桌面（Windows）或者启动器中上创建两个`CrackNuts`的快捷方式。

*Windows*

```shell
curl https://gitee.com/cracknuts-team/cracknuts/raw/main/install/install.ps1 -o "cracknuts-win-install.ps1"; powershell -ExecutionPolicy Bypass -File ".\cracknuts-win-install.ps1" -EnableChinaConfig; del "cracknuts-win-install.ps1"
```

*Linux*

```shell
curl -sSL https://gitee.com/cracknuts-team/cracknuts/raw/main/install/install.sh | bash -s -- --china-config
```

## 使用

访问 [CrackNuts](https://cracknuts.cn)  获取详细信息。  
