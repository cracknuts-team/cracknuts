# Copyright 2024 CrackNuts. All rights reserved.

from enum import Enum


class Stopbits(Enum):
    STOPBITS_ONE, STOPBITS_ONE_POINT_FIVE, STOPBITS_TWO = 0, 1, 2


class Parity(Enum):
    PARITY_NONE, PARITY_EVEN, PARITY_ODD, PARITY_MARK, PARITY_SPACE = 0, 1, 2, 3, 4


class Bytesize(Enum):
    FIVEBITS, SIXBITS, SEVENBITS, EIGHTBITS = 5, 6, 7, 8


class Baudrate(Enum):
    BAUDRATE_9600, BAUDRATE_19200, BAUDRATE_38400, BAUDRATE_57600, BAUDRATE_115200, BAUDRATE_1000000 = 0, 1, 2, 3, 4, 5


class SpiCpol(Enum):
    SPI_CPOL_LOW, SPI_CPOL_HIGH = 0, 1


class SpiCpha(Enum):
    SPI_CPHA_LOW, SPI_CPHA_HIGH = 0, 1


class I2cSpeed(Enum):
    STANDARD_100K, FAST_400K, FAST_PLUS_1M, HIGH_SPEED_3400K, ULTRA_FAST_5M = 0, 1, 2, 3, 4
