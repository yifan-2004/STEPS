"""Read frozen forecasts and split series without shipping datasets or weights."""
from __future__ import annotations
import json
from pathlib import Path
import numpy as np

def load(cache_dir, dataset, horizon, split, backbone, seed, epochs, batch_size):
    folder = Path(cache_dir) / f"{backbone}_{dataset}_H{horizon}_seed{seed}_ep{epochs}_b{batch_size}" / split
    metadata = json.loads((folder / "metadata.json").read_text())
    prediction = np.load(folder / "prediction.npy", mmap_mode="r", allow_pickle=False)
    series = np.load(folder / "series.npy", mmap_mode="r", allow_pickle=False)
    n, h, channels = prediction.shape
    lookback = int(metadata["lookback"])
    if h != horizon or series.ndim != 2 or series.shape[1] != channels or len(series) < lookback + horizon + n - 1:
        raise ValueError(f"Invalid cache dimensions in {folder}")
    history = np.lib.stride_tricks.sliding_window_view(series, lookback, axis=0)[:n].transpose(0, 2, 1)
    target = np.lib.stride_tricks.sliding_window_view(series[lookback:], horizon, axis=0)[:n].transpose(0, 2, 1)
    return prediction, history, target, metadata
