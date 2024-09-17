def get_bytes_matrix(data):
    # 每行打印16个字节
    bytes_per_line = 16

    # 显示字节总长度
    print(f"Total bytes: {len(data)}")
    print()

    # 打印header行

    print("          00 01 02 03 04 05 06 07  08 09 0A 0B 0C 0D 0E 0F   01234567 89ABCDEF")
    print("          ------------------------------------------------- -------------------")

    for i in range(0, len(data), bytes_per_line):
        # 获取当前行的字节
        chunk = data[i : i + bytes_per_line]

        # 打印偏移量
        print(f"{i:08X}: ", end="")

        # 打印16进制值,每8个字节之间增加一个空格
        hex_values = " ".join([f"{byte:02X}" for byte in chunk[:8]])
        hex_values += "  " if len(chunk) > 8 else ""
        hex_values += " ".join([f"{byte:02X}" for byte in chunk[8:]])
        print(f"{hex_values:<49}", end="")

        # 打印ASCII字符,每8个字符之间增加一个空格
        ascii_values = "".join([chr(byte) if 32 <= byte <= 126 else "." for byte in chunk[:8]])
        ascii_values += " " if len(chunk) > 8 else ""
        ascii_values += "".join([chr(byte) if 32 <= byte <= 126 else "." for byte in chunk[8:]])
        print(f"| {ascii_values} |")


def get_hex(b: bytes):
    return " ".join(f"{byte:02x}" for byte in b)


if __name__ == "__main__":
    get_bytes_matrix(bytes(range(256)))
