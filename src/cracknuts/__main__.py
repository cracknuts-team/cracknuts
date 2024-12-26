# Copyright 2024 CrackNuts. All rights reserved.

import logging
import shutil
import subprocess
import sys
from datetime import datetime
from importlib.resources import files
from pathlib import Path

import click

import cracknuts
import cracknuts.mock as mock
from cracknuts.cracker import protocol


@click.group(help="A library for cracker device.", context_settings=dict(max_content_width=120))
@click.version_option(version=cracknuts.__version__, message="%(version)s")
def main(): ...


@main.command(name="lab", help="Start jupyter lab")
@click.option("--workspace", default=".", show_default=True, help="Working directory")
def start_lab(workspace: str = "."):
    _update_check()
    try:
        subprocess.run(["jupyter", "lab", "--notebook-dir", workspace], check=True)
    except subprocess.CalledProcessError as e:
        print(f"Start Jupyter Lab failed: {e}")


@main.command(name="tutorials", help="Start tutorials")
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
    "--operator_port",
    default=protocol.DEFAULT_OPERATOR_PORT,
    show_default=True,
    help="The operator port to attach to.",
    type=int,
)
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
    operator_port: int = protocol.DEFAULT_OPERATOR_PORT,
    logging_level: str | int = logging.INFO,
):
    _update_check()
    mock.start(host, port, operator_port, logging_level)


def _open_jupyter(ipynb_file: str):
    subprocess.run(["jupyter", "lab", ipynb_file])


def _update_check():
    ...
    # time_format = "%Y-%m-%d %H:%M:%S"
    # current_version = version.parse(cracknuts.__version__)
    # latest_version = None
    # version_check_path = os.path.join(os.path.expanduser("~"), ".cracknuts", "version_check")
    # if os.path.exists(version_check_path):
    #     last_version_json = json.loads(open(version_check_path).read())
    #     last_check_time = datetime.strptime(last_version_json["last_check_time"], time_format)
    #     if datetime.now() - last_check_time < timedelta(days=1):
    #         latest_version = version.parse(last_version_json["version"])
    # if latest_version is None:
    #     try:
    #         res = urllib.request.urlopen("https://cracknuts.cn/api/version/latest")
    #         version_meta = json.loads(res.read().decode())
    #         latest_version = version.parse(version_meta["version"])
    #     except Exception as e:
    #         print(f"Failed to get latest version: {e}")
    #         return
    #
    # if latest_version > current_version:
    #     RED = "\033[31m"
    #     GREEN = "\033[32m"
    #     RESET = "\033[0m"
    #     print(
    #         f"A new release of cracknuts is available: "
    #         f"{RED}{current_version}{RESET} -> {GREEN}{latest_version}{RESET}\r\n"
    #         f"To update, run: python.exe -m pip install --upgrade cracknuts\r\n"
    #     )


if __name__ == "__main__":
    main()
