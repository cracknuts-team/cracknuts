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
        get_trace_data: typing.Callable[[typing.Any, typing.Any], tuple | np.ndarray],
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
    _channel_names: list[str] | None
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
        cls,
        path: str,
        channel_names: list[str],
        trace_count: int,
        sample_count: int,
        data_length: int,
        version,
        **kwargs,
    ) -> "TraceDataset": ...

    @abc.abstractmethod
    def dump(self, path: str | None = None, **kwargs): ...

    @abc.abstractmethod
    def set_trace(self, channel_name: str, trace_index: int, trace: np.ndarray, data: np.ndarray | None): ...

    @property
    def trace_data(self) -> TraceDatasetData:
        return TraceDatasetData(get_trace_data=self._get_trace_data)

    @property
    def trace(self):
        return TraceDatasetData(get_trace_data=self._get_trace)

    @property
    def plain_text(self):
        return TraceDatasetData(get_trace_data=self._get_plaintext)

    @property
    def trace_data_with_indices(self):
        return TraceDatasetData(get_trace_data=self._get_trace_data_with_indices)

    def __getitem__(self, item):
        return TraceDatasetData(get_trace_data=self._get_trace_data_with_indices)[item]

    @abc.abstractmethod
    def _get_trace_data_with_indices(self, channel_slice, trace_slice) -> tuple[list, list, np.ndarray, np.ndarray]: ...

    # This method should return trace, plaintext, and ciphertext.
    # However, the ciphertext is currently empty, so it only returns trace and plaintext.
    @abc.abstractmethod
    def _get_trace_data(self, channel_slice, trace_slice) -> tuple[np.ndarray, np.ndarray]: ...

    @abc.abstractmethod
    def _get_trace(self, channel_slice, trace_slice) -> np.ndarray: ...

    @abc.abstractmethod
    def _get_plaintext(self, channel_slice, trace_slice) -> np.ndarray: ...

    @abc.abstractmethod
    def _get_ciphertext(self, channel_slice, trace_slice) -> np.ndarray: ...

    @staticmethod
    def _parse_slice(origin_count, index_slice) -> list:
        if origin_count is None:
            raise Exception("origin_count is not set")
        if isinstance(index_slice, slice):
            start, stop, step = index_slice.indices(origin_count)
            indices = [i for i in range(start, stop, step)]
        elif isinstance(index_slice, int):
            indices = [index_slice]
        elif isinstance(index_slice, list):
            indices = index_slice
        else:
            raise ValueError("index_slice is not a slice or list")
        return indices

    def __repr__(self):
        t = type(self)
        return f"<{t.__module__}.{t.__name__} ({self._channel_names}, {self._trace_count})"

    def info(self):
        return _InfoRender(
            self._channel_names, self._channel_count, self._trace_count, self._sample_count, self._data_length
        )

    @property
    def channel_names(self):
        return self._channel_names

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


class _InfoRender:
    def __init__(
        self, channel_names: list[str], channel_count: int, trace_count: int, sample_count: int, data_length: int
    ):
        self._channel_names: list[str] = channel_names
        self._channel_count: int = channel_count
        self._trace_count: int = trace_count
        self._sample_count: int = sample_count
        self._data_length: int = data_length

    def __repr__(self):
        return (
            f"Channel: {self._channel_names}\r\n"
            f"Trace:   {self._trace_count}, {self._sample_count}\r\n"
            f"Data:    {self._trace_count}, {self._data_length}"
        )


