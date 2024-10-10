import abc
import os
import time
from datetime import datetime

import numpy as np
import zarr


class TraceDatasetMetadata:
    def __init__(
        self,
        create_time: int = None,
        version: str = None,
        trace_count: int = None,
        sample_count: int = None,
        data_length: int = None,
    ):
        self.create_time: int = int(time.time()) if create_time is None else create_time
        self.version: str = "Unknown" if version is None else version
        self.trace_count: int = trace_count
        self.sample_count: int = sample_count
        self.data_length: int = data_length


class TraceDataset(abc.ABC):
    @abc.abstractmethod
    def get_origin_data(self): ...

    @classmethod
    @abc.abstractmethod
    def load(cls, path: str, **kwargs) -> "TraceDataset": ...

    @classmethod
    @abc.abstractmethod
    def new(
        cls, path: str, channel_count: int, trace_count: int, sample_count: int, data_length: int, **kwargs
    ) -> "TraceDataset": ...

    @abc.abstractmethod
    def dump(self, path: str = None, **kwargs): ...

    @abc.abstractmethod
    def set_trace(self, channel_index: int, index: int, trace: np.ndarray, data: np.ndarray): ...

    @abc.abstractmethod
    def get_trace_by_indexes(self, channel_index: int, *indexes: int) -> tuple[np.ndarray, np.ndarray] | None: ...

    @abc.abstractmethod
    def get_trace_by_range(
        self, channel_index: int, index_start, index_end
    ) -> tuple[np.ndarray, np.ndarray] | None: ...


class ScarrTraceDataset(TraceDataset):
    _attr_metadata_key = "metadata"
    _group_root_path = "0"
    _array_traces_path = "traces"
    _array_data_path = "plaintext"

    def __init__(
        self,
        zarr_path: str,
        write: bool = False,
        channel_count: int = None,
        trace_count: int = None,
        sample_count: int = None,
        data_length: int = None,
        zarr_kwargs: dict = None,
        zarr_trace_group_kwargs: dict = None,
        zarr_data_group_kwargs: dict = None,
        create_time: int = None,
    ):
        if write:
            if channel_count is None or trace_count is None or sample_count is None or data_length is None:
                raise ValueError(
                    "channel_count and trace_count and sample_count and data_length "
                    "must be specified when in write mode."
                )
        else:
            if zarr_path is None:
                raise ValueError("The zarr_path must be specified when in non-write mode.")

        self._zarr_path: str = zarr_path
        self._channel_count: int = channel_count
        self._trace_count: int = trace_count
        self._sample_count: int = sample_count
        self._data_length: int = data_length
        self._create_time: int = create_time

        if zarr_kwargs is None:
            zarr_kwargs = {}
        if zarr_trace_group_kwargs is None:
            zarr_trace_group_kwargs = {}
        if zarr_data_group_kwargs is None:
            zarr_data_group_kwargs = {}

        mode = zarr_kwargs.pop("mode", "w" if write else "r")
        self._zarr_data = zarr.open(zarr_path, mode=mode, **zarr_kwargs)

        if write:
            self._create_time = int(time.time())
            group_root = self._zarr_data.create_group(self._group_root_path)
            for i in range(self._channel_count):
                channel_group = group_root.create_group(str(i))
                channel_group.create(
                    self._array_traces_path,
                    shape=(self._trace_count, self._sample_count),
                    dtype=np.uint16,
                    **zarr_trace_group_kwargs,
                )
                channel_group.create(
                    self._array_data_path,
                    shape=(self._trace_count, self._data_length),
                    dtype=np.uint8,
                    **zarr_data_group_kwargs,
                )
            self._zarr_data.attrs[self._attr_metadata_key] = {
                "create_time": self._create_time,
                "channel_count": self._channel_count,
                "trace_count": self._trace_count,
                "sample_count": self._sample_count,
                "data_length": self._data_length,
            }
        else:
            metadata = self._zarr_data.attrs[self._attr_metadata_key]
            self._create_time = metadata.get("create_time")
            self._channel_count = metadata.get("channel_count")
            self._trace_count = metadata.get("trace_count")
            self._sample_count = metadata.get("sample_count")
            self._data_length = metadata.get("data_length")

    @classmethod
    def load(cls, path: str, **kwargs) -> "TraceDataset":
        kwargs["mode"] = "r"
        return cls(path, zarr_kwargs=kwargs)

    @classmethod
    def new(
        cls, path: str, channel_count: int, trace_count: int, sample_count: int, data_length: int, **kwargs
    ) -> "TraceDataset":
        kwargs["mode"] = "w"
        return cls(
            path,
            write=True,
            channel_count=channel_count,
            trace_count=trace_count,
            sample_count=sample_count,
            data_length=data_length,
            zarr_kwargs=kwargs,
        )

    def dump(self, path: str = None, **kwargs):
        if path != self._zarr_path:
            zarr.copy_store(self._zarr_data, zarr.open(path, mode="w"))

    def set_trace(self, channel_index: int, trace_index: int, trace: np.ndarray, data: np.ndarray):
        if channel_index not in range(0, self._channel_count):
            raise ValueError("channel index out range")
        if trace_index not in range(0, self._trace_count):
            raise ValueError("trace, index out of range")
        self._get_under_root(channel_index, self._array_traces_path)[trace_index] = trace
        self._get_under_root(channel_index, self._array_data_path)[trace_index] = data

    def get_origin_data(self):
        return self._zarr_data

    def get_trace_by_indexes(self, channel_index: int, *trace_indexes: int) -> tuple[np.ndarray, np.ndarray] | None:
        return (
            self._get_under_root(channel_index, self._array_traces_path)[[i for i in trace_indexes]],
            self._get_under_root(channel_index, self._array_data_path)[[i for i in trace_indexes]],
        )

    def get_trace_by_range(
        self, channel_index: int, index_start: int, index_end: int
    ) -> tuple[np.ndarray, np.ndarray] | None:
        return (
            self._get_under_root(channel_index, self._array_traces_path)[index_start:index_end],
            self._get_under_root(channel_index, self._array_data_path)[index_start:index_end],
        )

    def _get_under_root(self, *paths: any):
        paths = self._group_root_path, *paths
        return self._zarr_data["/".join(str(path) for path in paths)]


