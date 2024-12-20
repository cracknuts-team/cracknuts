from cracknuts.trace.trace import ScarrTraceDataset, NumpyTraceDataset, TraceDataset
import numpy as np

channel_count = 2
trace_count = 100
sample_count = 4096
data_length = 16
version = "(cracker: 0.0.1, trace: 0.0.1)"

zarr_path = "d:\\z.zarr"


def _update_trace(ds: TraceDataset):
    for c in range(channel_count):
        for i in range(trace_count):
            ds.set_trace(c, i, np.random.randint(low=0, high=100, size=sample_count, dtype=np.int16),
                         np.random.randint(low=0, high=16, size=data_length, dtype=np.int8))

def test_scarr_trace_dataset_create():
    ds = ScarrTraceDataset.new(zarr_path, channel_count, trace_count, sample_count, data_length, version)
    _update_trace(ds)

def test_scarr_trace_dataset_load():
    ds = ScarrTraceDataset.load("d:\\z.zarr")
    print(ds.get_origin_data()["0/0/traces"].info)
    print(ds.get_origin_data()["0/0/traces"][0].shape)


def test_scarr_trace_dataset_data_slice():
    ds = ScarrTraceDataset.load(zarr_path)
    print()
    # print(ds.data[0][0])
    # print(type(ds.data[1][1]))
    # print(type(ds.data[1,1]))
    # print(type(ds.data[1]))
    # print(type(ds.data[[0,1]]))
    # print(type(ds.data[[0,1]][9:11]))
    # print(type(ds.data[[0,1]][[9,11]]))
    # print(ds.data[0][1:3][2].shape)
    # print(ds.data[0,1:3][2].shape)
    print(ds.get_origin_data()[0, 1])


npy_path = "d:\\trace_dataset.npy"


def test_numpy_trace_dataset_create():
    ds = NumpyTraceDataset.new(npy_path, channel_count, trace_count, sample_count, data_length, version)
    _update_trace(ds)
    ds.dump()

def test_numpy_trace_dataset_load():
    ds = NumpyTraceDataset.load(npy_path)
    print(ds.get_origin_data()[0].shape)
    print(ds.get_origin_data()[1].shape)

def test_numpy_trace_dataset_data_slice():
    ds = NumpyTraceDataset.load(npy_path)
    print()
    print(ds.channel_count)
    # print(ds.data[0:1][1:3][2].shape)
    # print(ds.data[0,1:3][2].shape)
    s = slice(0, 1)
    print(ds.data[s,1:3][2].shape)
    print(ds.data[0, 1][2])