import struct

__version__ = '1.0.0'

MAGIC_STR = b'AHCC'

# ┌───────────────────────────────────────────┬───────┐
# │--------------Request Header---------------│-------│
# │Magic │Version│Direction│Command│RFU│Length│PayLoad│
# │-------------------------------------------│-------│
# │ 4B   │  2B   │   1B    │   2B  │2B │  4B  │$Length│
# │-------------------------------------------│-------│
# │'AHCC'│   1   │   'S'   │       │   │      │       │
# └───────────────────────────────────────────┴───────┘

REQ_HEADER_FORMAT = ">4sH1sHHI"
REQ_HEADER_SIZE = struct.calcsize(REQ_HEADER_FORMAT)

# ┌──────────────────────────────────────┬───────┐
# │--------------Response Header---------│-------│
# │Magic │Version│Direction│Status│Length│PayLoad│
# │--------------------------------------│-------│
# │ 4B   │  2B   │   1B    │  2B  │  4B  │$Length│
# │--------------------------------------│-------│
# │'AHCC'│   1   │   'R'   │      │      │       │
# └──────────────────────────────────────┴───────┘

RESP_HEADER_FORMAT = ">4sH1sHI"
RESP_HEADER_SIZE = struct.calcsize(RESP_HEADER_FORMAT)

DIRECTION_SEND = b'S'
DIRECTION_RESPONSE = b'R'

# Status Code
STATUS_OK = 0x0000
STATUS_BUSY = 0x0001
STATUS_ERROR = 0x8000
STATUS_UNSUPPORTED = 0x8001


def version():
    return __version__


def _build_message(direction: bytes, command: int, payload: bytes | str = None):
    if isinstance(payload, str):
        payload = bytes.fromhex(payload)

    content = struct.pack(REQ_HEADER_FORMAT, MAGIC_STR, int(__version__.split('.')[0]), direction, command, 0,
                          0 if payload is None else len(payload))
    if payload is not None:
        content += payload

    return content


def build_send_message(command: int, payload: bytes | str = None):
    return _build_message(DIRECTION_SEND, command, payload)


def build_response_message(status: int, payload: bytes | str = None):
    return _build_message(DIRECTION_RESPONSE, status, payload)
