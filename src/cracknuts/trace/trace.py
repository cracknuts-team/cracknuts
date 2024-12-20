# Copyright 2024 CrackNuts. All rights reserved.

import abc
import json
import os.path
import time
import typing

import numpy as np
import zarr

from cracknuts import logger


class TraceDatasetData:
    def __init__(
        self,
        get_trace_data: typing.Callable[[typing.Any, typing.Any], tuple],
        level: int = 0,
        index: tuple | None = None,
    ):
        self._level: int = level
        self._index: tuple | None = index
        self._get_trace_data = get_trace_data

    def __getitem__(self, index):
        if not isinstance(index, tuple):
            index = (index,)

        level = len(index) + self._level
        index = index if self._index is None else (*self._index, *index)
        if level < 2:
            return TraceDatasetData(self._get_trace_data, level, index)
        else:
            return self._get_trace_data(*index)


class TraceDataset(abc.ABC):
    _channel_count: int | None
    _trace_count: int | None
    _sample_count: int | None
    _data_length: int | None
    _create_time: int | None
    _version: str | None

    @abc.abstractmethod
    def get_origin_data(self): ...

    @classmethod
    @abc.abstractmethod
    def load(cls, path: str, **kwargs) -> "TraceDataset": ...

    @classmethod
    @abc.abstractmethod
    def new(
        cls, path: str, channel_count: int, trace_count: int, sample_count: int, data_length: int, version, **kwargs
    ) -> "TraceDataset": ...

    @abc.abstractmethod
    def dump(self, path: str | None = None, **kwargs): ...

    @abc.abstractmethod
    def set_trace(self, channel_index: int, trace_index: int, trace: np.ndarray, data: np.ndarray | None): ...

    @property
    def data(self) -> TraceDatasetData:
        return TraceDatasetData(get_trace_data=self._get_trace_data)

    @abc.abstractmethod
    def _get_trace_data(self, channel_slice, trace_slice) -> tuple[list, list, np.ndarray, np.ndarray]: ...

    def _parse_slice(self, channel_slice, trace_slice) -> tuple[list, list]:
        if self._channel_count is None:
            raise Exception("Channel count is not set")
        if isinstance(channel_slice, slice):
            start, stop, step = channel_slice.indices(self._channel_count)
            channel_indexes = [i for i in range(start, stop, step)]
        elif isinstance(channel_slice, int):
            channel_indexes = [channel_slice]
        elif isinstance(channel_slice, list):
            channel_indexes = channel_slice
        else:
            raise ValueError("channel_slice is not a slice or list")

        if self._trace_count is None:
            raise Exception("Trace count is not set")
        if isinstance(trace_slice, slice):
            start, stop, step = trace_slice.indices(self._trace_count)
            trace_indexes = [i for i in range(start, stop, step)]
        elif isinstance(trace_slice, int):
            trace_indexes = [trace_slice]
        elif isinstance(trace_slice, list):
            trace_indexes = trace_slice
        else:
            raise ValueError("trace_slice is not a slice or list")

        return channel_indexes, trace_indexes

    @property
    def channel_count(self):
        return self._channel_count

    @property
    def trace_count(self):
        return self._trace_count

    @property
    def sample_count(self):
        return self._sample_count

    @property
    def data_length(self):
        return self._data_length

    @property
    def create_time(self):
        return self._create_time


