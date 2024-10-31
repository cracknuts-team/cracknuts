# Copyright 2024 CrackNuts. All rights reserved.

import urllib.request
import xml.etree.ElementTree as et
import logging
from packaging import version
import click

import cracknuts
import cracknuts.mock as mock
from cracknuts.cracker import protocol

try:
    from cracknuts_panel import __main__ as cp_main
    import cracknuts_panel

    has_cracknuts_panel = True
except ImportError:
    cp_main = None
    cracknuts_panel = None
    has_cracknuts_panel = False


@click.group(help="A library for cracker device.", context_settings=dict(max_content_width=120))
@click.version_option(version=cracknuts.__version__, message="%(version)s")
def main(): ...


@main.command(help="Start a mock cracker.")
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


if has_cracknuts_panel:

    @main.command(help="Create a jupyter notebook from template.")
    @click.option(
        "--template",
        "-t",
        help="The jupyter notebook template.",
        required=True,
        type=click.Choice(["acquisition", "analysis"]),
    )
    @click.option(
        "--new-ipynb-name",
        "-n",
        "new_ipynb_name",
        help="The jupyter notebook name or path.",
        required=True,
    )
    def create_jupyter_notebook(template: str, new_ipynb_name: str):
        _update_check()
        cp_main.create_jupyter_notebook(template, new_ipynb_name)


def _update_check():
    cracknuts_version_list_url = "https://pypi.org/rss/project/cracknuts/releases.xml"
    _do_update_check("cracknuts", cracknuts_version_list_url, cracknuts.__version__)
    if has_cracknuts_panel:
        cracknuts_panel_version_list_url = "https://pypi.org/rss/project/cracknuts-panel/releases.xml"
        _do_update_check("cracknuts-panel", cracknuts_panel_version_list_url, cracknuts_panel.__version__)


def _do_update_check(name, url, current_version):
    res = urllib.request.urlopen(url)
    content = res.read().decode("utf-8")
    root = et.fromstring(content)
    latest = root.find("./channel/item")

    latest_version = version.parse(latest.find("title").text)
    current_version = version.parse(current_version)

    if latest_version > current_version:
        RED = "\033[31m"
        GREEN = "\033[32m"
        RESET = "\033[0m"
        print(
            f"A new release of {name} is available: "
            f"{RED}{current_version}{RESET} -> {GREEN}{latest_version}{RESET}\r\n"
            f"To update, run: python.exe -m pip install --upgrade {name}\r\n"
        )


if __name__ == "__main__":
    main()
