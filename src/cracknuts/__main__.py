# Copyright 2024 CrackNuts. All rights reserved.

import json
import logging
import os
import shutil
import subprocess
import sys
import textwrap
from datetime import datetime, timedelta
from importlib.resources import files
from pathlib import Path
from packaging import version
import click
import urllib.request
import cracknuts
import cracknuts.mock as mock
from cracknuts.cracker.cracker_basic import CrackerBasic
from cracknuts.cracker import protocol
from cracknuts.utils import user_config


@click.group(help="A library for cracker device.", context_settings=dict(max_content_width=120))
@click.version_option(version=cracknuts.__version__, message="%(version)s")
def main(): ...


@main.group(name="config", help="Get and set cracknuts options.")
def config(): ...


@config.command(name="get", help="Get cracknuts options.")
@click.argument("key")
def config_get(key):
    print(user_config.get_option(key))


@config.command(name="set", help="Set cracknuts options.")
@click.argument("key")
@click.argument("value")
def config_set(key, value):
    user_config.set_option(key, value)


@config.command(name="unset", help="Delete the cracknuts options.")
@click.argument("key")
def config_unset(key):
    user_config.unset_option(key)


@main.command(name="lab", help="Start jupyter lab")
@click.option("--workspace", show_default=True, help="Working directory")
def start_lab(workspace: str = None):
    _update_check()
    if workspace is None:
        workspace = user_config.get_option("lab.workspace", ".")
    try:
        subprocess.run(["jupyter", "lab", "--ServerApp.root_dir", workspace], check=True)
    except subprocess.CalledProcessError as e:
        print(f"Start Jupyter Lab failed: {e}")


@main.command(name="tutorials", help="Start tutorials.")
def start_tutorials():
    tutorials_path = str(Path(sys.modules["cracknuts"].__file__).parent.joinpath("tutorials").as_posix())
    try:
        subprocess.run(["jupyter", "notebook", "--notebook-dir", tutorials_path], check=True)
    except subprocess.CalledProcessError as e:
        print(f"Start Jupyter Lab failed: {e}")


@main.command(name="create", help="Create a jupyter notebook from template.")
@click.option(
    "--template",
    "-t",
    help="The jupyter notebook template.",
    required=False,
    type=click.Choice(["acquisition", "analysis"]),
)
@click.option(
    "--new-ipynb-name",
    "-n",
    help="The jupyter notebook name or path.",
    required=False,
)
def create_jupyter_notebook(template: str, new_ipynb_name: str):
    _update_check()
    template_dir = Path(sys.modules["cracknuts"].__file__).parent.joinpath("template")
    if template is None:
        print("Available templates:")
        for t in template_dir.glob("*.ipynb"):
            print(f"\t{t.name[:-6]}")
        return
    if new_ipynb_name is None:
        new_ipynb_name = f"{template}_{datetime.now().timestamp():.0f}.ipynb"

    template = files("cracknuts.template").joinpath(f"{template}.ipynb")
    if not new_ipynb_name.endswith(".ipynb"):
        new_ipynb_name += ".ipynb"

    new_ipynb_path = Path(new_ipynb_name)
    if not new_ipynb_path.is_absolute():
        new_ipynb_path = Path.cwd().joinpath(new_ipynb_name)
    new_ipynb_path.parent.mkdir(parents=True, exist_ok=True)

    shutil.copy(template.as_posix(), new_ipynb_path.as_posix())
    _open_jupyter(new_ipynb_path.as_posix())


@main.command(name="mock", help="Start a mock cracker.")
@click.option("--host", default="127.0.0.1", show_default=True, help="The host to attach to.")
@click.option("--port", default=protocol.DEFAULT_PORT, show_default=True, help="The port to attach to.", type=int)
@click.option(
    "--logging-level",
    default="INFO",
    show_default=True,
    help="The logging level of mock cracker.",
    type=click.Choice(["DEBUG", "INFO", "WARNING", "ERROR", "CRITICAL"], case_sensitive=True),
)
def start_mock_cracker(
    host: str = "127.0.0.1",
    port: int = protocol.DEFAULT_PORT,
    logging_level: str | int = logging.INFO,
):
    _update_check()
    mock.start(host, port, logging_level)


