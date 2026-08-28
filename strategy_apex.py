import numpy as np
import pandas as pd
from quant import enrich
from regimes import RegimeClassifier
from setups import detect_setup, is_super_setup, get_setup_direction


RULE_WEIGHTS = {
    "trend_ema200": 14,
    "trend_ema50": 10,
    "macd_momentum": 13,
    "rsi_zone": 11,
    "adx_strength": 12,
    "volume_surge": 10,
    "swing_breakout": 10,
    "funding_ok": 10,
    "book_imbalance": 10,
}


def compute_rule_score(df: pd.DataFrame, micro: dict, direction: str) -> float:
    c = df.iloc[-1]
    p = df.iloc[-2]
    score = 0.0

    if direction == "LONG":
        if c["close"] > c["ema200"]:
            score += RULE_WEIGHTS["trend_ema200"]
        if c["close"] > c["ema50"]:
            score += RULE_WEIGHTS["trend_ema50"]
        if c["macd"] > c["macd_sig"] and c["macd_hist"] > p["macd_hist"]:
            score += RULE_WEIGHTS["macd_momentum"]
        if 45 <= c["rsi"] <= 68:
            score += RULE_WEIGHTS["rsi_zone"]
        if c["close"] >= p["swing_high"] * 0.995:
            score += RULE_WEIGHTS["swing_breakout"]
        if micro.get("funding_rate", 0) < 0.0005:
            score += RULE_WEIGHTS["funding_ok"]
        if micro.get("near_imbalance", 0) > 0.05:
            score += RULE_WEIGHTS["book_imbalance"]
    else:
        if c["close"] < c["ema200"]:
            score += RULE_WEIGHTS["trend_ema200"]
        if c["close"] < c["ema50"]:
            score += RULE_WEIGHTS["trend_ema50"]
        if c["macd"] < c["macd_sig"] and c["macd_hist"] < p["macd_hist"]:
            score += RULE_WEIGHTS["macd_momentum"]
        if 32 <= c["rsi"] <= 55:
            score += RULE_WEIGHTS["rsi_zone"]
        if c["close"] <= p["swing_low"] * 1.005:
            score += RULE_WEIGHTS["swing_breakout"]
        if micro.get("funding_rate", 0) > -0.0005:
            score += RULE_WEIGHTS["funding_ok"]
        if micro.get("near_imbalance", 0) < -0.05:
            score += RULE_WEIGHTS["book_imbalance"]

    if c["adx"] > 22:
        score += RULE_WEIGHTS["adx_strength"]
    if c["volume"] > c["vol_ma20"]:
        score += RULE_WEIGHTS["volume_surge"]

    return score


def build_features(df: pd.DataFrame, micro: dict, direction: str) -> np.ndarray:
    c = df.iloc[-1]
    p = df.iloc[-2]

    feats = [
        (c["close"] - c["ema200"]) / c["close"],
        (c["close"] - c["ema50"]) / c["close"],
        (c["close"] - c["ema20"]) / c["close"],
        c["rsi"] / 100,
        c["adx"] / 100,
        c["macd_hist"] / c["close"],
        c["vol_ratio"],
        c["vol_ret_z"],
        c["atr"] / c["close"],
        micro.get("spread_bps", 0) / 100,
        micro.get("near_imbalance", 0),
        micro.get("funding_rate", 0) * 10000,
        micro.get("basis_bps", 0) / 100,
        micro.get("long_short", 1),
        micro.get("cvd", 0) / (c["volume"] + 1e-12),
        (c["close"] - p["swing_high"]) / (c["atr"] + 1e-12),
        (c["close"] - p["swing_low"]) / (c["atr"] + 1e-12),
    ]
    return np.asarray(feats, dtype=float)


def classify_conviction(prob: float) -> str:
    if prob >= 0.72:
        return "A+"
    elif prob >= 0.62:
        return "A"
    else:
        return "B"


def rank_candidates(candidates: list) -> list:
    if not candidates:
        return []
    sorted_cands = sorted(candidates, key=lambda x: x["prob"], reverse=True)
    top_n = max(1, int(len(sorted_cands) * 0.25))
    return sorted_cands[:top_n]
