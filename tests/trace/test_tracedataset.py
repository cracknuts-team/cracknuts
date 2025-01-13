from cracknuts.trace.trace import ScarrTraceDataset, NumpyTraceDataset, TraceDataset
import numpy as np

channel_name = ['1', '2']
trace_count = 100
sample_count = 4096
data_length = 16
version = "(cracker: 0.0.1, trace: 0.0.1)"

zarr_path = "d:\\z.zarr"


def _update_trace(ds: TraceDataset):
    for c in channel_name:
        for i in range(trace_count):
            ds.set_trace(c, i, np.random.randint(low=0, high=100, size=sample_count, dtype=np.int16),
                         np.random.randint(low=0, high=16, size=data_length, dtype=np.int8))


def test_scarr_trace_dataset_create():
    ds = ScarrTraceDataset.new(zarr_path, channel_name, trace_count, sample_count, data_length, version)
    _update_trace(ds)

def test_scarr_trace_dataset_load():
    ds = ScarrTraceDataset.load("D:\\project\\cracknuts\\demo\\jupyter\\dataset\\20250113160603.zarr")
    print(ds.info())
    print(ds.get_origin_data().tree())
    for name in ds.channel_names:
        print(ds.get_origin_data()[f"0/{name}/traces"].info)
        print(ds.get_origin_data()[f"0/{name}/traces"][0].shape)


def test_scarr_trace_dataset_data_slice():
    ds = ScarrTraceDataset.load(zarr_path)
    print(ds.info())
    print(ds.data[0][0])
    # print(ds.data[0][0])
    # print(type(ds.data[1][1]))
    # print(type(ds.data[1,1]))
    # print(type(ds.data[1]))
    # print(type(ds.data[[0,1]]))
    # print(type(ds.data[[0,1]][9:11]))
    # print(type(ds.data[[0,1]][[9,11]]))
    # print(ds.data[0][1:3][2].shape)
    # print(ds.data[0,1:3][2].shape)
    # print(ds.get_origin_data())


npy_path = "d:\\trace_dataset.npy"


def test_numpy_trace_dataset_create():
    ds = NumpyTraceDataset.new(npy_path, channel_name, trace_count, sample_count, data_length, version)
    _update_trace(ds)
    ds.dump()


def test_numpy_trace_dataset_load():
    ds = NumpyTraceDataset.load(npy_path)
    print(ds.get_origin_data()[0].shape)
    print(ds.get_origin_data()[1].shape)
    print(ds.info())


def test_numpy_trace_dataset_data_slice():
    ds = NumpyTraceDataset.load(npy_path)
    print()
    print(ds.channel_names)
    # print(ds.data[0:1][1:3][2].shape)
    # print(ds.data[0,1:3][2].shape)
    s = slice(0, 1)
    print(ds.data[s,1:3][2].shape)
    print(ds.data[0, 1][2])