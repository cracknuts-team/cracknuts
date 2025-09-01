import os.path
import shutil
import time

import zarr
import numpy as np
from numpy import dtype

from cracknuts.trace import ZarrTraceDataset


def speed1():
    sample_len = 2000
    trace_count = 10000000
    zarr_data_filename = 'b.zarr'

    if os.path.exists(zarr_data_filename):
        shutil.rmtree(zarr_data_filename)

    zarr_data = zarr.open(zarr_data_filename, mode='w')
    trace_group = zarr_data.create_group('/0/0/')
    trace_array = trace_group.create('traces', shape=(trace_count, sample_len), dtype=np.uint16)

    traces = []

    for _ in range(100):
        traces.append(np.random.randint(0, 100, sample_len))

    for i in range(100):
        s = time.time()
        trace_array[i] = traces[i]
        print(time.time() - s)


def speed1_1():
    sample_len = 2000
    trace_count = 1000
    zarr_data_filename = 'b.zarr'

    if os.path.exists(zarr_data_filename):
        shutil.rmtree(zarr_data_filename)

    zarr_data = zarr.open(zarr_data_filename, mode='w')
    trace_group = zarr_data.create_group('/0/0/')
    trace_array = trace_group.create('traces', shape=(trace_count, sample_len), dtype=np.uint16)

    traces = []

    for _ in range(100):
        traces.append(np.random.randint(0, 100, sample_len))

    for i in range(100):
        s = time.time()
        trace_array[i] = traces[i]
        print(time.time() - s)


def speed1_2():
    sample_len = 2000
    trace_count = 10000000
    zarr_data_filename = 'b.zarr'

    if os.path.exists(zarr_data_filename):
        shutil.rmtree(zarr_data_filename)

    zarr_data = zarr.open(zarr_data_filename, mode='w')
    trace_group = zarr_data.create_group('/0/0/')
    trace_array = trace_group.create('traces', shape=(trace_count, sample_len), dtype=np.uint16, chunks=(300, 2000))

    traces = []

    for _ in range(100):
        traces.append(np.random.randint(0, 100, sample_len))

    for i in range(100):
        s = time.time()
        trace_array[i] = traces[i]
        print(time.time() - s)


def speed2():
    sample_len = 2000
    trace_count = 100
    zarr_data_filename = 'a.zarr'

    if os.path.exists(zarr_data_filename):
        shutil.rmtree(zarr_data_filename)

    zarr_dataset = ZarrTraceDataset(
        zarr_path=zarr_data_filename,
        channel_names=['A'],
        trace_count=trace_count,
        sample_count=sample_len,
        create_empty=True
    )

    traces = []

    for _ in range(100):
        traces.append(np.random.randint(0, 100, sample_len))

    for i in range(100):
        s = time.time()
        zarr_dataset.set_trace('A', i, traces[i], {
            'plaintext': np.frombuffer(bytes.fromhex('aabb'), dtype=np.uint8),
            'ciphertext': np.frombuffer(bytes.fromhex('ccdd'), dtype=np.uint8),
            'key': np.frombuffer(bytes.fromhex('eeff'), dtype=np.uint8)
        })
        print(time.time() - s)


if __name__ == '__main__':
    # speed1()
    # speed1_2()
    speed2()