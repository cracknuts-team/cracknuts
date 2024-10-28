# Copyright 2024 CrackNuts. All rights reserved.

import logging

import click

import cracknuts
from cracknuts.cracker import protocol
import cracknuts.mock as mock


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
    "--logging_level",
    default="INFO",
    show_default=True,
    help="The logging level of mock cracker.",
    type=click.Choice(["DEBUG", "INFO", "WARNING", "ERROR", "CRITICAL"]),
)
def start_mock_cracker(
    host: str = "127.0.0.1",
    port: int = protocol.DEFAULT_PORT,
    operator_port: int = protocol.DEFAULT_OPERATOR_PORT,
    logging_level: str | int = logging.INFO,
):
    mock.start(host, port, operator_port, logging_level)


if __name__ == "__main__":
    main()
