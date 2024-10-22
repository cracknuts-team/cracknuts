# Copyright 2024 CrackNuts. All rights reserved.

import logging

import click

import cracknuts
from cracknuts.cracker import protocol
from cracknuts.cracker.mock_cracker import MockCracker


@click.group(help="A library for cracker device.")
@click.version_option(version=cracknuts.__version__, message="%(version)s")
def main(): ...


@main.command(help="Start a mock cracker.")
@click.option("--host", default="127.0.0.1", show_default=True, help="The host to attach to.")
@click.option("--port", default=protocol.DEFAULT_PORT, show_default=True, help="The port to attach to.", type=int)
@click.option(
    "--logging_level",
    default="INFO",
    show_default=True,
    help="The logging level of mock cracker.",
    type=click.Choice(["DEBUG", "INFO", "WARNING", "ERROR", "CRITICAL"]),
)
def start_mock_cracker(
    host: str = "127.0.0.1", port: int = protocol.DEFAULT_PORT, logging_level: str | int = logging.INFO
):
    mock_cracker = MockCracker(host, port, logging_level)
    mock_cracker.start()


if __name__ == "__main__":
    main()
