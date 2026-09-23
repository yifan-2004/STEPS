"""Final STEPS residual adapter; extracted from the final 144-cell grid implementation."""
from __future__ import annotations

import numpy as np
from scipy.fft import dct, idct
from scipy.linalg import eigh, cho_factor, cho_solve

WIDTHS = [4, 12, 24, 48, 96, 192, 336, 720, 1080]
RIDGES = [1e-3, 1e-2, 1e-1, 1.0, 10.0, 100.0]
RANKS = [8, 16, 32, 64]

def residual_records(prediction: np.ndarray, target: np.ndarray, modes: int = 4) -> np.ndarray:
    """One low-frequency residual-state record per origin and channel."""
    error = np.asarray(target, dtype=np.float64) - np.asarray(prediction, dtype=np.float64)
    return dct(error, axis=1, norm="ortho")[:, :modes, :].transpose(0, 2, 1)


def causal_multiscale(records: np.ndarray, carry: np.ndarray, horizon: int) -> tuple[np.ndarray, np.ndarray]:
    """Aggregate only records whose complete horizon has already arrived."""
    records = np.asarray(records, dtype=np.float64)
    carry = np.asarray(carry, dtype=np.float64)
    joined = np.concatenate([carry, records], axis=0)
    offset, n, channels, modes = len(carry), len(records), records.shape[1], records.shape[2]
    prefix = np.concatenate([np.zeros((1, channels, modes)), np.cumsum(joined, axis=0)], axis=0)
    out = np.zeros((n, channels, len(WIDTHS), modes), dtype=np.float64)
    lengths = np.zeros(n, dtype=np.int32)
    for i in range(n):
        end = offset + max(0, i - horizon + 1)
        lengths[i] = min(end, WIDTHS[-1])
        for wi, width in enumerate(WIDTHS):
            start = max(0, end - width)
            count = end - start
            if count:
                out[i, :, wi] = (prefix[end] - prefix[start]) / count
    return out, lengths


def current_features(prediction: np.ndarray, history: np.ndarray) -> np.ndarray:
    """Shift/scale-stable forecast and input descriptors for each channel."""
    p = np.asarray(prediction, dtype=np.float64)
    x = np.asarray(history, dtype=np.float64)
    mean = x.mean(axis=1)
    scale = np.sqrt(x.var(axis=1) + 1e-5)
    pn = (p - mean[:, None, :]) / scale[:, None, :]
    xn = (x - mean[:, None, :]) / scale[:, None, :]
    pf = dct(pn, axis=1, norm="ortho")[:, :16, :].transpose(0, 2, 1)
    xf = dct(xn, axis=1, norm="ortho")[:, :8, :].transpose(0, 2, 1)
    stats = np.stack([xn[:, -1], xn[:, -1] - xn[:, -24:].mean(1),
                      pn.mean(1), pn[:, -1] - pn[:, 0]], axis=-1)
    return np.concatenate([pf, xf, stats], axis=-1)


def make_features(current: np.ndarray, bank: np.ndarray, lengths: np.ndarray, variant: str) -> np.ndarray:
    n, channels = current.shape[:2]
    length = np.stack([lengths / WIDTHS[-1],
                       np.log1p(lengths) / np.log1p(WIDTHS[-1])], axis=-1)
    length = np.repeat(length[:, None, :], channels, axis=1)
    if variant == "MSMean-LR":
        state = bank[..., :1].reshape(n, channels, -1)
        return np.concatenate([current, state, length], axis=-1)
    state = bank.reshape(n, channels, -1)
    if variant == "MSSpectral-LR":
        return np.concatenate([current, state, length], axis=-1)
    if variant != "MSRegime-LR":
        raise ValueError(variant)
    # Bounded, mechanism-specific nonlinear terms: fast/slow disagreement
    # measures regime change, and its interaction with the current forecast
    # lets the correction depend on which regime the backbone is forecasting.
    fast = bank[:, :, 0]                    # last 4 mature residual records
    medium = bank[:, :, 4]                  # last 96
    slow = bank[:, :, -1]                   # last 1080
    drift = fast - slow
    bend = fast - 2.0 * medium + slow
    denom = 1.0 + np.abs(fast) + np.abs(slow)
    bounded = np.concatenate([drift / denom, bend / denom], axis=-1)
    interaction = np.tanh(bounded[..., :4]) * np.tanh(current[..., :4])
    return np.concatenate([current, state, length, bounded, interaction], axis=-1)


