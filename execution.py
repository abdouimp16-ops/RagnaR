import numpy as np


def build_order_plan(entry: float, atr: float, side: str,
                     maker_offset_bps: float = 8,
                     timeout_min: int = 45) -> dict:
    if side == "LONG":
        limit_price = entry * (1 + maker_offset_bps / 10000)
        sl = entry - 1.6 * atr
        tps = [entry + m * atr for m in (1.6, 3.2, 5.0)]
        super_tps = [entry + m * atr for m in (4.0, 6.0, 8.0)]
    else:
        limit_price = entry * (1 - maker_offset_bps / 10000)
        sl = entry + 1.6 * atr
        tps = [entry - m * atr for m in (1.6, 3.2, 5.0)]
        super_tps = [entry - m * atr for m in (4.0, 6.0, 8.0)]

    return {
        "limit_price": round(limit_price, 8),
        "sl": round(sl, 8),
        "tps": [round(x, 8) for x in tps],
        "super_tps": [round(x, 8) for x in super_tps],
        "timeout_min": timeout_min,
    }


def should_cancel_order(current_price: float, entry: float, spread_bps: float,
                        book_imbalance: float, side: str) -> bool:
    drift = abs(current_price - entry) / entry * 10000
    if drift > 25:
        return True
    if spread_bps > 15:
        return True
    if side == "LONG" and book_imbalance < -0.2:
        return True
    if side == "SHORT" and book_imbalance > 0.2:
        return True
    return False


def split_order_by_liquidity(size: float, book_vol: float, max_pct: float = 0.08) -> list:
    if book_vol <= 0:
        return [size]
    max_single = book_vol * max_pct
    if size <= max_single:
        return [size]
    parts = []
    remaining = size
    while remaining > 0:
        part = min(remaining, max_single)
        parts.append(part)
        remaining -= part
    return parts


def audit_slippage(planned: float, actual: float) -> dict:
    diff_bps = abs(actual - planned) / planned * 10000
    return {
        "planned": planned,
        "actual": actual,
        "slippage_bps": round(diff_bps, 2),
        "acceptable": diff_bps < 5,
    }


def chandelier_stop(df, side: str, mult: float = 2.6) -> float:
    highest = df["high"].rolling(22).max().iloc[-1]
    lowest = df["low"].rolling(22).min().iloc[-1]
    atr = df["atr"].iloc[-1]
    if side == "LONG":
        return highest - mult * atr
    return lowest + mult * atr


def check_time_exit(bars_held: int, max_bars: int = 60) -> bool:
    return bars_held >= max_bars
