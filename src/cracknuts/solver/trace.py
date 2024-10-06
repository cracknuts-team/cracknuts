import os
from datetime import datetime
from typing import Any

import numpy as np
import pandas as pd
import zarr


class TraceDataSetMetadata:
    def __init__(self):
        self.create_time: datetime = datetime.now()
        self.cracknuts: str = "Unknown"
        self.cracker: str = "Unknown"
        self.nuts: str = "Unknown"
        self.trace_count: int = 0
        self.sample_count: int = 0


class TraceDataset:
    def __init__(self, shape: tuple[int, int] = None, data_length: int = None):
        self.shape: tuple[int, int] = shape
        self._metadata = TraceDataSetMetadata()
        self.data: np.ndarray | None = (
            np.empty(shape=shape[0], dtype=np.dtype((np.void, data_length))) if data_length is not None else None
        )
        self.traces: np.ndarray | None = np.empty(shape=shape) if shape is not None else None
        self._current_create_trace_index: int = 0
        self._current_create_data_index: int = 0

    def load_from_numpy_data_file(self, path: str, transpose=False) -> "TraceDataset":
        """
        Load traces from numpy data file.
        :param path: file path.
        :param transpose: if axes 0 is not represent trace and axes 1 is not represent trace data(sample)
        """
        self.traces = np.load(path)
        if transpose:
            self.traces = self.traces.T
            sample_count, trace_count = self.traces.shape
        else:
            trace_count, sample_count = self.traces.shape

        self._metadata.trace_count = trace_count
        self._metadata.sample_count = sample_count

        return self

    def load_from_zarr(self, path: str, structure: str = "scarr"):
        if structure == "scarr":
            self.load_from_scarr(path)
        # todo other

    def load_from_scarr(self, path: str):
        scarr_data = zarr.open(path, "r")
        self.traces = scarr_data["0/0/traces"]
        trace_count = self.traces.shape[0]
        sample_count = self.traces.shape[1]
        data = scarr_data["0/0/plaintext"]

        self._metadata.trace_count = trace_count
        self._metadata.sample_count = sample_count
        self.data = data

    def load_from_hdf5(self, path: str): ...

    def add_trace(self, trace: np.ndarray, index: int = None):
        if index is None:
            index = self._current_create_trace_index
            self._current_create_trace_index += 1
        self.traces[index:] = trace

    def add_data(self, data: bytes, index: int = None):
        if index is None:
            index = self._current_create_data_index
            self._current_create_data_index += 1
        self.data[index:] = data

    def update_metadata_environment_info(self, cracknuts: str, cracker: str, nuts: str): ...

    def get_metadata(self) -> TraceDataSetMetadata:
        return self._metadata

    def save_as_numpy_file(self, path):
        np.save(os.path.join(path, "trace.npy"), self.traces)
        np.save(os.path.join(path, "data.npy"), self.data)

    def save_as_zarr(self, path): ...  # todo


def down_sample(value: np.ndarray, mn, mx, down_count):
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


def get_traces_df_from_ndarray(
    traces: np.ndarray,
    trace_index_mn=None,
    trace_index_mx=None,
    mn=None,
    mx=None,
    down_count=500,
    trace_indexes=None,
):
    traces_dict = {}
    if not trace_indexes:
        trace_indexes = [t for t in range(trace_index_mn, trace_index_mx)]
    index = None
    for i in trace_indexes:
        index, value = down_sample(traces[i, :], mn, mx, down_count)
        iv = np.empty((2, len(index)))
        iv[:] = index, value
        traces_dict[i] = value

    traces_dict["index"] = index

    return pd.DataFrame(traces_dict).melt(id_vars="index", var_name="traces", value_name="value"), trace_indexes


def load_traces(path: str) -> tuple[str, Any, Any, Any, Any, Any | None]:
    if os.path.isdir(path):
        # load scarr data from zarr format file.
        scarr_data = zarr.open(path, "r")
        traces_source = scarr_data["0/0/traces"]
        trace_count = traces_source.shape[0]
        sample_count = traces_source.shape[1]
        data = scarr_data["0/0/plaintext"]
        data_type = "zarr"
        origin_data = scarr_data
    else:
        # load newae data from npy format file.
        traces_source = np.load(path)
        trace_count = traces_source.shape[0]
        sample_count = traces_source.shape[1]
        data_type = "npy"
        data = None
        origin_data = None

    return data_type, traces_source, trace_count, sample_count, data, origin_data