class ScarrTraceDataset(TraceDataset):
    _ATTR_METADATA_KEY = "metadata"
    _GROUP_ROOT_PATH = "0"
    _ARRAY_TRACES_PATH = "traces"
    _ARRAY_PLAINTEXT_PATH = "plaintext"

    def __init__(
        self,
        zarr_path: str,
        create_empty: bool = False,
        channel_names: list[str] | None = None,
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
        self._channel_names: list[str] | None = channel_names
        self._channel_count = None if self._channel_names is None else len(self._channel_names)
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
                self._channel_names is None
                or self._trace_count is None
                or self._sample_count is None
                or self._data_length is None
            ):
                raise ValueError(
                    "channel_names and trace_count and sample_count and data_length "
                    "must be specified when in write mode."
                )
            self._create_time = int(time.time())
            group_root = self._zarr_data.create_group(self._GROUP_ROOT_PATH)
            for i, _ in enumerate(self._channel_names):
                channel_group = group_root.create_group(str(i))
                channel_group.create(
                    self._ARRAY_TRACES_PATH,
                    shape=(self._trace_count, self._sample_count),
                    dtype=trace_dtype,
                    **zarr_trace_group_kwargs,
                )
                channel_group.create(
                    self._ARRAY_PLAINTEXT_PATH,
                    shape=(self._trace_count, self._data_length),
                    dtype=np.uint8,
                    **zarr_data_group_kwargs,
                )
            self._zarr_data.attrs[self._ATTR_METADATA_KEY] = {
                "create_time": self._create_time,
                "channel_names": self._channel_names,
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
            # This is a piece of logic for handling dataset files compatible with previous versions,
            # which will be removed in subsequent stable versions.
            if "channel_names" not in metadata:
                self._channel_count = metadata.get("channel_count")
                self._channel_names = [str(i) for i in range(self._channel_count)]
            else:
                self._channel_names = metadata.get("channel_names")
                self._channel_count = len(self._channel_names)
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
        channel_names: list[str],
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
            channel_names=channel_names,
            trace_count=trace_count,
            sample_count=sample_count,
            data_length=data_length,
            version=version,
            zarr_kwargs=kwargs,
        )

    def dump(self, path: str | None = None, **kwargs):
        if path is not None and path != self._zarr_path:
            zarr.copy_store(self._zarr_data, zarr.open(path, mode="w"))

    def set_trace(self, channel_name: str, trace_index: int, trace: np.ndarray, data: np.ndarray | None):
        if self._trace_count is None or self._channel_count is None:
            raise Exception("Channel or trace count must has not specified.")
        if channel_name not in self._channel_names:
            raise ValueError("channel index out range")
        if trace_index not in range(0, self._trace_count):
            raise ValueError("trace, index out of range")
        channel_index = self._channel_names.index(channel_name)
        self._get_under_root(channel_index, self._ARRAY_TRACES_PATH)[trace_index] = trace
        if self._data_length != 0 and data is not None:
            self._get_under_root(channel_index, self._ARRAY_PLAINTEXT_PATH)[trace_index] = data

    def get_origin_data(self) -> zarr.hierarchy.Group:
        return self._zarr_data

    def get_trace_by_indexes(self, channel_name: str, *trace_indexes: int) -> tuple[np.ndarray, np.ndarray] | None:
        channel_index = self._channel_names.index(channel_name)
        return (
            self._get_under_root(channel_index, self._ARRAY_TRACES_PATH)[[i for i in trace_indexes]],
            self._get_under_root(channel_index, self._ARRAY_PLAINTEXT_PATH)[[i for i in trace_indexes]],
        )

    def get_trace_by_range(
        self, channel_name: str, index_start: int, index_end: int
    ) -> tuple[np.ndarray, np.ndarray] | None:
        channel_index = self._channel_names.index(channel_name)
        return (
            self._get_under_root(channel_index, self._ARRAY_TRACES_PATH)[index_start:index_end],
            self._get_under_root(channel_index, self._ARRAY_PLAINTEXT_PATH)[index_start:index_end],
        )

    def _get_under_root(self, *paths: typing.Any):
        paths = self._GROUP_ROOT_PATH, *paths
        return self._zarr_data["/".join(str(path) for path in paths)]

    def _get_trace_data_with_indices(self, channel_slice, trace_slice) -> tuple[list, list, np.ndarray, np.ndarray]:
        traces = []
        data = []

        channel_indexes, trace_indexes = (
            self._parse_slice(self._channel_count, channel_slice),
            self._parse_slice(self._trace_count, trace_slice),
        )

        if isinstance(trace_slice, int):
            trace_slice = slice(trace_slice, trace_slice + 1)

        for channel_index in channel_indexes:
            traces.append(self._get_under_root(channel_index, self._ARRAY_TRACES_PATH)[trace_slice])
            data.append(self._get_under_root(channel_index, self._ARRAY_PLAINTEXT_PATH)[trace_slice])

        return channel_indexes, trace_indexes, np.array(traces), np.array(data)

    def _get_trace_data(self, channel_slice, trace_slice) -> tuple[np.ndarray, np.ndarray]:
        traces = []
        plaintext = []

        channel_indexes = self._parse_slice(self.channel_count, channel_slice)

        if isinstance(trace_slice, int):
            trace_slice = slice(trace_slice, trace_slice + 1)

        for channel_index in channel_indexes:
            traces.append(self._get_under_root(channel_index, self._ARRAY_TRACES_PATH)[trace_slice])
            plaintext.append(self._get_under_root(channel_index, self._ARRAY_PLAINTEXT_PATH)[trace_slice])

        return np.vstack(traces), np.vstack(plaintext)

    def _get_trace(self, channel_slice, trace_slice) -> np.ndarray:
        traces = []

        channel_indexes = self._parse_slice(self.channel_count, channel_slice)

        if isinstance(trace_slice, int):
            trace_slice = slice(trace_slice, trace_slice + 1)

        for channel_index in channel_indexes:
            traces.append(self._get_under_root(channel_index, self._ARRAY_TRACES_PATH)[trace_slice])

        return np.vstack(traces) if len(traces) == 1 else np.stack(traces)

    def _get_plaintext(self, channel_slice, trace_slice) -> np.ndarray:
        plaintext = []

        channel_indexes = self._parse_slice(self.channel_count, channel_slice)

        if isinstance(trace_slice, int):
            trace_slice = slice(trace_slice, trace_slice + 1)

        for channel_index in channel_indexes:
            plaintext.append(self._get_under_root(channel_index, self._ARRAY_PLAINTEXT_PATH)[trace_slice])

        return np.vstack(plaintext) if len(plaintext) == 1 else np.stack(plaintext)

    def _get_ciphertext(self, channel_slice, trace_slice) -> np.ndarray: ...


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
        channel_names: list[str] | None = None,
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

        self._channel_names: list[str] | None = channel_names
        self._channel_count: int | None = None if self._channel_names is None else len(self._channel_names)
        self._trace_count: int | None = trace_count
        self._sample_count: int | None = sample_count
        self._data_length: int | None = data_length
        self._create_time: int | None = create_time
        self._version: str | None = version

        self._trace_array: np.ndarray
        self._data_array: np.ndarray

        if create_empty:
            if (
                self._channel_names is None
                or self._trace_count is None
                or self._sample_count is None
                or self._data_length is None
            ):
                raise ValueError(
                    "channel_names and trace_count and sample_count and data_length "
                    "must be specified when in write mode."
                )
            self._trace_array = np.zeros(
                shape=(self._channel_count, self._trace_count, self._sample_count), dtype=trace_dtype
            )
            self._plaintext_array = np.zeros(
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
                self._plaintext_array = np.load(self._npy_data_path)
                self._load_metadata()

    def _load_metadata(self):
        with open(self._npy_metadata_path) as f:
            metadata = json.load(f)
            # This is a piece of logic for handling dataset files compatible with previous versions,
            # which will be removed in subsequent stable versions.
            if "channel_names" not in metadata:
                self._channel_count = metadata["channel_count"]
                self._channel_names = [str(i) for i in range(self._channel_count)]
            else:
                self._channel_names: list[str] | None = metadata.get("channel_names")
                self._channel_count: int | None = len(self._channel_names)
            self._trace_count: int | None = metadata.get("trace_count")
            self._sample_count: int | None = metadata.get("sample_count")
            self._data_length: int | None = metadata.get("data_length")
            self._create_time: int | None = metadata.get("create_time")
            self._version: str | None = metadata.get("version")

    def _dump_metadata(self):
        with open(self._npy_metadata_path, "w") as f:
            json.dump(
                {
                    "channel_names": self._channel_names,
                    "trace_count": self._trace_count,
                    "sample_count": self._sample_count,
                    "data_length": self._data_length,
                    "create_time": self._create_time,
                    "version": self._version,
                },
                f,
            )

    def get_origin_data(self) -> tuple[np.array, np.array]:
        return self._trace_array, self._plaintext_array

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

        channel_names = []
        for i in range(channel_count):
            channel_names.append(str(i))

        ds = cls(
            create_empty=True,
            channel_names=channel_names,
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
        channel_names: list[str],
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
            channel_names=channel_names,
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
            np.save(self._npy_data_path, self._plaintext_array)
            self._dump_metadata()

    def set_trace(self, channel_name: str | int, trace_index: int, trace: np.ndarray, data: np.ndarray | None):
        if isinstance(channel_name, int):
            channel_index = channel_name
        else:
            channel_index = self._channel_names.index(channel_name)
        self._trace_array[channel_index, trace_index, :] = trace
        if self._data_length != 0 and data is not None:
            self._plaintext_array[channel_index, trace_index, :] = data

    def _get_trace_data_with_indices(self, channel_slice, trace_slice) -> tuple[list, list, np.ndarray, np.ndarray]:
        c = self._parse_slice(self._channel_count, channel_slice)
        t = self._parse_slice(self._trace_count, trace_slice)
        if isinstance(channel_slice, int):
            channel_slice = slice(channel_slice, channel_slice + 1)
        if isinstance(trace_slice, int):
            trace_slice = slice(trace_slice, trace_slice + 1)
        return c, t, self._trace_array[channel_slice, trace_slice], self._plaintext_array[channel_slice, trace_slice]

    def _get_trace_data(self, channel_slice, trace_slice) -> tuple[np.ndarray, np.ndarray]:
        pass

    def _get_trace(self, channel_slice, trace_slice) -> np.ndarray:
        return self._trace_array[channel_slice, trace_slice]

    def _get_plaintext(self, channel_slice, trace_slice) -> np.ndarray:
        return self._plaintext_array[channel_slice, trace_slice]

    def _get_ciphertext(self, channel_slice, trace_slice) -> np.ndarray:
        pass
