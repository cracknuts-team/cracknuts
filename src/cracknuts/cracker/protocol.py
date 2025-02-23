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
STATUS_COMMAND_UNSUPPORTED = 0x8001
STATUS_NUT_TIMEOUT = 0x8002
STATUS_ANALOG_CHANNEL_NONE_DATA = 0x8003
STATUS_DIGITAL_CHANNEL_NONE_DATA = 0x8004

STATUS_DESCRIPTION = {
    STATUS_OK: "OK",
    STATUS_BUSY: "BUSY",
    STATUS_ERROR: "ERROR",
    STATUS_COMMAND_UNSUPPORTED: "COMMAND UNSUPPORTED",
    STATUS_NUT_TIMEOUT: "NUT EXECUTE TIMEOUT",
    STATUS_ANALOG_CHANNEL_NONE_DATA: "ANALOG CHANNEL HAVE NO DATA",
    STATUS_DIGITAL_CHANNEL_NONE_DATA: "DIGITAL CHANNEL HAVE NO DATA",
}


def version():
    return __version__


class Command:
    """
    The generic command proxy configuration class defines the `CNP` communication code for general devices.
    For details, refer to the `CNP` protocol documentation.

    """

    GET_ID = 0x0001
    GET_NAME = 0x0002
    GET_VERSION = 0x0003

    CRACKER_READ_REGISTER = 0x0004
    CRACKER_WRITE_REGISTER = 0x0005

    SET_LOGGING_LEVEL = 0x0006

    OSC_ANALOG_CHANNEL_ENABLE = 0x0100
    OSC_ANALOG_COUPLING = 0x0101
    OSC_ANALOG_VOLTAGE = 0x0102
    OSC_ANALOG_BIAS_VOLTAGE = 0x0103
    OSC_ANALOG_GAIN = 0x0104
    OSC_ANALOG_GAIN_RAW = 0x0105
    OSC_CLOCK_BASE_FREQ_MUL_DIV = 0x0106
    OSC_CLOCK_SAMPLE_DIVISOR = 0x0107
    OSC_CLOCK_SAMPLE_PHASE = 0x0108
    OSC_CLOCK_NUT_DIVISOR = 0x0109
    OSC_CLOCK_UPDATE = 0x10A
    OSC_CLOCK_SIMPLE = 0x10B

    OSC_DIGITAL_CHANNEL_ENABLE = 0x0110
    OSC_DIGITAL_VOLTAGE = 0x0111

    OSC_TRIGGER_MODE = 0x0151

    OSC_ANALOG_TRIGGER_SOURCE = 0x0150
    OSC_DIGITAL_TRIGGER_SOURCE = 0x0122

    OSC_TRIGGER_EDGE = 0x0152
    OSC_TRIGGER_EDGE_LEVEL = 0x0153

    OSC_ANALOG_TRIGGER_VOLTAGE = 0x0123

    OSC_SAMPLE_DELAY = 0x0124

    OSC_SAMPLE_LENGTH = 0x0125
    OSC_SAMPLE_RATE = 0x0128

    OSC_SINGLE = 0x0126

    OSC_IS_TRIGGERED = 0x0127
    OSC_FORCE = 0x0129

    OSC_GET_ANALOG_WAVES = 0x0130
    OSC_GET_DIGITAL_WAVES = 0x0130

    NUT_ENABLE = 0x0200
    NUT_VOLTAGE = 0x0201
    NUT_VOLTAGE_RAW = 0x0203
    NUT_CLOCK_ENABLE = 0x0204
    NUT_CLOCK = 0x0202
    NUT_INTERFACE = 0x0210
    NUT_TIMEOUT = 0x0224

    CRACKER_SERIAL_BAUD = 0x0220
    CRACKER_SERIAL_WIDTH = 0x0221
    CRACKER_SERIAL_STOP = 0x0222
    CRACKER_SERIAL_ODD_EVE = 0x0223
    CRACKER_SERIAL_DATA = 0x022A

    CRACKER_SPI_CPOL = 0x0230
    CRACKER_SPI_CPHA = 0x0231
    CRACKER_SPI_DATA_LEN = 0x0232
    CRACKER_SPI_FREQ = 0x0233
    CRACKER_SPI_TIMEOUT = 0x0234
    CRACKER_SPI_DATA = 0x023A
    CRACKER_SPI_TRANSCEIVE = 0x023C
    CRACKER_SPI_ENABLE = 0x023D
    CRACKER_SPI_RESET = 0x023E
    CRACKER_SPI_CONFIG = 0x023F

    CRACKER_I2C_FREQ = 0x0240
    CRACKER_I2C_TIMEOUT = 0x0244
    CRACKER_I2C_TRANSCEIVE = 0x024A
    CRACKER_I2C_ENABLE = 0x024B
    CRACKER_I2C_RESET = 0x024C
    CRACKER_I2C_CONFIG = 0x024D

    CRACKER_UART_ENABLE = 0x0260
    CRACKER_UART_RESET = 0x0261
    CRACKER_UART_CONFIG = 0x0262
    CRACKER_UART_TRANSCEIVE = 0x0263
    CRACKER_UART_RECEIVE_FIFO_REMAINED = 0x0264
    CRACKER_UART_CRACKER_UART_RECEIVE_FIFO_DUMP = 0x0265
    CRACKER_UART_CRACKER_UART_RECEIVE_CLEAR = 0x0266

    CRACKER_CAN_FREQ = 0x0250
    CRACKER_CAN_TIMEOUT = 0x0254
    CRACKER_CA_DATA = 0x025A

    GET_BITSTREAM_VERSION = 0x0007


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
