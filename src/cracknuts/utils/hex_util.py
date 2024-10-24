# Copyright 2024 CrackNuts. All rights reserved.


def get_bytes_matrix(data):
    hex_matrix = ""

    bytes_per_line = 16

    hex_matrix += f"Total bytes: {len(data)}\n"

    hex_matrix += "          00 01 02 03 04 05 06 07  08 09 0A 0B 0C 0D 0E 0F   01234567 89ABCDEF\n"
    hex_matrix += "          ------------------------------------------------- -------------------\n"

    for i in range(0, len(data), bytes_per_line):
        chunk = data[i : i + bytes_per_line]

        hex_matrix_line = ""

        hex_matrix_line += f"{i:08X}: "

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


def get_hex(b: bytes):
    return " ".join(f"{byte:02x}" for byte in b)


if __name__ == "__main__":
    get_bytes_matrix(bytes(range(256)))
