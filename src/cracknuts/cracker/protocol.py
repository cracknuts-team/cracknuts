# Copyright 2024 CrackNuts. All rights reserved.

import struct

__version__ = "1.0.0"

DEFAULT_PORT = 9761

DEFAULT_OPERATOR_PORT = 9760

MAGIC_STR = b"CRAK"

# ┌───────────────────────────────────────────┬───────┐
# │--------------Request Header---------------│-------│
# │Magic │Version│Direction│Command│RFU│Length│PayLoad│
# │-------------------------------------------│-------│
# │ 4B   │  2B   │   1B    │   2B  │2B │  4B  │$Length│
# │-------------------------------------------│-------│
# │'CRAK'│   1   │   'S'   │       │   │      │       │
# └───────────────────────────────────────────┴───────┘

REQ_HEADER_FORMAT = ">4sH1sHHI"
REQ_HEADER_SIZE = struct.calcsize(REQ_HEADER_FORMAT)

# ┌──────────────────────────────────────┬───────┐
# │--------------Response Header---------│-------│
# │Magic │Version│Direction│Status│Length│PayLoad│
# │--------------------------------------│-------│
# │ 4B   │  2B   │   1B    │  2B  │  4B  │$Length│
# │--------------------------------------│-------│
# │'CRAK'│   1   │   'R'   │      │      │       │
# └──────────────────────────────────────┴───────┘

RES_HEADER_FORMAT = ">4sH1sHI"
RES_HEADER_SIZE = struct.calcsize(RES_HEADER_FORMAT)

DIRECTION_SEND = b"S"
DIRECTION_RESPONSE = b"R"

# Status Code
STATUS_OK = 0x0000
STATUS_BUSY = 0x0001
STATUS_ERROR = 0x8000
STATUS_UNSUPPORTED = 0x8001


def version():
    return __version__


def _build_req_message(command: int, rfu: int = 0, payload: bytes | None = None):
    content = struct.pack(
        REQ_HEADER_FORMAT,
        MAGIC_STR,
        int(__version__.split(".")[0]),
        DIRECTION_SEND,
        command,
        rfu,
        0 if payload is None else len(payload),
    )
    if payload is not None:
        content += payload

    return content


def _build_res_message(status: int, payload: bytes | None = None):
    content = struct.pack(
        RES_HEADER_FORMAT,
        MAGIC_STR,
        int(__version__.split(".")[0]),
        DIRECTION_RESPONSE,
        status,
        0 if payload is None else len(payload),
    )
    if payload is not None:
        content += payload

    return content


def build_send_message(command: int, rfu: int = 0, payload: bytes | None = None):
    return _build_req_message(command, rfu, payload)


def build_response_message(status: int, payload: bytes | None = None):
    return _build_res_message(status, payload)