class ScarrTraceDataset(TraceDataset):
    _ATTR_METADATA_KEY = "metadata"
    _GROUP_ROOT_PATH = "0"
    _ARRAY_TRACES_PATH = "traces"
    _ARRAY_DATA_PATH = "plaintext"

    def __init__(
        self,
        zarr_path: str,
        create_empty: bool = False,
        channel_count: int | None = None,
        trace_count: int | None = None,
        sample_count: int | None = None,
        data_length: int | None = None,
        trace_dtype: np.dtype = np.int16,
        zarr_kwargs: dict | None = None,
        zarr_trace_group_kwargs: dict | None = None,
        zarr_data_group_kwargs: dict | None = None,
        create_time: int | None = None,
        version: str | None = None,
    ):
        self._zarr_path: str = zarr_path
        self._channel_count: int | None = channel_count
        self._trace_count: int | None = trace_count
        self._sample_count: int | None = sample_count
        self._data_length: int | None = data_length
        self._create_time: int | None = create_time
        self._version: str | None = version

        if zarr_kwargs is None:
            zarr_kwargs = {}
        if zarr_trace_group_kwargs is None:
            zarr_trace_group_kwargs = {}
        if zarr_data_group_kwargs is None:
            zarr_data_group_kwargs = {}

        mode = zarr_kwargs.pop("mode", "w" if create_empty else "r")
        self._zarr_data = zarr.open(zarr_path, mode=mode, **zarr_kwargs)

        if create_empty:
            if (
                self._channel_count is None
                or self._trace_count is None
                or self._sample_count is None
                or self._data_length is None
            ):
                raise ValueError(
                    "channel_count and trace_count and sample_count and data_length "
                    "must be specified when in write mode."
                )
            self._create_time = int(time.time())
            group_root = self._zarr_data.create_group(self._GROUP_ROOT_PATH)
            for i in range(self._channel_count):
                channel_group = group_root.create_group(str(i))
                channel_group.create(
                    self._ARRAY_TRACES_PATH,
                    shape=(self._trace_count, self._sample_count),
                    dtype=trace_dtype,
                    **zarr_trace_group_kwargs,
                )
                channel_group.create(
                    self._ARRAY_DATA_PATH,
                    shape=(self._trace_count, self._data_length),
                    dtype=np.uint8,
                    **zarr_data_group_kwargs,
                )
            self._zarr_data.attrs[self._ATTR_METADATA_KEY] = {
                "create_time": self._create_time,
                "channel_count": self._channel_count,
                "trace_count": self._trace_count,
                "sample_count": self._sample_count,
                "data_length": self._data_length,
                "version": self._version,
            }
        else:
            if self._zarr_path is None:
                raise ValueError("The zarr_path must be specified when in non-write mode.")
            metadata = self._zarr_data.attrs[self._ATTR_METADATA_KEY]
            self._create_time = metadata.get("create_time")
            self._channel_count = metadata.get("channel_count")
            self._trace_count = metadata.get("trace_count")
            self._sample_count = metadata.get("sample_count")
            self._data_length = metadata.get("data_length")
            self._version = metadata.get("version")

    @classmethod
    def load(cls, path: str, **kwargs) -> "TraceDataset":
        kwargs["mode"] = "r"
        return cls(path, zarr_kwargs=kwargs)

    @classmethod
    def new(
        cls,
        path: str,
        channel_count: int,
        trace_count: int,
        sample_count: int,
        data_length: int,
        version: str,
        **kwargs,
    ) -> "TraceDataset":
        kwargs["mode"] = "w"
        return cls(
            path,
            create_empty=True,
            channel_count=channel_count,
            trace_count=trace_count,
            sample_count=sample_count,
            data_length=data_length,
            version=version,
            zarr_kwargs=kwargs,
        )

    def dump(self, path: str | None = None, **kwargs):
        if path is not None and path != self._zarr_path:
            zarr.copy_store(self._zarr_data, zarr.open(path, mode="w"))

    def set_trace(self, channel_index: int, trace_index: int, trace: np.ndarray, data: np.ndarray | None):
        if self._trace_count is None or self._channel_count is None:
            raise Exception("Channel or trace count must has not specified.")
        if channel_index not in range(0, self._channel_count):
            raise ValueError("channel index out range")
        if trace_index not in range(0, self._trace_count):
            raise ValueError("trace, index out of range")
        self._get_under_root(channel_index, self._ARRAY_TRACES_PATH)[trace_index] = trace
        if self._data_length != 0 and data is not None:
            self._get_under_root(channel_index, self._ARRAY_DATA_PATH)[trace_index] = data

    def get_origin_data(self):
        return self._zarr_data

    def get_trace_by_indexes(self, channel_index: int, *trace_indexes: int) -> tuple[np.ndarray, np.ndarray] | None:
        return (
            self._get_under_root(channel_index, self._ARRAY_TRACES_PATH)[[i for i in trace_indexes]],
            self._get_under_root(channel_index, self._ARRAY_DATA_PATH)[[i for i in trace_indexes]],
        )

    def get_trace_by_range(
        self, channel_index: int, index_start: int, index_end: int
    ) -> tuple[np.ndarray, np.ndarray] | None:
        return (
            self._get_under_root(channel_index, self._ARRAY_TRACES_PATH)[index_start:index_end],
            self._get_under_root(channel_index, self._ARRAY_DATA_PATH)[index_start:index_end],
        )

    def _get_under_root(self, *paths: typing.Any):
        paths = self._GROUP_ROOT_PATH, *paths
        return self._zarr_data["/".join(str(path) for path in paths)]

    def _get_trace_data(self, channel_slice, trace_slice) -> tuple[list, list, np.ndarray, np.ndarray]:
        traces = []
        data = []

        channel_indexes, trace_indexes = self._parse_slice(channel_slice, trace_slice)

        if isinstance(trace_slice, int):
            trace_slice = slice(trace_slice, trace_slice + 1)

        for channel_index in channel_indexes:
            traces.append(self._get_under_root(channel_index, self._ARRAY_TRACES_PATH)[trace_slice])
            data.append(self._get_under_root(channel_index, self._ARRAY_DATA_PATH)[trace_slice])

        return channel_indexes, trace_indexes, np.array(traces), np.array(data)


