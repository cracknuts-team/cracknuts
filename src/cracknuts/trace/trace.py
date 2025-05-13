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
    _data_plaintext_length: int | None
    _data_ciphertext_length: int | None
    _data_key_length: int | None
    _data_extended_length: int | None
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
        version,
        data_plaintext_length: int | None = None,
        data_ciphertext_length: int | None = None,
        data_key_length: int | None = None,
        data_extended_length: int | None = None,
        **kwargs,
    ) -> "TraceDataset": ...

    @abc.abstractmethod
    def dump(self, path: str | None = None, **kwargs): ...

    @abc.abstractmethod
    def set_trace(
        self,
        channel_name: str,
        trace_index: int,
        trace: np.ndarray,
        data: dict[str, np.ndarray[np.int8] | bytes] | None,
    ): ...

    @property
    def trace_data(self) -> TraceDatasetData:
        return TraceDatasetData(get_trace_data=self._get_trace_data)

    @property
    def trace(self):
        return TraceDatasetData(get_trace_data=self._get_trace)

    @property
    def data(self):
        return TraceDatasetData(get_trace_data=self._get_data)

    @property
    def trace_data_with_indices(self):
        return TraceDatasetData(get_trace_data=self._get_trace_data_with_indices)

    def __getitem__(self, item):
        return TraceDatasetData(get_trace_data=self._get_trace_data_with_indices)[item]

    @abc.abstractmethod
    def _get_trace_data_with_indices(
        self, channel_slice, trace_slice
    ) -> tuple[list, list, np.ndarray, list[list[dict[str, bytes | None]]]]: ...

    @abc.abstractmethod
    def _get_trace_data(self, channel_slice, trace_slice) -> tuple[np.ndarray, np.ndarray]: ...

    @abc.abstractmethod
    def _get_trace(self, channel_slice, trace_slice) -> np.ndarray: ...

    @abc.abstractmethod
    def _get_data(self, channel_slice, trace_slice) -> np.ndarray: ...

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
            self._channel_names,
            self._channel_count,
            self._trace_count,
            self._sample_count,
            self._data_plaintext_length,
            self._data_ciphertext_length,
            self._data_key_length,
            self._data_extended_length,
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
    def adata_plaintext_length(self):
        return self._data_plaintext_length

    @property
    def data_ciphertext_length(self):
        return self._data_ciphertext_length

    @property
    def data_key_length(self):
        return self._data_key_length

    @property
    def data_extended_length(self):
        return self._data_extended_length

    @property
    def create_time(self):
        return self._create_time


class _InfoRender:
    def __init__(
        self,
        channel_names: list[str],
        channel_count: int,
        trace_count: int,
        sample_count: int,
        data_plaintext_length: int,
        data_ciphertext_length: int,
        data_key_length: int,
        data_extended_length: int,
    ):
        self._channel_names: list[str] = channel_names
        self._channel_count: int = channel_count
        self._trace_count: int = trace_count
        self._sample_count: int = sample_count
        self._data_plaintext_length: int = data_plaintext_length
        self._data_ciphertext_length: int = data_ciphertext_length
        self._data_key_length: int = data_key_length
        self._data_extended_length: int = data_extended_length

    def __repr__(self):
        return (
            f"Channel: {self._channel_names}\r\n"
            f"Trace:   {self._trace_count}, {self._sample_count}\r\n"
            f"Data:    {self._trace_count} "
            f"plaintext: {self._data_plaintext_length} "
            f"ciphertext: {self._data_ciphertext_length} "
            f"key: {self._data_key_length} "
            f"extended: {self._data_extended_length}"
        )


