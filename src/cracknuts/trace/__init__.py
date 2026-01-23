# Copyright 2024 CrackNuts. All rights reserved.

from cracknuts.trace.trace import ZarrTraceDataset, TraceDataset
from cracknuts.trace.trace import ScarrTraceDataset
from cracknuts.trace.trace import NumpyTraceDataset


def load_trace_dataset(path: str) -> TraceDataset:
    """
    Load a TraceDataset from the given path.

    :param path: Path to the dataset
    :type path: str
    :return: TraceDataset instance
    :rtype: TraceDataset
    """
    path = path.rstrip("/\\")
    if path.endswith(".zarr"):
        return ZarrTraceDataset(path)
    elif path.endswith(".numpy"):
        return NumpyTraceDataset.load(path)
    else:
        raise ValueError(f"Unsupported trace dataset format: {path}")


__all__ = ["TraceDataset", "ZarrTraceDataset", "ScarrTraceDataset", "NumpyTraceDataset", "load_trace_dataset"]
