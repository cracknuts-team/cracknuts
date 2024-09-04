import os
from typing import Any

import numpy as np
import pandas as pd
import zarr


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
