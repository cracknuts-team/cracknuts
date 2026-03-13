import time

import os
import mmap
import struct

class Axi:

    AXI_PATH = "/dev/mem"

    def __init__(self, base_addr: int, size: int):
        self.base_addr = base_addr
        self.size = size

        self.fd = os.open(self.AXI_PATH, os.O_RDWR | os.O_SYNC)

        self.mem = mmap.mmap(
            self.fd,
            size,
            mmap.MAP_SHARED,
            mmap.PROT_READ | mmap.PROT_WRITE,
            offset=base_addr
        )

    def read_register(self, offset: int) -> int:
        if offset >= self.size:
            raise ValueError(
                f"AXI invalid offset {offset}, total size: {self.size}"
            )

        data = self.mem[offset:offset+4]
        return struct.unpack("<I", data)[0]

    def write_register(self, offset: int, value: int):
        if offset >= self.size:
            raise ValueError(
                f"AXI invalid offset {offset}, total size: {self.size}"
            )

        self.mem[offset:offset+4] = struct.pack("<I", value)



# AXI 基地址
BASE_ADDR = 0x43C10000
SIZE = 0x10000

# GPIO 寄存器偏移
GPIO_DIR_OFFSET = 0x194C
GPIO_OUT_OFFSET = 0x1950

# GPIO 对应位
GP4 = 4
GP5 = 5
GP6 = 6

# 初始化 AXI
axi = Axi(BASE_ADDR, SIZE)

# GPIO 模拟 digital_pin_mode / digital_write
def pin_mode(bit: int, mode: str):
    """
    mode: "OUTPUT" or "INPUT"
    """
    dir_val = axi.read_register(GPIO_DIR_OFFSET)
    if mode.upper() == "OUTPUT":
        dir_val &= ~(1 << bit)
    else:
        dir_val |= (1 << bit)
    axi.write_register(GPIO_DIR_OFFSET, dir_val)

def digital_write(bit: int, value: int):
    out_val = axi.read_register(GPIO_OUT_OFFSET)
    if value:
        out_val |= (1 << bit)
    else:
        out_val &= ~(1 << bit)
    axi.write_register(GPIO_OUT_OFFSET, out_val)


# 初始化 595
def led595_init():
    for bit in [GP4, GP5, GP6]:
        pin_mode(bit, "OUTPUT")
        digital_write(bit, 0)

def shift_bit(bit):
    digital_write(GP4, bit)   # DATA
    digital_write(GP6, 1)     # CLK
    digital_write(GP6, 0)

def shift_16bit(value):
    for i in range(15, -1, -1):
        shift_bit((value >> i) & 1)
    digital_write(GP5, 1)   # LATCH
    digital_write(GP5, 0)


def display_matrix(matrix, t):
    # delay = 0.0001
    # count = t / delay
    for _ in range(int(t)):
        for row in range(8):
            data = matrix[row]          # 列数据
            row_sel = 1 << row          # 行选择
            value = (row_sel << 8) | data
            shift_16bit(value)
        # time.sleep(delay)


# 主程序
if __name__ == "__main__":
    led595_init()
    digits = {
        0: [
            0b11000011, 
            0b10111101, 
            0b10011101, 
            0b10101101, 
            0b10110101, 
            0b10111001, 
            0b10111101, 
            0b11000011, 
        ],
        1: [
            0b11100111, 
            0b11100011, 
            0b11100111, 
            0b11100111,
            0b11100111,
            0b11100111,
            0b11100111,
            0b10000001, 
        ],
        2: [
            0b11000011,
            0b10111101,
            0b10111111, 
            0b11011111, 
            0b11110111, 
            0b11111011, 
            0b11101111, 
            0b10000001,
        ],
        3: [
            0b11000011,
            0b10111101,
            0b10111111, 
            0b11000111, 
            0b10111111, 
            0b10111111,
            0b10111101,
            0b11000011,
        ],
        4: [
            0b11011111, 
            0b11001111, 
            0b11010111, 
            0b11011011, 
            0b11011101, 
            0b10000001,
            0b11011111, 
            0b11011111,
        ],
        5: [
            0b10000001,
            0b11111101, 
            0b11111101,
            0b11000001, 
            0b10111111, 
            0b10111111,
            0b10111101,
            0b11000011,
        ],
        6: [
            0b11000011,
            0b10111101,
            0b11111101, 
            0b11000001, 
            0b10111101,
            0b10111101,
            0b10111101,
            0b11000011,
        ],
        7: [
            0b10000001,
            0b10111111, 
            0b11011111, 
            0b11101111, 
            0b11110111, 
            0b11111011, 
            0b11111101, 
            0b11111101,
        ],
        8: [
            0b11000011,
            0b10111101,
            0b10111101,
            0b11000011,
            0b10111101,
            0b10111101,
            0b10111101,
            0b11000011,
        ],
        9: [
            0b11000011,
            0b10111101,
            0b10111101,
            0b10000011, 
            0b10111111, 
            0b10111111,
            0b10111101,
            0b11000011,
        ]
    }
    for i in range(10):
        display_matrix(digits[i], 200)
    # clear led
    display_matrix(
        [
            0b11111111,
            0b11111111,
            0b11111111,
            0b11111111,
            0b11111111,
            0b11111111,
            0b11111111,
            0b11111111,
            0b11111111
        ], 1
    )
