# Copyright 2024 CrackNuts. All rights reserved.

import logging
import threading
import time

from cracknuts.cracker import protocol
from cracknuts.mock.mock_cracker import MockCracker


def start(
    host: str = "127.0.0.1",
    port: int = protocol.DEFAULT_PORT,
    logging_level: str | int = logging.INFO,
):
    cracker = MockCracker(host, port, logging_level)
    cracker_thread = threading.Thread(target=cracker.start)
    cracker_thread.start()
    print(f"Mock cracker start success, cracker server listen on {port}.")
    try:
        while cracker_thread.is_alive():
            time.sleep(0.3)
    except KeyboardInterrupt:
        cracker.stop()


if __name__ == "__main__":
    start()