class NumpyTraceDataset(TraceDataset):
    _ARRAY_TRACE_PATH = "trace.npy"
    _ARRAY_DATA_PATH = "data.npy"
    _METADATA_PATH = "metadata.json"

    def __init__(
        self,
        npy_trace_path: str | None = None,
        npy_data_path: str | None = None,
        npy_metadata_path: str | None = None,
        create_empty: bool = False,
        channel_count: int | None = None,
        trace_count: int | None = None,
        sample_count: int | None = None,
        trace_dtype: np.dtype = np.int16,
        data_length: int | None = None,
        create_time: int | None = None,
        version: str | None = None,
    ):
        self._logger = logger.get_logger(NumpyTraceDataset)

        self._npy_trace_path: str | None = npy_trace_path
        self._npy_data_path: str | None = npy_data_path
        self._npy_metadata_path: str | None = npy_metadata_path

        self._channel_count: int | None = channel_count
        self._trace_count: int | None = trace_count
        self._sample_count: int | None = sample_count
        self._data_length: int | None = data_length
        self._create_time: int | None = create_time
        self._version: str | None = version

        self._trace_array: np.ndarray
        self._data_array: np.ndarray

        if create_empty:
            if (
                self._channel_count is None
                or self._trace_count is None
                or self._sample_count is None
                or self._data_length is None
            ):
                raise ValueError(
                    "channel_count and trace_count and sample_count and data_length "
                    "must be specified when in write mode."
                )
            self._trace_array = np.zeros(
                shape=(self._channel_count, self._trace_count, self._sample_count), dtype=trace_dtype
            )
            self._data_array = np.zeros(
                shape=(self._channel_count, self._trace_count, self._data_length), dtype=np.uint8
            )
            self._create_time = int(time.time())

        else:
            if self._npy_trace_path is None:
                raise ValueError("The npy_trace_path must be specified when in non-write mode.")

            self._trace_array = np.load(self._npy_trace_path)

            if self._npy_data_path is None or self._npy_metadata_path is None:
                self._logger.warning(
                    "npy_data_path or npy_metadata_path is not specified, data or metadata info will be not load."
                )
            else:
                self._data_array = np.load(self._npy_data_path)
                self._load_metadata()

    def _load_metadata(self):
        with open(self._npy_metadata_path) as f:
            metadata = json.load(f)
            self._channel_count: int | None = metadata.get("channel_count")
            self._trace_count: int | None = metadata.get("trace_count")
            self._sample_count: int | None = metadata.get("sample_count")
            self._data_length: int | None = metadata.get("data_length")
            self._create_time: int | None = metadata.get("create_time")
            self._version: str | None = metadata.get("version")

    def _dump_metadata(self):
        with open(self._npy_metadata_path, "w") as f:
            json.dump(
                {
                    "channel_count": self._channel_count,
                    "trace_count": self._trace_count,
                    "sample_count": self._sample_count,
                    "data_length": self._data_length,
                    "create_time": self._create_time,
                    "version": self._version,
                },
                f,
            )

    def get_origin_data(self):
        return self._trace_array, self._data_array

    @classmethod
    def load(cls, path: str, **kwargs) -> "TraceDataset":
        return cls(
            os.path.join(path, cls._ARRAY_TRACE_PATH),
            os.path.join(path, cls._ARRAY_DATA_PATH),
            os.path.join(path, cls._METADATA_PATH),
            **kwargs,
        )

    @classmethod
    def load_from_numpy_array(cls, trace: np.ndarray, data: np.ndarray | None = None):
        channel_count = None
        trace_count = None
        sample_count = None
        data_length = None

        shape = trace.shape

        if data is not None and not shape == data.shape:
            raise ValueError("trace and data must have the same shape.")

        array_size = len(shape)

        if array_size == 1:
            channel_count = 1
            trace_count = 1
            sample_count = shape[0]
            data_length = data.shape[0] if data is not None else 0
        elif array_size == 2:
            channel_count = 1
            trace_count = shape[0]
            sample_count = shape[1]
            data_length = data.shape[1] if data is not None else 0
        elif array_size == 3:
            channel_count = shape[0]
            trace_count = shape[1]
            sample_count = shape[2]
            data_length = data.shape[2] if data is not None else 0

        ds = cls(
            create_empty=True,
            channel_count=channel_count,
            trace_count=trace_count,
            sample_count=sample_count,
            data_length=data_length,
            trace_dtype=trace.dtype,
        )

        if array_size == 1:
            ds.set_trace(0, 0, trace, data)
        elif array_size == 2:
            for t in range(shape[0]):
                ds.set_trace(0, t, trace[t], data[t] if data is not None else None)
        elif array_size == 3:
            for c in range(shape[0]):
                for t in range(shape[1]):
                    ds.set_trace(c, t, trace[c, t], data[c, t] if data is not None else None)

        return ds

    @classmethod
    def new(
        cls,
        path: str,
        channel_count: int,
        trace_count: int,
        sample_count: int,
        data_length: int,
        version: str,
        **kwargs,
    ) -> "TraceDataset":
        if not os.path.exists(path):
            os.makedirs(path)
        elif os.path.isfile(path):
            raise Exception(f"{path} is not a file.")

        npy_trace_path = os.path.join(path, cls._ARRAY_TRACE_PATH)
        npy_data_path = os.path.join(path, cls._ARRAY_DATA_PATH)
        npy_metadata_path = os.path.join(path, cls._METADATA_PATH)

        return cls(
            npy_trace_path=npy_trace_path,
            npy_data_path=npy_data_path,
            npy_metadata_path=npy_metadata_path,
            create_empty=True,
            channel_count=channel_count,
            trace_count=trace_count,
            sample_count=sample_count,
            data_length=data_length,
            version=version,
            **kwargs,
        )

    def dump(self, path: str | None = None, **kwargs):
        if self._npy_trace_path is None or self._npy_data_path is None:
            raise Exception("trace and metadata path must not be None.")
        else:
            np.save(self._npy_trace_path, self._trace_array)
            np.save(self._npy_data_path, self._data_array)
            self._dump_metadata()

    def set_trace(self, channel_index: int, trace_index: int, trace: np.ndarray, data: np.ndarray | None):
        self._trace_array[channel_index, trace_index, :] = trace
        if self._data_length != 0 and data is not None:
            self._data_array[channel_index, trace_index, :] = data

    def _get_trace_data(self, channel_slice, trace_slice) -> tuple[list, list, np.ndarray, np.ndarray]:
        c, t = self._parse_slice(channel_slice, trace_slice)
        if isinstance(channel_slice, int):
            channel_slice = slice(channel_slice, channel_slice + 1)
        if isinstance(trace_slice, int):
            trace_slice = slice(trace_slice, trace_slice + 1)
        return c, t, self._trace_array[channel_slice, trace_slice], self._data_array[channel_slice, trace_slice]


