import numpy as np
import config
from cv import wilson_lower


def kelly_fraction(p: float, b: float) -> float:
    if b <= 0:
        return 0.0
    return (p * b - (1 - p)) / b


def half_kelly_wilson(wins: int, total: int, avg_rr: float, z: float = 1.96) -> float:
    p = wilson_lower(wins, total, z)
    kelly = kelly_fraction(p, avg_rr)
    return max(0.0, kelly * 0.5)


def vol_adjust(vol_20: float, target_daily: float = 1.2) -> float:
    if vol_20 <= 0:
        return 1.0
    vol_4h = vol_20 * np.sqrt(6)
    return min(2.0, target_daily / vol_4h)


def class_multiplier(conviction: str) -> float:
    return config.MULT_CLASS.get(conviction, 0.5)


def regime_multiplier(regime_mult: float) -> float:
    return np.clip(regime_mult, 0.35, 1.5)


def fear_greed_damper(fg_value: float, direction: str) -> float:
    if direction == "LONG" and fg_value >= 88:
        return 0.7
    if direction == "SHORT" and fg_value <= 10:
        return 0.7
    return 1.0


def calculate_risk_pct(wins: int, total: int, avg_rr: float,
                       conviction: str, regime_mult: float,
                       vol_20: float, fg_value: float,
                       direction: str) -> float:
    base = half_kelly_wilson(wins, total, avg_rr)
    vol_adj = vol_adjust(vol_20)
    cls_mult = class_multiplier(conviction)
    reg_mult = regime_multiplier(regime_mult)
    fg_damp = fear_greed_damper(fg_value, direction)

    risk = base * vol_adj * cls_mult * reg_mult * fg_damp

    risk = min(risk, config.MAX_RISK_PCT)
    risk = max(risk, 0.0)
    return round(risk, 4)


def monte_carlo_sim(returns_r: list, n_paths: int = 4000, n_trades: int = 250, seed: int = 7):
    returns_r = np.asarray(returns_r)
    if len(returns_r) == 0:
        return {"worst_5": 0.0, "max_dd": 0, "median": 0.0}

    rng = np.random.default_rng(seed)
    paths = []
    max_dds = []

    for _ in range(n_paths):
        path = rng.choice(returns_r, size=n_trades, replace=True).cumsum()
        peak = np.maximum.accumulate(path)
        dd = (path - peak).min()
        paths.append(path[-1])
        max_dds.append(dd)

    paths = np.array(paths)
    return {
        "worst_5": round(float(np.percentile(paths, 5)), 3),
        "max_dd": round(float(min(max_dds)), 3),
        "median": round(float(np.median(paths)), 3),
    }


def expected_r(p: float, rr: float, cost_r: float = 0.026) -> float:
    return p * rr - (1 - p) * 1 - cost_r
