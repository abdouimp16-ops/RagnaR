import ccxt
import pandas as pd
import config

_exchange = getattr(ccxt, config.EXCHANGE)({"enableRateLimit": True})


def fetch_ohlcv(symbol: str, timeframe: str, limit: int = config.CANDLES) -> pd.DataFrame:
    raw = _exchange.fetch_ohlcv(symbol, timeframe=timeframe, limit=limit)
    df = pd.DataFrame(raw, columns=["ts", "open", "high", "low", "close", "volume"])
    df["time"] = pd.to_datetime(df["ts"], unit="ms", utc=True)
    return df.drop(columns=["ts"]).reset_index(drop=True)
