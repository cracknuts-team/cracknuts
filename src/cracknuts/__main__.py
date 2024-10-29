# Copyright 2024 CrackNuts. All rights reserved.

import logging

import click

import cracknuts
import cracknuts.mock as mock
from cracknuts.cracker import protocol

try:
    from cracknuts_panel import __main__ as cp_main

    has_cracknuts_panel = True
except ImportError:
    cp_main = None
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
        cp_main.create_jupyter_notebook(template, new_ipynb_name)


if __name__ == "__main__":
    main()
