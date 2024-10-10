from cracknuts.solver.trace import ScarrTraceDataset
import numpy as np

zarr_path = "d:\\z.zarr"


def test_trace_dataset_create():

    channel_count = 2
    trace_count = 100
    sample_count = 4096
    data_length = 16

    ds = ScarrTraceDataset.new(zarr_path, channel_count, trace_count, sample_count, data_length)

    for c in range(channel_count):
        for i in range(trace_count):
            ds.set_trace(c, i, np.random.randint(low=0, high=100, size=sample_count, dtype=np.int16),
                         np.random.randint(low=0, high=16, size=data_length, dtype=np.int8))


def test_trace_dataset_read():
    ds = ScarrTraceDataset.load("d:\\z.zarr")
    print(ds.get_trace_by_range(1,2,3)[0].shape)
    print(ds.get_trace_by_indexes(0,2,3)[0].shape)
    print(ds.get_origin_data()["0/0/traces"].info)
    print(ds.get_origin_data()["0/0/traces"][0].shape)