def fit_stats(features: np.ndarray, target_coeff: np.ndarray) -> dict[str, np.ndarray]:
    """Channel-wise standardized ridge sufficient statistics."""
    xm = features.mean(0)
    xs = np.maximum(features.std(0), 1e-5)
    ym = target_coeff.mean(0)
    z = (features - xm) / xs
    v = target_coeff - ym
    n = len(features)
    gram = np.einsum("ncf,ncg->cfg", z, z, optimize=True) / n
    cross = np.einsum("ncf,nck->cfk", z, v, optimize=True) / n
    return {"xmean": xm, "xscale": xs, "ymean": ym, "gram": gram, "cross": cross}


def solve(stats: dict[str, np.ndarray], ridge: float, rank: int) -> dict[str, np.ndarray]:
    weights = []
    for gram, cross in zip(stats["gram"], stats["cross"][:, :, :rank]):
        eig, vec = eigh(gram, check_finite=False)
        weights.append(vec @ ((vec.T @ cross) / (np.maximum(eig, 0)[:, None] + ridge)))
    return {"xmean": stats["xmean"], "xscale": stats["xscale"],
            "ymean": stats["ymean"][:, :rank], "weights": np.stack(weights),
            "ridge": np.array(ridge), "rank": np.array(rank)}


def correction(model: dict[str, np.ndarray], features: np.ndarray, horizon: int) -> np.ndarray:
    z = (features - model["xmean"]) / model["xscale"]
    coeff = np.einsum("ncf,cfk->nck", z, model["weights"], optimize=True) + model["ymean"]
    spectrum = np.zeros((len(features), horizon, features.shape[1]), dtype=np.float64)
    spectrum[:, :coeff.shape[-1], :] = coeff.transpose(0, 2, 1)
    return idct(spectrum, axis=1, norm="ortho")


def empirical_prior(train_error: np.ndarray, modes: int = 64) -> dict[str, np.ndarray]:
    scale = np.sqrt(np.mean(train_error * train_error, axis=(0, 1)) + 1e-8)
    normalized = train_error / scale
    modes = min(modes, train_error.shape[1])
    coeff = dct(normalized, axis=1, norm="ortho")[:, :modes, :]
    coeff = coeff.transpose(0, 2, 1).reshape(-1, modes)
    covariance = coeff.T @ coeff / len(coeff)
    basis = idct(np.eye(train_error.shape[1])[:modes], axis=1, norm="ortho").T
    white = max(float(np.mean(normalized * normalized) - np.trace(covariance) / train_error.shape[1]), 1e-6)
    return {"scale": scale, "covariance": covariance, "basis": basis, "white": np.array(white)}


def empirical_gain(prior: dict[str, np.ndarray], prefix: int, noise: float) -> np.ndarray:
    kernel = prior["basis"] @ prior["covariance"] @ prior["basis"].T
    observed = kernel[:prefix, :prefix] + np.eye(prefix) * float(prior["white"]) * (1.0 + noise)
    return cho_solve(
        cho_factor(observed, lower=True, check_finite=False),
        kernel[prefix:, :prefix].T,
        check_finite=False,
    ).T


def local_correction(prediction, target, prefix, gain, scale):
    raw = (np.asarray(target[:, :prefix], np.float64) - prediction[:, :prefix]) / scale
    suffix = np.einsum("ua,nac->nuc", gain, raw, optimize=True) * scale
    out = np.zeros_like(prediction, dtype=np.float64)
    out[:, prefix:] = suffix
    return out
