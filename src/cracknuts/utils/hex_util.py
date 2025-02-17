# Copyright 2024 CrackNuts. All rights reserved.

import math


def get_bytes_matrix(data, max_line=32, max_bytes_count=None):
    if max_bytes_count is not None:
        max_line = math.ceil(int(math.ceil(max_line / max_bytes_count)) / 2) * 2

    hex_matrix = ""

    bytes_per_line = 16

    hex_matrix += f"Total bytes: {len(data)}\n"

    hex_matrix += "          00 01 02 03 04 05 06 07  08 09 0A 0B 0C 0D 0E 0F   01234567 89ABCDEF\n"
    hex_matrix += "          ------------------------------------------------   -------- --------\n"

    data_length = len(data)
    line_count = math.ceil(data_length / bytes_per_line)
    if line_count > max_line:
        head_slice = max_line // 2 * bytes_per_line
        tail_start = (line_count - (max_line // 2)) * bytes_per_line
        tail_slice = data_length - tail_start
        data_head = data[:head_slice]
        data_tail = data[-tail_slice:]
        hex_matrix += _get_bytes_matrix(data_head, bytes_per_line)
        hex_matrix += "          .......................  .......................   ........ ........\n"
        hex_matrix += _get_bytes_matrix(data_tail, bytes_per_line, tail_start)
    else:
        hex_matrix += _get_bytes_matrix(data, bytes_per_line)

    return hex_matrix


def _get_bytes_matrix(data, bytes_per_line=16, start=0):
    hex_matrix = ""
    for i in range(0, len(data), bytes_per_line):
        chunk = data[i : i + bytes_per_line]

        hex_matrix_line = ""

        hex_matrix_line += f"{i + start:08X}: "

        hex_values = " ".join([f"{byte:02X}" for byte in chunk[:8]])
        hex_values += "  " if len(chunk) > 8 else ""
        hex_values += " ".join([f"{byte:02X}" for byte in chunk[8:]])
        hex_matrix_line += f"{hex_values:<49}"

        ascii_values = "".join([chr(byte) if 32 <= byte <= 126 else "." for byte in chunk[:8]])
        ascii_values += " " if len(chunk) > 8 else ""
        ascii_values += "".join([chr(byte) if 32 <= byte <= 126 else "." for byte in chunk[8:]])
        hex_matrix_line += f"| {ascii_values:<17} |"

        hex_matrix += hex_matrix_line + "\n"

    return hex_matrix


def get_hex(b: bytes, max_len=16):
    if b is None:
        hex_str = ""
    else:
        if len(b) > max_len:
            slice_len = max_len // 2
            hex_str = (
                f"{' '.join(f'{byte:02x}' for byte in b[:slice_len])}"
                f" .. "
                f"{' '.join(f'{byte:02x}' for byte in b[-slice_len:])}"
            )
        else:
            hex_str = f"{' '.join(f'{byte:02x}' for byte in b)}"
    return hex_str