class NumpyTraceDataset:
    def __init__(
        self,
        create_time: datetime = None,
        version: str = None,
        trace_count: int = None,
        sample_count: int = None,
        data_length: int = None,
    ):
        self._metadata = TraceDatasetMetadata(create_time, version, trace_count, sample_count, data_length)
        self._data_array: np.ndarray | None
        self._trace_array: np.ndarray | None = None

        if self._metadata.trace_count is not None and self._metadata.sample_count is not None:
            self._trace_array = np.zeros((self._metadata.trace_count, self._metadata.sample_count))
            if self._metadata.data_length is not None:
                self._data_array = np.zeros(
                    shape=self._metadata.trace_count, dtype=np.dtype((np.void, self._metadata.data_length))
                )
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

    def load_from_hdf5(self, path: str): ...

    # def add_trace(self, trace: np.ndarray, index: int = None):
    #     if index is None:
    #         index = self._current_create_trace_index
    #         self._current_create_trace_index += 1
    #     self.traces[index:] = trace

    def add_data(self, data: bytes, index: int = None):
        if index is None:
            index = self._current_create_data_index
            self._current_create_data_index += 1
        self.data[index:] = data

    def update_metadata_environment_info(self, cracknuts: str, cracker: str, nuts: str): ...

    def get_metadata(self) -> TraceDatasetMetadata:
        return self._metadata

    def save_as_numpy_file(self, path):
        np.save(os.path.join(path, "trace.npy"), self.traces)
        np.save(os.path.join(path, "data.npy"), self.data)

    def save_as_zarr(self, path): ...  # todo
