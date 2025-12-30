import time
import zarr
import numcodecs
import numpy as np

def benchmark(shape=(10_000_000,), chunk_sizes=[10_000, 100_000, 1_000_000], compressors=None):
    if compressors is None:
        compressors = [
            None,
            numcodecs.Blosc(cname="zstd", clevel=1, shuffle=2),
            numcodecs.Blosc(cname="zstd", clevel=5, shuffle=2),
        ]

    data = np.random.rand(*shape).astype("f4")

    for chunks in chunk_sizes:
        for compressor in compressors:
            store_name = f"test_{shape[0]}_chunks{chunks}_comp{compressor}.zarr"
            z = zarr.open(
                store_name,
                mode="w",
                shape=shape,
                chunks=(chunks,),
                dtype="f4",
                compressor=compressor,
            )

            t0 = time.time()
            z[:] = data
            t1 = time.time()

            print(
                f"Shape={shape}, Chunk={chunks}, "
                f"Compressor={compressor}, "
                f"Time={t1 - t0:.2f}s"
            )


if __name__ == "__main__":
    benchmark()