@main.command(name="discover", help="Discover cracknuts devices on the local network.")
@click.option("--broadcast", default="255.255.255.255", show_default=True, help="Broadcast address.")
@click.option("--scan-interval", default=3.0, show_default=True, type=float, help="Scan interval in seconds.")
@click.option(
    "--offline-grace",
    default=15.0,
    show_default=True,
    type=float,
    help="Offline grace period in seconds.",
)
@click.option("--timeout", "device_timeout", default=60.0, show_default=True, type=float, help="Device timeout.")
@click.option("--json-output", is_flag=True, help="Print discovered devices as JSON.")
def discover_devices(
    broadcast: str,
    scan_interval: float,
    offline_grace: float,
    device_timeout: float,
    json_output: bool,
):
    _update_check()
    devices = cracknuts.discover_devices(
        broadcast=broadcast,
        scan_interval=scan_interval,
        offline_grace=offline_grace,
        device_timeout=device_timeout,
    )
    if json_output:
        print(json.dumps(devices, indent=2, ensure_ascii=False))
        return

    print(f"{'MAC':17}  {'IP':15}  {'HOSTNAME':20}  STATUS")
    print("-" * 72)
    for device in devices:
        print(
            f"{device.get('mac', ''):17}  {device.get('ip', ''):15}  "
            f"{device.get('hostname', ''):20}  {device.get('status', '')}"
        )


@main.command(name="set-ip", help="Set the IP address of a cracknuts device.")
@click.argument("target_ip")
@click.argument("new_ip")
@click.option("--mask", default=None, help="Subnet mask or prefix length. Defaults to current device setting.")
@click.option("--gateway", default=None, help="Default gateway. Defaults to current device setting.")
@click.option("--delay", "delay_ms", default=200, show_default=True, type=int, help="Apply delay in ms.")
@click.option("--broadcast", default="255.255.255.255", show_default=True, help="Broadcast address.")
@click.option("--json-output", is_flag=True, help="Print ACK as JSON.")
def set_device_ip(
    target_ip: str,
    new_ip: str,
    mask: str | None,
    gateway: str | None,
    delay_ms: int,
    broadcast: str,
    json_output: bool,
):
    _update_check()
    ack = CrackerBasic.set_device_ip(
        target_ip=target_ip,
        new_ip=new_ip,
        mask=mask,
        gateway=gateway,
        delay_ms=delay_ms,
        broadcast=broadcast,
    )
    if json_output:
        print(json.dumps(ack, indent=2, ensure_ascii=False))
    else:
        print(ack)


@main.command(name="welcome", help="Welcome to cracknuts.")
def welcome():
    # ruff: noqa: W293 W291
    welcome_str = rf"""
       ______                           __      _   __           __         
      / ____/   _____  ____ _  _____   / /__   / | / /  __  __  / /_   _____
     / /       / ___/ / __ `/ / ___/  / //_/  /  |/ /  / / / / / __/  / ___/
    / /___    / /    / /_/ / / /__   / ,<    / /|  /  / /_/ / / /_   (__  ) 
    \____/   /_/     \__,_/  \___/  /_/|_|  /_/ |_/   \__,_/  \__/  /____/  
                                                        
    Welcome to CrackNuts({cracknuts.version()})! 🎉
    
    Here are some commands to get you started:
    
    1. cracknuts tutorials - Open the tutorials to learn more about CrackNuts.
    2. cracknuts lab - Launch Jupyter Lab for interactive analysis.
    3. cracknuts --help - View detailed command options and usage instructions.
    
    For more information, visit:
    - Official website: https://cracknuts.io
    - GitHub repository: https://github.com/cracknuts-team/cracknuts
    - API documentation: https://api.cracknuts.io
    
    Enjoy exploring CrackNuts! If you need assistance, feel free to check the documentation or ask for help.
    """

    print(textwrap.dedent(welcome_str))


def _open_jupyter(ipynb_file: str):
    subprocess.run(["jupyter", "lab", ipynb_file])


def _update_check():
    time_format = "%Y-%m-%d %H:%M:%S"
    current_version = version.parse(cracknuts.__version__)
    latest_version = None
    version_check_path = os.path.join(os.path.expanduser("~"), ".cracknuts", "version_check")
    if os.path.exists(version_check_path):
        try:
            with open(version_check_path) as f:
                last_version_json = json.loads("".join(f.readlines()))
            last_check_time = datetime.strptime(last_version_json["last_check_time"], time_format)
            if datetime.now() - last_check_time < timedelta(days=1):
                latest_version = version.parse(last_version_json["version"])
        except Exception as e:
            print(f"Check update file failed: {e.args}")
    if latest_version is None:
        try:
            res = urllib.request.urlopen("https://cracknuts.cn/api/version/latest")
            version_meta = json.loads(res.read().decode())
            latest_version = version.parse(version_meta["version"])
        except Exception as e:
            print(f"Failed to get latest version: {e}")
            return

    with open(version_check_path, "w") as f:
        json.dump(
            {"version": str(latest_version), "last_check_time": datetime.strftime(datetime.now(), time_format)}, f
        )

    if latest_version > current_version:
        RED = "\033[31m"
        GREEN = "\033[32m"
        RESET = "\033[0m"
        print(
            f"A new release of cracknuts is available: "
            f"{RED}{current_version}{RESET} -> {GREEN}{latest_version}{RESET}\r\n"
            f"To update, run: python.exe -m pip install --upgrade cracknuts\r\n"
        )


if __name__ == "__main__":
    main()
