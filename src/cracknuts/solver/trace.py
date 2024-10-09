import abc
import os
from ctypes import windll
from datetime import datetime
from typing import Any

import numpy as np
import pandas as pd
import zarr
from numpy.core.fromnumeric import shape
from numpy.core.records import ndarray


class TraceDatasetMetadata:
    def __init__(
            self,
            create_time: datetime = None,
            version: str = None,
            trace_count: int = None,
            sample_count: int = None,
            data_length: int = None
    ):
        self.create_time: datetime = datetime.now() if create_time is None else create_time
        self.version: str = "Unknown" if version is None else version
        self.trace_count: int = trace_count
        self.sample_count: int = sample_count
        self.data_length: int = data_length


class TraceDataset(abc.ABC):


    @abc.abstractmethod
    def get_trace_data_ndarray(self) -> tuple[np.ndarray, np.ndarray]: ...

    @classmethod
    @abc.abstractmethod
    def load(cls, path: str, **kwargs) -> 'TraceDataset':
        ...

    @classmethod
    @abc.abstractmethod
    def new(cls, path: str, trace_count: int, sample_count: int, data_length: int, **kwargs) -> 'TraceDataset':
        ...

    @abc.abstractmethod
    def dump(self, path: str = None, **kwargs):
        ...

    @abc.abstractmethod
    def set_trace(self, index: int, trace: np.ndarray, data: np.ndarray):
        ...

    @abc.abstractmethod
    def get_trace_by_indexes(self, *indexes) -> tuple[np.ndarray, np.ndarray] | None:
        ...

    @abc.abstractmethod
    def get_trace_by_range(self, index_start, index_end) -> tuple[np.ndarray, np.ndarray] | None:
        ...


class ScarrTraceDataset(TraceDataset):
    _group_path = "/0/0"
    _traces_path = "traces"
    _data_path = "plaintext"

    def __init__(self, zarr_path: str, write: bool = False,
                 trace_count: int = None,
                 sample_count: int = None,
                 data_length: int = None,
                 zarr_kwargs: dict = None,
                 zarr_trace_group_kwargs: dict = None,
                 zarr_data_group_kwargs: dict = None,
                 ):
        self._zarr_path = zarr_path
        self._trace_count = trace_count
        self._sample_count = sample_count
        self._data_length = data_length

        if zarr_kwargs is None:
            zarr_kwargs = {}
        if zarr_trace_group_kwargs is None:
            zarr_trace_group_kwargs = {}
        if zarr_data_group_kwargs is None:
            zarr_data_group_kwargs = {}

        mode = zarr_kwargs.pop("mode", "w" if write else "r")
        self._zarr_data = zarr.open(zarr_path, mode=mode, **zarr_kwargs)

        if write:
            default_group = self._zarr_data.create_group(self._group_path)  # todo multiple channel support ?
            self._trace_array = default_group.create(
                self._traces_path,
                shape=(self._trace_count, self._sample_count),
                dtype=np.uint16,
                **zarr_trace_group_kwargs)
            self._data_array = default_group.create(
                self._data_path,
                shape=(self._trace_count, self._data_length),
                dtype=np.uint8,
                **zarr_data_group_kwargs)
        else:
            self._trace_array = self._zarr_data[self._group_path + "/" + self._traces_path]
            self._data_array = self._zarr_data[self._group_path + "/" + self._data_path]

    @classmethod
    def load(cls, path: str, **kwargs) -> 'TraceDataset':
        kwargs["mode"] = "r"
        return cls(path, zarr_kwargs=kwargs)

    @classmethod
    def new(cls, path: str, trace_count: int, sample_count: int, data_length: int, **kwargs) -> 'TraceDataset':
        kwargs["mode"] = "w"
        return cls(path, write=True, trace_count=trace_count, sample_count=sample_count, data_length=data_length,
                   zarr_kwargs=kwargs)

    def dump(self, path: str = None, **kwargs):
        if path != self._zarr_path:
            zarr.copy_store(self._zarr_data, zarr.open(path, mode="w"))

    def set_trace(self, index: int, trace: np.ndarray, data: np.ndarray):
        if index not in range(0, self._trace_count):
            raise ValueError("Index out of range")
        self._trace_array[index] = trace
        self._data_array[index] = np.frombuffer(data, dtype=np.uint8)

    def get_trace_data_ndarray(self) -> tuple[np.ndarray, np.ndarray]:
        return self._trace_array, self._data_array

    def get_trace_by_indexes(self, *indexes) -> tuple[np.ndarray, np.ndarray] | None:
        return self._trace_array[[i for i in indexes]], self._data_array[[i for i in indexes]]

    def get_trace_by_range(self, index_start, index_end) -> tuple[np.ndarray, np.ndarray] | None:
        return self._trace_array[index_start:index_end], self._data_array[index_start:index_end]


class NumpyTraceDataset:

    def __init__(
            self,
            create_time: datetime = None,
            version: str = None,
            trace_count: int = None,
            sample_count: int = None,
            data_length: int = None
    ):
        self._metadata = TraceDatasetMetadata(create_time, version, trace_count, sample_count, data_length)
        self._data_array: np.ndarray | None
        self._trace_array: np.ndarray | None = None

        if self._metadata.trace_count is not None and self._metadata.sample_count is not None:
            self._trace_array = np.zeros((self._metadata.trace_count, self._metadata.sample_count))
            if self._metadata.data_length is not None:
                self._data_array = np.zeros(shape=self._metadata.trace_count,
                                            dtype=np.dtype((np.void, self._metadata.data_length)))
        else:
            self._trace_array: np.ndarray | None = None
            self._data_array: np.ndarray | None = None

    def add_trace(self, index: int, trace: np.ndarray, data: bytes):
        self._trace_array[index:] = trace
        self._data_array[index:] = data

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

    def load_from_hdf5(self, path: str):
        ...

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

    def update_metadata_environment_info(self, cracknuts: str, cracker: str, nuts: str):
        ...

    def get_metadata(self) -> TraceDatasetMetadata:
        return self._metadata

    def save_as_numpy_file(self, path):
        np.save(os.path.join(path, "trace.npy"), self.traces)
        np.save(os.path.join(path, "data.npy"), self.data)

    def save_as_zarr(self, path):
        ...  # todo
