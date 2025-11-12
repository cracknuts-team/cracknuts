# Copyright 2024 CrackNuts. All rights reserved.

from numba import prange, njit
from numpy.typing import NDArray
import numpy as np


@njit(parallel=True, cache=True)
def minmax(value: NDArray[np.int16], mn: int, mx: int, down_count: int) -> tuple[NDArray[np.int32], NDArray[np.int16]]:
    mn = max(0, mn)
    mx = min(value.shape[0], mx)
    ds = max(1, int((mx - mn) / down_count))
    if ds == 1:
        _index = np.arange(mn, mx, dtype=np.int32)
        _value = value[mn:mx]
        return _index, _value
    sample_count = (mx - mn) // ds
    down_index = np.empty(sample_count * 2, dtype=np.int32)
    down_value = np.empty(sample_count * 2, dtype=np.int16)

    for i in prange(sample_count):
        start = mn + i * ds
        end = start + ds
        block = value[start:end]

        down_index[2 * i] = start
        down_index[2 * i + 1] = start
        down_value[2 * i] = block.max()
        down_value[2 * i + 1] = block.min()
    return down_index, down_value
