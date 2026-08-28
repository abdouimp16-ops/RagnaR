import numpy as np
import pandas as pd


def ema(s: pd.Series, n: int) -> pd.Series:
    return s.ewm(span=n, adjust=False).mean()


def rsi(s: pd.Series, n: int = 14) -> pd.Series:
    d = s.diff()
    gain = d.clip(lower=0).ewm(alpha=1 / n, adjust=False).mean()
    loss = (-d.clip(upper=0)).ewm(alpha=1 / n, adjust=False).mean()
    rs = gain / loss.replace(0, np.nan)
    return (100 - 100 / (1 + rs)).fillna(50)


def macd(s: pd.Series, fast=12, slow=26, signal=9):
    line = ema(s, fast) - ema(s, slow)
    sig = ema(line, signal)
    return line, sig, line - sig


def atr(df: pd.DataFrame, n: int = 14) -> pd.Series:
    pc = df["close"].shift(1)
    tr = pd.concat([
        df["high"] - df["low"],
        (df["high"] - pc).abs(),
        (df["low"] - pc).abs(),
    ], axis=1).max(axis=1)
    return tr.ewm(alpha=1 / n, adjust=False).mean()


def adx(df: pd.DataFrame, n: int = 14) -> pd.Series:
    up = df["high"].diff()
    dn = -df["low"].diff()
    plus = np.where((up > dn) & (up > 0), up, 0.0)
    minus = np.where((dn > up) & (dn > 0), dn, 0.0)
    a = atr(df, n).replace(0, np.nan)
    pdi = 100 * pd.Series(plus, index=df.index).ewm(alpha=1 / n, adjust=False).mean() / a
    mdi = 100 * pd.Series(minus, index=df.index).ewm(alpha=1 / n, adjust=False).mean() / a
    dx = ((pdi - mdi).abs() / (pdi + mdi).replace(0, np.nan)) * 100
    return dx.ewm(alpha=1 / n, adjust=False).mean().fillna(0)


def rolling_zscore(s: pd.Series, n: int = 100) -> pd.Series:
    m = s.rolling(n).mean()
    std = s.rolling(n).std()
    return (s - m) / std.replace(0, np.nan)


def true_range(df: pd.DataFrame) -> pd.Series:
    pc = df["close"].shift(1)
    return pd.concat([
        df["high"] - df["low"],
        (df["high"] - pc).abs(),
        (df["low"] - pc).abs(),
    ], axis=1).max(axis=1)


def bollinger(s: pd.Series, n: int = 20, k: float = 2.0):
    m = s.rolling(n).mean()
    sd = s.rolling(n).std()
    return m + k * sd, m, m - k * sd


def cci(df: pd.DataFrame, n: int = 20) -> pd.Series:
    tp = (df["high"] + df["low"] + df["close"]) / 3
    m = tp.rolling(n).mean()
    md = (tp - m).abs().rolling(n).mean()
    return (tp - m) / (0.015 * md.replace(0, np.nan))


def stochastic(df: pd.DataFrame, n: int = 14, d: int = 3):
    low_n = df["low"].rolling(n).min()
    high_n = df["high"].rolling(n).max()
    k = 100 * (df["close"] - low_n) / (high_n - low_n).replace(0, np.nan)
    return k, k.rolling(d).mean()


def obv(df: pd.DataFrame) -> pd.Series:
    sign = np.sign(df["close"].diff()).fillna(0)
    return (sign * df["volume"]).cumsum()


def vwap(df: pd.DataFrame) -> pd.Series:
    tp = (df["high"] + df["low"] + df["close"]) / 3
    return (tp * df["volume"]).cumsum() / df["volume"].cumsum().replace(0, np.nan)


def kama(s: pd.Series, n: int = 10, fast: int = 2, slow: int = 30) -> pd.Series:
    change = (s - s.shift(n)).abs()
    vol = (s - s.shift(1)).abs().rolling(n).sum()
    er = (change / vol.replace(0, np.nan)).fillna(0)
    sc = (er * (2 / (fast + 1) - 2 / (slow + 1)) + 2 / (slow + 1)) ** 2
    out = [s.iloc[0]]
    for i in range(1, len(s)):
        out.append(out[-1] + sc.iloc[i] * (s.iloc[i] - out[-1]))
    return pd.Series(out, index=s.index)


def enrich(df: pd.DataFrame) -> pd.DataFrame:
    df = df.copy()
    df["ema20"] = ema(df["close"], 20)
    df["ema50"] = ema(df["close"], 50)
    df["ema200"] = ema(df["close"], 200)
    df["rsi"] = rsi(df["close"])
    df["macd"], df["macd_sig"], df["macd_hist"] = macd(df["close"])
    df["atr"] = atr(df)
    df["adx"] = adx(df)
    df["tr"] = true_range(df)
    df["upper_bb"], df["mid_bb"], df["lower_bb"] = bollinger(df["close"])
    df["cci"] = cci(df)
    df["stoch_k"], df["stoch_d"] = stochastic(df)
    df["obv"] = obv(df)
    df["vwap"] = vwap(df)
    df["kama"] = kama(df["close"])
    df["vol_ma20"] = df["volume"].rolling(20).mean()
    df["vol_ma50"] = df["volume"].rolling(50).mean()
    df["swing_high"] = df["high"].rolling(20).max()
    df["swing_low"] = df["low"].rolling(20).min()
    df["ret_1"] = df["close"].pct_change(1)
    df["ret_5"] = df["close"].pct_change(5)
    df["ret_20"] = df["close"].pct_change(20)
    df["vol_ret_z"] = rolling_zscore(df["ret_1"], 100)
    df["vol_ratio"] = df["vol_ma20"] / df["vol_ma50"].replace(0, np.nan)
    return df
