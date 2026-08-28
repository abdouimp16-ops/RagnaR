import numpy as np
import pandas as pd


def detect_setup(df: pd.DataFrame, micro: dict) -> str | None:
    """
    يفحص الإعدادات الخارقة الخمسة:
    1. ضغط بيعي (شراء)
    2. تصريف اللونجات (بيع)
    3. انفجار انضغاط التقلب
    4. تحوّل نظام + أول ارتداد (شراء)
    5. انحراف الكبار عن الجمهور
    """
    c = df.iloc[-1]
    p = df.iloc[-2]

    # 1. ضغط بيعي
    if (micro.get("funding_rate", 0) < -0.0001 and
        c["close"] > c["ema20"] and
        micro.get("open_interest", 0) > 0):
        return "SELL_PRESSURE_LONG"

    # 2. تصريف اللونجات
    if (micro.get("funding_rate", 0) > 0.0005 and
        c["close"] < c["ema20"] and
        micro.get("cvd", 0) < 0):
        return "LONG_DISTRIBUTION_SHORT"

    # 3. انفجار انضغاط التقلب
    bb_width = (c["upper_bb"] - c["lower_bb"]) / c["mid_bb"]
    prev_bb_width = (p["upper_bb"] - p["lower_bb"]) / p["mid_bb"]
    if prev_bb_width < 0.03 and bb_width > prev_bb_width * 1.5:
        if c["close"] > c["ema20"]:
            return "VOL_BREAKOUT_LONG"
        else:
            return "VOL_BREAKOUT_SHORT"

    # 4. تحوّل نظام + أول ارتداد
    if (p["close"] < p["ema200"] and c["close"] > c["ema200"] and
        c["rsi"] < 60 and c["close"] > c["ema20"]):
        return "REGIME_SHIFT_LONG"

    # 5. انحراف الكبار عن الجمهور
    if micro.get("long_short", 0) > 1.2 and c["close"] > c["ema50"]:
        return "WHALE_DIVERGENCE_LONG"
    if micro.get("long_short", 0) < 0.8 and c["close"] < c["ema50"]:
        return "WHALE_DIVERGENCE_SHORT"

    return None


SUPER_SETUPS = {
    "SELL_PRESSURE_LONG": "LONG",
    "LONG_DISTRIBUTION_SHORT": "SHORT",
    "VOL_BREAKOUT_LONG": "LONG",
    "VOL_BREAKOUT_SHORT": "SHORT",
    "REGIME_SHIFT_LONG": "LONG",
    "WHALE_DIVERGENCE_LONG": "LONG",
    "WHALE_DIVERGENCE_SHORT": "SHORT",
}


def is_super_setup(setup_name: str) -> bool:
    return setup_name in SUPER_SETUPS


def get_setup_direction(setup_name: str) -> str | None:
    return SUPER_SETUPS.get(setup_name)
