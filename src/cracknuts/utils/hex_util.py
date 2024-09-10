def get_bytes_matrix(b):
    summary = f"========  >>>>>>>> total length: {len(b)}"

    bytes_per_line = 16

    lines = (len(b) + bytes_per_line - 1) // bytes_per_line

    header = "         "
    for i in range(bytes_per_line):
        header += f" {i:02X}"
    header += "  | ASCII"

    content = ""

    for line in range(lines):
        offset = line * bytes_per_line
        hex_line = []
        ascii_line = []

        for i in range(offset, min(len(b), offset + bytes_per_line)):
            byte = b[i]
            hex_line.append(f"{byte:02X}")
            if 32 <= byte <= 126:
                ascii_line.append(chr(byte))
            else:
                ascii_line.append(".")

        while len(hex_line) < bytes_per_line:
            hex_line.append("  ")
            ascii_line.append(" ")

        content += f"{offset:08X}: {' '.join(hex_line)}  | {''.join(ascii_line)}\n"

    return summary + "\n" + header + "\n" + content


def get_hex(b: bytes):
    return " ".join(f"{byte:02x}" for byte in b)
