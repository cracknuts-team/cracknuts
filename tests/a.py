def print_bytes_matrix(b):
    # 每行显示的字节数
    BYTES_PER_LINE = 16

    # 计算总行数
    lines = (len(b) + BYTES_PER_LINE - 1) // BYTES_PER_LINE

    # 打印16进制头部
    print("         ", end="")
    for i in range(BYTES_PER_LINE):
        print(f" {i:02X}", end="")
    print("   ASCII")

    # 打印16进制矩阵和ASCII字符
    for line in range(lines):
        offset = line * BYTES_PER_LINE
        hex_line = []
        ascii_line = []

        for i in range(offset, min(len(b), offset + BYTES_PER_LINE)):
            byte = b[i]
            hex_line.append(f"{byte:02X}")
            if 32 <= byte <= 126:  # 只打印可打印的ASCII字符
                ascii_line.append(chr(byte))
            else:
                ascii_line.append(".")

        # 补齐不足16个字节的情况
        while len(hex_line) < BYTES_PER_LINE:
            hex_line.append("  ")
            ascii_line.append(" ")

        # 打印十六进制行
        hex_str = f"{offset:08X}: {' '.join(hex_line)}  | {''.join(ascii_line)}"
        print(hex_str)


# 示例bytes对象
b = b'Hello, World!\x00\x01\x02\x03\x04\x05\x06\x07\x08\t\n\x0b\x0c\x0d\x0e\x0f\x10'

# 调用函数
print_bytes_matrix(b)

print(' '.join(f'{byte:02x}' for byte in b))

i=1
print(f'{1:02x}')
