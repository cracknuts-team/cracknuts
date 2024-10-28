import logging
import threading
import time

from cracknuts.cracker import protocol
from cracknuts.mock.mock_cracker import MockCracker
from cracknuts.mock.mock_operator import MockOperator


def start(
    host: str = "127.0.0.1",
    port: int = protocol.DEFAULT_PORT,
    operator_port: int = protocol.DEFAULT_OPERATOR_PORT,
    logging_level: str | int = logging.INFO,
):
    cracker = MockCracker(host, port, logging_level)
    cracker_thread = threading.Thread(target=cracker.start)
    cracker_thread.start()

    operator = MockOperator(host, operator_port, logging_level)
    operator_thread = threading.Thread(target=operator.start)
    operator_thread.start()

    print(f"Mock cracker start success, cracker server listen on {port} and operator listen on {operator_port}.")

    try:
        while cracker_thread.is_alive() or operator_thread.is_alive():
            time.sleep(0.3)
    except KeyboardInterrupt:
        cracker.stop()
        operator.stop()


if __name__ == "__main__":
    start()
