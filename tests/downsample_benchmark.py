import numpy as np

def down_sample(value: np.ndarray, mn, mx, down_count) -> tuple[np.ndarray, np.ndarray]:
    mn = max(0, mn)
    mx = min(value.shape[0], mx)

    _value = value[mn:mx]
    _index = np.arange(mn, mx).astype(np.int32)

    ds = int(max(1, int(mx - mn) / down_count))

    if ds == 1:
        return _index, _value
    sample_count = int((mx - mn) // ds)

    down_index = np.empty((sample_count, 2), dtype=np.int32)
    down_index[:] = _index[: sample_count * ds : ds, np.newaxis]

    _value = _value[: sample_count * ds].reshape((sample_count, ds))
    down_value = np.empty((sample_count, 2))
    down_value[:, 0] = _value.max(axis=1)
    down_value[:, 1] = _value.min(axis=1)

    return down_index.reshape(sample_count * 2), down_value.reshape(sample_count * 2)

import numpy as np

def down_sample_opt(value: np.ndarray, mn, mx, down_count) -> tuple[np.ndarray, np.ndarray]:
    mn = max(0, mn)
    mx = min(value.shape[0], mx)

    _value = value[mn:mx]
    _index = np.arange(mn, mx, dtype=np.int32)

    ds = max(1, (mx - mn) // down_count)
    if ds == 1:
        return _index, _value

    sample_count = (mx - mn) // ds

    # 截取整块数据
    v = _value[:sample_count * ds].reshape(sample_count, ds)
    i = _index[:sample_count * ds].reshape(sample_count, ds)

    # 计算每块最大最小值
    max_val = v.max(axis=1)
    min_val = v.min(axis=1)

    max_idx = i[np.arange(sample_count), v.argmax(axis=1)]
    min_idx = i[np.arange(sample_count), v.argmin(axis=1)]

    # 拼接成一维数组
    down_index = np.empty(sample_count * 2, dtype=np.int32)
    down_value = np.empty(sample_count * 2, dtype=_value.dtype)

    down_index[0::2] = max_idx
    down_index[1::2] = min_idx

    down_value[0::2] = max_val
    down_value[1::2] = min_val

    return down_index, down_value


from numba import njit, prange
import numpy as np

@njit(parallel=True)
def down_sample_numba(value, mn, mx, down_count):
    mn = max(0, mn)
    mx = min(value.shape[0], mx)
    ds = max(1, int((mx - mn) / down_count))

    sample_count = (mx - mn) // ds
    down_index = np.empty(sample_count * 2, dtype=np.int32)
    down_value = np.empty(sample_count * 2, dtype=np.float64)

    for i in prange(sample_count):
        start = mn + i * ds
        end = start + ds
        block = value[start:end]

        down_index[2 * i] = start
        down_index[2 * i + 1] = start
        down_value[2 * i] = block.max()
        down_value[2 * i + 1] = block.min()

    return down_index, down_value



if __name__ == "__main__":
    np.random.seed(0)
    import time
    for i in range(5):
        data = np.random.randint(-32768, 32767, size=100_000_000, dtype=np.int16)
        down_count = 4000
        start = time.time()
        idx1, val1 = down_sample(data, 0, len(data), down_count)
        end = time.time()
        print(f"Original down_sample time: {end - start:.6f} seconds")
        start = time.time()
        idx2, val2 = down_sample_opt(data, 0, len(data), down_count)
        end = time.time()
        print(f"Optimized down_sample time: {end - start:.6f} seconds")
        start = time.time()
        idx3, val3 = down_sample_numba(data, 0, len(data), down_count)
        end = time.time()
        print(f"Numba down_sample time: {end - start:.6f} seconds")
