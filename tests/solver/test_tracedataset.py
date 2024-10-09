from cracknuts.solver.trace import ScarrTraceDataset
import numpy as np

def test_trace_dataset_create():
    ds = ScarrTraceDataset.new("d:\\z.zarr", 1000, 10240, 16)

    for i in range(1000):
        ds.set_trace(i, np.random.randint(low=0, high=100, size=10240, dtype=np.int16),
                     np.random.randint(low=0, high=16, size=16, dtype=np.int8))


def test_trace_dataset_read():
    ds = ScarrTraceDataset.load("d:\\z.zarr")
    print(ds.get_trace_by_range(1,2)[0].shape)
    print(ds.get_trace_by_indexes(1,2)[0].shape)
    print(ds.get_trace_data_ndarray()[0][9:13].shape)