class ScarrTraceDataset(TraceDataset):
    _ATTR_METADATA_KEY = "metadata"
    _GROUP_ROOT_PATH = "0"
    _ARRAY_TRACES_PATH = "traces"
    _ARRAY_DATA_PLAINTEXT_PATH = "plaintext"
    _ARRAY_DATA_CIPHERTEXT_PATH = "ciphertext"
    _ARRAY_DATA_KEY_PATH = "key"
    _ARRAY_DATA_EXTENDED_PATH = "extended"

    def __init__(
        self,
        zarr_path: str,
        create_empty: bool = False,
        channel_names: list[str] | None = None,
        trace_count: int | None = None,
        sample_count: int | None = None,
        data_plaintext_length: int | None = None,
        data_ciphertext_length: int | None = None,
        data_key_length: int | None = None,
        data_extended_length: int | None = None,
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
        self._data_plaintext_length: int = data_plaintext_length
        self._data_ciphertext_length: int = data_ciphertext_length
        self._data_key_length: int = data_key_length
        self._data_extended_length: int = data_extended_length
        self._create_time: int | None = create_time
        self._version: str | None = version

        self._logger = logger.get_logger(self)

        if zarr_kwargs is None:
            zarr_kwargs = {}
        if zarr_trace_group_kwargs is None:
            zarr_trace_group_kwargs = {}
        if zarr_data_group_kwargs is None:
            zarr_data_group_kwargs = {}

        mode = zarr_kwargs.pop("mode", "w" if create_empty else "r")
        self._zarr_data = zarr.open(zarr_path, mode=mode, **zarr_kwargs)

        if create_empty:
            if self._channel_names is None or self._trace_count is None or self._sample_count is None:
                raise ValueError(
                    "channel_names and trace_count and sample_count " "must be specified when in write mode."
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
                if self._data_plaintext_length is not None:
                    channel_group.create(
                        self._ARRAY_DATA_PLAINTEXT_PATH,
                        shape=(
                            self._trace_count,
                            self._data_plaintext_length,
                        ),
                    )
                if self._data_ciphertext_length is not None:
                    channel_group.create(
                        self._ARRAY_DATA_CIPHERTEXT_PATH,
                        shape=(
                            self._trace_count,
                            self._data_ciphertext_length,
                        ),
                    )
                if self._data_key_length is not None:
                    channel_group.create(
                        self._ARRAY_DATA_KEY_PATH,
                        shape=(
                            self._trace_count,
                            self._data_key_length,
                        ),
                    )
                if self._data_extended_length is not None:
                    channel_group.create(
                        self._ARRAY_DATA_EXTENDED_PATH,
                        shape=(
                            self._trace_count,
                            self._data_extended_length,
                        ),
                    )
            self._zarr_data.attrs[self._ATTR_METADATA_KEY] = {
                "create_time": self._create_time,
                "channel_names": self._channel_names,
                "trace_count": self._trace_count,
                "sample_count": self._sample_count,
                "data_plaintext_length": self._data_plaintext_length,
                "data_ciphertext_length": self._data_ciphertext_length,
                "data_key_length": self._data_key_length,
                "data_extended_length": self._data_extended_length,
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
            self._data_plaintext_length = metadata.get("data_plaintext_length")
            self._data_ciphertext_length = metadata.get("data_ciphertext_length")
            self._data_key_length = metadata.get("data_key_length")
            self._data_extended_length = metadata.get("data_extended_length")
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
        version: str,
        data_plaintext_length: int | None = None,
        data_ciphertext_length: int | None = None,
        data_key_length: int | None = None,
        data_extended_length: int | None = None,
        **kwargs,
    ) -> "TraceDataset":
        kwargs["mode"] = "w"
        return cls(
            path,
            create_empty=True,
            channel_names=channel_names,
            trace_count=trace_count,
            sample_count=sample_count,
            version=version,
            data_plaintext_length=data_plaintext_length,
            data_ciphertext_length=data_ciphertext_length,
            data_key_length=data_key_length,
            data_extended_length=data_extended_length,
            zarr_kwargs=kwargs,
        )

    def dump(self, path: str | None = None, **kwargs):
        if path is not None and path != self._zarr_path:
            zarr.copy_store(self._zarr_data, zarr.open(path, mode="w"))

    def set_trace(
        self,
        channel_name: str,
        trace_index: int,
        trace: np.ndarray,
        data: dict[str, np.ndarray[np.int8] | bytes] | None = None,
    ):
        if self._trace_count is None or self._channel_count is None:
            raise Exception("Channel or trace count must has not specified.")
        if channel_name not in self._channel_names:
            raise ValueError("channel index out range")
        if trace_index not in range(0, self._trace_count):
            raise ValueError("trace, index out of range")
        if self._sample_count != trace.shape[0]:
            self._logger.error(
                f"Trace sample count {trace.shape[0]} does not match the previously "
                f"defined value {self._sample_count}, so the trace will be ignored."
            )
            return
        channel_index = self._channel_names.index(channel_name)
        self._get_under_root(channel_index, self._ARRAY_TRACES_PATH)[trace_index] = trace
        if data is not None:
            channel_group = self._get_under_root(str(channel_index))
            for k, v in data.items():
                if isinstance(v, bytes):
                    v = np.frombuffer(v, dtype=np.uint8)
                data_item_group = channel_group.get(k)
                if data_item_group is None:
                    data_length = v.shape[0]
                    attrs = self._zarr_data.attrs[self._ATTR_METADATA_KEY]
                    if k == "plaintext":
                        self._data_plaintext_length = data_length
                        data_item_group = channel_group.create(
                            k,
                            shape=(
                                self._trace_count,
                                self._data_plaintext_length,
                            ),
                            dtype=np.uint8,
                        )
                        self._zarr_data.attrs[self._ATTR_METADATA_KEY] = attrs | {
                            "data_plaintext_length": self._data_plaintext_length
                        }
                    if k == "ciphertext":
                        self._data_ciphertext_length = data_length
                        data_item_group = channel_group.create(
                            k,
                            shape=(
                                self._trace_count,
                                self._data_ciphertext_length,
                            ),
                            dtype=np.uint8,
                        )
                        self._zarr_data.attrs[self._ATTR_METADATA_KEY] = attrs | {
                            "data_ciphertext_length": self._data_ciphertext_length
                        }
                    if k == "key":
                        self._data_key_length = data_length
                        data_item_group = channel_group.create(
                            k,
                            shape=(
                                self._trace_count,
                                self._data_key_length,
                            ),
                            dtype=np.uint8,
                        )
                        self._zarr_data.attrs[self._ATTR_METADATA_KEY] = attrs | {
                            "data_key_length": self._data_key_length
                        }
                    if k == "extended":
                        self._data_extended_length = data_length
                        data_item_group = channel_group.create(
                            k,
                            shape=(
                                self._trace_count,
                                self._data_extended_length,
                            ),
                            dtype=np.uint8,
                        )
                        self._zarr_data.attrs[self._ATTR_METADATA_KEY] = attrs | {
                            "data_extended_length": self._data_extended_length
                        }
                if data_item_group is not None:
                    data_item_group[trace_index] = v

    def get_origin_data(self) -> zarr.hierarchy.Group:
        return self._zarr_data

    def get_trace_by_indexes(
        self, channel_name: str, *trace_indexes: int
    ) -> tuple[np.ndarray, list[dict[str, bytes | None]]] | None:
        channel_index = self._channel_names.index(channel_name)
        return (
            self._get_under_root(channel_index, self._ARRAY_TRACES_PATH)[[i for i in trace_indexes]],
            [self._get_data_by_index(channel_index, trace_index) for trace_index in trace_indexes],
        )

    def _get_data_by_index(self, channel_index: int, trace_index: int) -> dict[str, bytes | None]:
        plaintext = self._get_under_root(channel_index, self._ARRAY_DATA_PLAINTEXT_PATH)
        ciphertext = self._get_under_root(channel_index, self._ARRAY_DATA_CIPHERTEXT_PATH)
        key = self._get_under_root(channel_index, self._ARRAY_DATA_KEY_PATH)
        extended = self._get_under_root(channel_index, self._ARRAY_DATA_EXTENDED_PATH)
        if plaintext is not None:
            plaintext = plaintext[trace_index]
            if ciphertext is not None:
                plaintext = plaintext.tobytes()
        if ciphertext is not None:
            ciphertext = ciphertext[trace_index]
            if ciphertext is not None:
                ciphertext = ciphertext.tobytes()
        if key is not None:
            key = key[trace_index]
            if key is not None:
                key = key.tobytes()
        if extended is not None:
            if extended is not None:
                extended = extended.tobytes()
        return {"plaintext": plaintext, "ciphertext": ciphertext, "key": key, "extend": extended}

    def get_trace_by_range(
        self, channel_name: str, index_start: int, index_end: int
    ) -> tuple[np.ndarray, list[dict[str, bytes | None]]] | None:
        channel_index = self._channel_names.index(channel_name)
        return (
            self._get_under_root(channel_index, self._ARRAY_TRACES_PATH)[index_start:index_end],
            [self._get_data_by_index(channel_index, trace_index) for trace_index in range(index_start, index_end)],
        )

    def _get_under_root(self, *paths: typing.Any):
        paths = self._GROUP_ROOT_PATH, *paths
        path = "/".join(str(path) for path in paths)
        if path in self._zarr_data:
            return self._zarr_data[path]
        else:
            return None

    def _get_trace_data_with_indices(
        self, channel_slice, trace_slice
    ) -> tuple[list, list, np.ndarray, list[list[dict[str, bytes | None]]]]:
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
            data.append([self._get_data_by_index(channel_index, trace_index) for trace_index in trace_indexes])

        return channel_indexes, trace_indexes, np.array(traces), data

    def _get_trace_data(self, channel_slice, trace_slice) -> tuple[np.ndarray, list[list[dict[str, bytes | None]]]]:
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
            data.append([self._get_data_by_index(channel_index, trace_index) for trace_index in trace_indexes])

        return np.vstack(traces), data

    def _get_trace(self, channel_slice, trace_slice) -> np.ndarray:
        traces = []

        channel_indexes = self._parse_slice(self.channel_count, channel_slice)

        if isinstance(trace_slice, int):
            trace_slice = slice(trace_slice, trace_slice + 1)

        for channel_index in channel_indexes:
            traces.append(self._get_under_root(channel_index, self._ARRAY_TRACES_PATH)[trace_slice])

        return np.vstack(traces) if len(traces) == 1 else np.stack(traces)

    def _get_data(self, channel_slice, trace_slice) -> list[list[dict[str, bytes | None]]]:
        data = []

        channel_indexes, trace_indexes = (
            self._parse_slice(self._channel_count, channel_slice),
            self._parse_slice(self._trace_count, trace_slice),
        )

        for channel_index in channel_indexes:
            data.append([self._get_data_by_index(channel_index, trace_index) for trace_index in trace_indexes])

        return data


class NumpyTraceDataset(TraceDataset):
    _ARRAY_TRACE_PATH = "trace.npy"
    _ARRAY_PLAINTEXT_PATH = "plaintext.npy"
    _ARRAY_CIPHERTEXT_PATH = "ciphertext.npy"
    _ARRAY_KEY_PATH = "key.npy"
    _ARRAY_EXTENDED_PATH = "extended.npy"

    _METADATA_PATH = "metadata.json"

    def __init__(
        self,
        path: str | None = None,
        create_empty: bool = False,
        channel_names: list[str] | None = None,
        trace_count: int | None = None,
        sample_count: int | None = None,
        trace_dtype: np.dtype = np.int16,
        data_plaintext_length: int | None = None,
        data_ciphertext_length: int | None = None,
        data_key_length: int | None = None,
        data_extended_length: int | None = None,
        create_time: int | None = None,
        version: str | None = None,
    ):
        self._logger = logger.get_logger(NumpyTraceDataset)

        self._channel_names: list[str] | None = channel_names
        self._channel_count: int | None = None if self._channel_names is None else len(self._channel_names)
        self._trace_count: int | None = trace_count
        self._sample_count: int | None = sample_count
        self._data_plaintext_length: int | None = data_plaintext_length
        self._data_ciphertext_length: int | None = data_ciphertext_length
        self._data_key_length: int | None = data_key_length
        self._data_extended_length: int | None = data_extended_length
        self._create_time: int | None = create_time
        self._version: str | None = version

        self._trace_array: np.ndarray | None = None
        self._plaintext_array: np.ndarray | None = None
        self._ciphertext_array: np.ndarray | None = None
        self._key_array: np.ndarray | None = None
        self._extended_array: np.ndarray | None = None

        if path is not None:
            self._set_path(path)
            self._npy_metadata_path: str = os.path.join(path, self._METADATA_PATH)

        if create_empty:
            if self._channel_names is None or self._trace_count is None or self._sample_count is None:
                raise ValueError(
                    "channel_names and trace_count and sample_count " "must be specified when in write mode."
                )
            self._trace_array = np.zeros(
                shape=(self._channel_count, self._trace_count, self._sample_count), dtype=trace_dtype
            )
            if self._data_plaintext_length is not None:
                self._plaintext_array = np.zeros(
                    shape=(self._channel_count, self._trace_count, self._data_plaintext_length), dtype=np.uint8
                )
            if self._data_ciphertext_length is not None:
                self._ciphertext_array = np.zeros(
                    shape=(self._channel_count, self._trace_count, self._data_ciphertext_length), dtype=np.uint8
                )
            if self._data_key_length is not None:
                self._key_array = np.zeros(
                    shape=(self._channel_count, self._trace_count, self._data_key_length), dtype=np.uint8
                )
            if self._data_extended_length is not None:
                self._extended_array = np.zeros(
                    shape=(self._channel_count, self._trace_count, self._data_extended_length), dtype=np.uint8
                )
            self._create_time = int(time.time())

        else:
            if path is None:
                print("path is required if create_empty is False")
            else:
                self._trace_array = np.load(self._npy_trace_path)

                if not os.path.exists(self._npy_data_plaintext_path):
                    self._logger.warning("npy_data_plaintext_path is not specified, plaintext will be not load.")
                else:
                    self._plaintext_array = np.load(self._npy_data_plaintext_path)

                if not os.path.exists(self._npy_data_ciphertext_path):
                    self._logger.warning("npy_data_ciphertext_path is not specified, ciphertext will be not load.")
                else:
                    self._ciphertext_array = np.load(self._npy_data_ciphertext_path)

                if not os.path.exists(self._npy_data_key_path):
                    self._logger.info("npy_data_key_path is not specified, key will be not load.")
                else:
                    self._key_array = np.load(self._npy_data_key_path)

                if not os.path.exists(self._npy_data_extended_path):
                    self._logger.info("npy_data_extended_path is not specified, extended will be not load.")
                else:
                    self._extended_array = np.load(self._npy_data_extended_path)

                if not os.path.exists(self._npy_metadata_path):
                    self._logger.info("npy_metadata_path is not specified, metadata will be not load.")
                else:
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
            self._data_plaintext_length: int | None = metadata.get("data_plaintext_length")
            self._data_ciphertext_length: int | None = metadata.get("data_ciphertext_length")
            self._data_key_length: int | None = metadata.get("data_key_length")
            self._data_extended_length: int | None = metadata.get("data_extended_length")
            self._create_time: int | None = metadata.get("create_time")
            self._version: str | None = metadata.get("version")

    def _dump_metadata(self):
        with open(self._npy_metadata_path, "w", encoding="utf-8") as f:
            json.dump(
                {
                    "channel_names": self._channel_names,
                    "trace_count": self._trace_count,
                    "sample_count": self._sample_count,
                    "data_plaintext_length": self._data_plaintext_length,
                    "data_ciphertext_length": self._data_ciphertext_length,
                    "data_key_length": self._data_key_length,
                    "data_extended_length": self._data_extended_length,
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
            path,
            **kwargs,
        )

    @classmethod
    def load_from_numpy_array(cls, trace: np.ndarray):
        channel_count = None
        trace_count = None
        sample_count = None

        shape = trace.shape

        array_size = len(shape)

        if array_size == 1:
            channel_count = 1
            trace_count = 1
            sample_count = shape[0]
        elif array_size == 2:
            channel_count = 1
            trace_count = shape[0]
            sample_count = shape[1]
        elif array_size == 3:
            channel_count = shape[0]
            trace_count = shape[1]
            sample_count = shape[2]

        channel_names = []
        for i in range(channel_count):
            channel_names.append(str(i))

        ds = cls(
            create_empty=True,
            channel_names=channel_names,
            trace_count=trace_count,
            sample_count=sample_count,
            trace_dtype=trace.dtype,
        )

        if array_size == 1:
            ds.set_trace(0, 0, trace, None)
        elif array_size == 2:
            for t in range(shape[0]):
                ds.set_trace(0, t, trace[t], None)
        elif array_size == 3:
            for c in range(shape[0]):
                for t in range(shape[1]):
                    ds.set_trace(c, t, trace[c, t], None)

        return ds

    @classmethod
    def new(
        cls,
        path: str,
        channel_names: list[str],
        trace_count: int,
        sample_count: int,
        version: str,
        data_plaintext_length: int | None = None,
        data_ciphertext_length: int | None = None,
        data_key_length: int | None = None,
        data_extended_length: int | None = None,
        **kwargs,
    ) -> "TraceDataset":
        if not os.path.exists(path):
            os.makedirs(path)
        elif os.path.isfile(path):
            raise Exception(f"{path} is not a file.")

        return cls(
            path=path,
            create_empty=True,
            channel_names=channel_names,
            trace_count=trace_count,
            sample_count=sample_count,
            version=version,
            data_plaintext_length=data_plaintext_length,
            data_ciphertext_length=data_ciphertext_length,
            data_key_length=data_key_length,
            data_extended_length=data_extended_length,
            **kwargs,
        )

    def _set_path(self, path: str):
        self._npy_trace_path: str = os.path.join(path, self._ARRAY_TRACE_PATH)
        self._npy_data_plaintext_path: str = os.path.join(path, self._ARRAY_PLAINTEXT_PATH)
        self._npy_data_ciphertext_path: str = os.path.join(path, self._ARRAY_CIPHERTEXT_PATH)
        self._npy_data_key_path: str = os.path.join(path, self._ARRAY_KEY_PATH)
        self._npy_data_extended_path: str = os.path.join(path, self._ARRAY_EXTENDED_PATH)

    def dump(self, path: str | None = None, **kwargs):
        if path is not None:
            self._set_path(path)
        if self._npy_trace_path is None:
            print("Path must be provided, either as an argument or set in __init__.")
            return
        np.save(self._npy_trace_path, self._trace_array)

        if self._plaintext_array is not None:
            np.save(self._npy_data_plaintext_path, self._plaintext_array)
        if self._ciphertext_array is not None:
            np.save(self._npy_data_ciphertext_path, self._ciphertext_array)
        if self._key_array is not None:
            np.save(self._npy_data_key_path, self._key_array)
        if self._extended_array is not None:
            np.save(self._npy_data_extended_path, self._extended_array)
        self._dump_metadata()

    def set_trace(self, channel_name: str | int, trace_index: int, trace: np.ndarray, data: dict[str, bytes] | None):
        if isinstance(channel_name, int):
            channel_index = channel_name
        else:
            channel_index = self._channel_names.index(channel_name)

        self._trace_array[channel_index, trace_index, :] = trace

        data_plaintext = None if data is None else data.get("plaintext")
        data_ciphertext = None if data is None else data.get("ciphertext")
        data_key = None if data is None else data.get("key")
        data_extended = None if data is None else data.get("extended")

        if data_plaintext is not None:
            if self._plaintext_array is None:
                item_length = len(data_plaintext)
                self._plaintext_array = np.zeros(
                    shape=(self._channel_count, self._sample_count, item_length), dtype=np.uint8
                )
            self._plaintext_array[channel_index, trace_index, :] = np.frombuffer(data_plaintext, dtype=np.uint8)
        if data_ciphertext is not None:
            if self._ciphertext_array is None:
                item_length = len(data_ciphertext)
                self._ciphertext_array = np.zeros(
                    shape=(self._channel_count, self._sample_count, item_length), dtype=np.uint8
                )
            self._ciphertext_array[channel_index, trace_index, :] = np.frombuffer(data_ciphertext, dtype=np.uint8)
        if data_key is not None:
            if self._key_array is None:
                item_length = len(data_key)
                self._key_array = np.zeros(shape=(self._channel_count, self._sample_count, item_length), dtype=np.uint8)
            self._key_array[channel_index, trace_index, :] = np.frombuffer(data_key, dtype=np.uint8)
        if data_extended is not None:
            if self._extended_array is None:
                item_length = len(data_extended)
                self._extended_array = np.zeros(
                    shape=(self._channel_count, self._sample_count, item_length), dtype=np.uint8
                )
            self._key_array[channel_index, trace_index, :] = np.frombuffer(data_extended, dtype=np.uint8)

    def _get_trace_data_with_indices(
        self, channel_slice, trace_slice
    ) -> tuple[list, list, np.ndarray, list[list[dict[str, bytes | None]]]]:
        c = self._parse_slice(self._channel_count, channel_slice)
        t = self._parse_slice(self._trace_count, trace_slice)
        if isinstance(channel_slice, int):
            channel_slice = slice(channel_slice, channel_slice + 1)
        if isinstance(trace_slice, int):
            trace_slice = slice(trace_slice, trace_slice + 1)
        plaintext = None if self._plaintext_array is None else self._plaintext_array[channel_slice, trace_slice]
        ciphertext = None if self._ciphertext_array is None else self._ciphertext_array[channel_slice, trace_slice]
        key = None if self._key_array is None else self._key_array[channel_slice, trace_slice]
        extended = None if self._extended_array is None else self._extended_array[channel_slice, trace_slice]

        return c, t, self._trace_array[channel_slice, trace_slice], [plaintext, ciphertext, key, extended]

    def _get_trace_data(self, channel_slice, trace_slice) -> tuple[np.ndarray, list[list[dict[str, bytes | None]]]]:
        data = []

        channel_indexes, trace_indexes = (
            self._parse_slice(self._channel_count, channel_slice),
            self._parse_slice(self._trace_count, trace_slice),
        )

        if isinstance(trace_slice, int):
            trace_slice = slice(trace_slice, trace_slice + 1)

        traces = self._trace_array[channel_slice, trace_slice]
        for channel_index in channel_indexes:
            data.append([self._get_data_by_index(channel_index, trace_index) for trace_index in trace_indexes])

        return traces, data

    def _get_trace(self, channel_slice, trace_slice) -> np.ndarray:
        return self._trace_array[channel_slice, trace_slice]

    def _get_data(self, channel_slice, trace_slice) -> list[list[dict[str, bytes | None]]]:
        data = []

        channel_indexes, trace_indexes = (
            self._parse_slice(self._channel_count, channel_slice),
            self._parse_slice(self._trace_count, trace_slice),
        )

        for channel_index in channel_indexes:
            data.append([self._get_data_by_index(channel_index, trace_index) for trace_index in trace_indexes])

        return data

    def _get_data_by_index(self, channel_index: int, trace_index: int) -> dict[str, bytes | None]:
        data = {}
        if self._plaintext_array is not None:
            data["plaintext"] = self._plaintext_array[channel_index, trace_index].tobytes()
        if self._ciphertext_array is not None:
            data["ciphertext"] = self._ciphertext_array[channel_index, trace_index].tobytes()
        if self._key_array is not None:
            data["key"] = self._key_array[channel_index, trace_index].tobytes()
        if self._extended_array is not None:
            data["extended"] = self._extended_array[channel_index, trace_index].tobytes()
        return data
