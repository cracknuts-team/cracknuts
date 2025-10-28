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


def speed3(chunk, shape):
    trace_count = shape[0]
    sample_length = shape[1]
    zarr_data_filename = f'dataset/test_{chunk[0]}_{chunk[1]}.zarr'
    if os.path.exists(zarr_data_filename):
        shutil.rmtree(zarr_data_filename)
    zarr_data = zarr.open(zarr_data_filename, mode='w')
    trace_group = zarr_data.create_group('/0/0')
    trace_array = trace_group.create('traces', shape=(trace_count, sample_length), dtype=np.uint16, chunks=chunk)
    for i in range(trace_count):
        s = time.time()
        trace = np.random.randint(0, 100, sample_length, dtype=np.uint16)
        e = time.time()
        # print(f"trace gen cost: {e - s}")
        trace_array[i] = trace
        c = time.time() - e
        # print(f"trace set cost: {c}")
        yield i, c


def speed3_test():
    shapes = [
        (1_000, 20_000),
        # (1_000_000, 20_000),
        # (100, 80_000_000)
    ]
    chunks = [
        (300, 2000),  # 每个chunk 300 条曲线， 每条曲线由 10 个 chunk 组成
        (1, 20_000) # 一个chunk一条曲线, 每条曲线由 1 个 chunk 组成
    ]
    # chunks = [
    #     (1, 80_000_000), # 一个chunk一条曲线
    #     (10, 8_000_000), # 每个chunk 10 条曲线， 每条曲线由 10 个 chunk 组成
    #     (100, 800_000),  # 每个chunk 100 条曲线， 每条曲线由 100 个 chunk 组成
    # ]
    import csv
    for shape in shapes:
        result_csv_path = f"test_result_{shape[0]}_{shape[1]}.csv"
        if os.path.exists(result_csv_path):
            os.remove(result_csv_path)
        for chunk in chunks:
            print("Chunk:", chunk)
            for i, c in speed3(chunk, shape):
                with open(result_csv_path, mode='a', newline='') as file:
                    writer = csv.writer(file)
                    writer.writerow([chunk[0], chunk[1], c])
                print(f"save {i}: {c}")


def plot_speed3_test():
    import pandas as pd
    import matplotlib.pyplot as plt

    # 读取 CSV
    df = pd.read_csv("test_result_1000_20000.csv")
    # df = pd.read_csv("test_result_100_80000000.csv")

    # 检查列名（假设为前三列）
    col1, col2, col3 = df.columns[:3]

    # 根据前两列分组
    grouped = df.groupby([col1, col2])

    plt.figure(figsize=(8, 5))

    # 为每个组绘制曲线
    for (g1, g2), group in grouped:
        y = group[col3].values
        x = range(len(y))  # 按行顺序作为 x
        label = f"{g1}-{g2}"  # legend 名称
        plt.plot(x, y, label=label)

    plt.xlabel("Index")
    plt.ylabel(col3)
    plt.title("Grouped Plot from CSV")
    plt.legend()
    plt.grid(True)
    plt.tight_layout()
    plt.show()


if __name__ == '__main__':
    # speed1()
    # speed1_2()
    # speed2()
    # speed3_test()
    plot_speed3_test()