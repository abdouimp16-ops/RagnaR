import hashlib
import json
import os
import numpy as np
import pandas as pd
import config


def psi(expected: np.ndarray, actual: np.ndarray, bins: int = 10) -> float:
    expected = np.asarray(expected, dtype=float)
    actual = np.asarray(actual, dtype=float)

    expected = expected[~np.isnan(expected)]
    actual = actual[~np.isnan(actual)]

    if len(expected) < 10 or len(actual) < 10:
        return 0.0

    lo = min(expected.min(), actual.min())
    hi = max(expected.max(), actual.max())
    if hi - lo < 1e-12:
        return 0.0

    edges = np.linspace(lo, hi, bins + 1)
    e_hist, _ = np.histogram(expected, bins=edges)
    a_hist, _ = np.histogram(actual, bins=edges)

    e_pct = e_hist / max(len(expected), 1)
    a_pct = a_hist / max(len(actual), 1)

    e_pct = np.clip(e_pct, 0.0001, 1)
    a_pct = np.clip(a_pct, 0.0001, 1)

    return float(((a_pct - e_pct) * np.log(a_pct / e_pct)).sum())


def model_sha256(model_bytes: bytes) -> str:
    return hashlib.sha256(model_bytes).hexdigest()


def save_model_registry(model, name: str, features: list, metrics: dict):
    os.makedirs(config.REGISTRY_DIR, exist_ok=True)
    import pickle
    path = os.path.join(config.REGISTRY_DIR, f"{name}.pkl")
    with open(path, "wb") as f:
        pickle.dump({
            "model": model,
            "features": features,
            "metrics": metrics,
            "hash": model_sha256(pickle.dumps(model)),
        }, f)
    return path


def load_model_registry(name: str):
    import pickle
    path = os.path.join(config.REGISTRY_DIR, f"{name}.pkl")
    if not os.path.exists(path):
        return None
    with open(path, "rb") as f:
        return pickle.load(f)


def check_psi_drift(reference: pd.DataFrame, current: pd.DataFrame,
                    features: list, threshold: float = 0.25) -> dict:
    results = {}
    for feat in features:
        if feat in reference.columns and feat in current.columns:
            ps = psi(reference[feat].values, current[feat].values)
            results[feat] = round(ps, 4)

    max_psi = max(results.values()) if results else 0.0
    alert = max_psi > threshold
    warn = max_psi > 0.15

    return {
        "per_feature": results,
        "max_psi": round(max_psi, 4),
        "alert": alert,
        "warning": warn,
        "action": "STOP" if alert else ("WARN" if warn else "OK"),
    }