# def add_trace(self, index: int, trace: np.ndarray, data: bytes):
#     self._trace_array[index:] = trace
#     self._data_array[index:] = data
#
# def load_from_numpy_data_file(self, path: str, transpose=False) -> "TraceDataset":
#     """
#     Load traces from numpy data file.
#     :param path: file path.
#     :param transpose: if axes 0 is not represent trace and axes 1 is not represent trace data(sample)
#     """
#     self.traces = np.load(path)
#     if transpose:
#         self.traces = self.traces.T
#         sample_count, trace_count = self.traces.shape
#     else:
#         trace_count, sample_count = self.traces.shape
#
#     self._metadata.trace_count = trace_count
#     self._metadata.sample_count = sample_count
#
#     return self
#
# def load_from_zarr(self, path: str, structure: str = "scarr"):
#     if structure == "scarr":
#         self.load_from_scarr(path)
#     # todo other
#
# def load_from_scarr(self, path: str):
#     scarr_data = zarr.open(path, "r")
#     self.traces = scarr_data["0/0/traces"]
#     trace_count = self.traces.shape[0]
#     sample_count = self.traces.shape[1]
#     data = scarr_data["0/0/plaintext"]
#
#     self._metadata.trace_count = trace_count
#     self._metadata.sample_count = sample_count
#     self.data = data
#
# def load_from_hdf5(self, path: str): ...
#
# # def add_trace(self, trace: np.ndarray, index: int = None):
# #     if index is None:
# #         index = self._current_create_trace_index
# #         self._current_create_trace_index += 1
# #     self.traces[index:] = trace
#
# def add_data(self, data: bytes, index: int = None):
#     if index is None:
#         index = self._current_create_data_index
#         self._current_create_data_index += 1
#     self.data[index:] = data
#
# def update_metadata_environment_info(self, cracknuts: str, cracker: str, nuts: str): ...
#
# def save_as_numpy_file(self, path):
#     np.save(os.path.join(path, "trace.npy"), self.traces)
#     np.save(os.path.join(path, "data.npy"), self.data)
#
# def save_as_zarr(self, path): ...  # todo
# ...
