import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import time
import config
from data import fetch_ohlcv
from microstructure import collect_micro
from store import init_db, insert_candles, insert_micro, insert_label
import numpy as np


def run():
    init_db()
    for symbol in config.SYMBOLS:
        try:
            df = fetch_ohlcv(symbol, config.TIMEFRAME, config.CANDLES)
            insert_candles(df, symbol, config.TIMEFRAME)
            print(f"[collect] {symbol} candles: {len(df)}")
        except Exception as e:
            print(f"[collect][skip] {symbol}: {e}")

        try:
            micro = collect_micro(symbol)
            insert_micro(micro, int(time.time() * 1000))
            print(f"[collect] {symbol} micro: ok")
        except Exception as e:
            print(f"[collect][micro][skip] {symbol}: {e}")

        time.sleep(1)


def label_pass():
    from data import fetch_ohlcv
    from indicators import enrich

    init_db()
    for symbol in config.SYMBOLS:
        try:
            df = enrich(fetch_ohlcv(symbol, config.TIMEFRAME, config.CANDLES))
            for i in range(210, len(df) - config.LOOKAHEAD):
                entry = df.iloc[i]["close"]
                atr = df.iloc[i]["atr"]
                if atr <= 0:
                    continue
                sl = entry - 1.6 * atr
                tp = entry + 3.2 * atr
                label = 0
                ret_r = 0.0
                for j in range(i + 1, i + config.LOOKAHEAD):
                    low = df.iloc[j]["low"]
                    high = df.iloc[j]["high"]
                    if low <= sl:
                        label = 0
                        ret_r = -1.0
                        break
                    if high >= tp:
                        label = 1
                        ret_r = 3.2
                        break
                ts = int(df.iloc[i]["time"].timestamp() * 1000)
                insert_label(symbol, ts, config.LOOKAHEAD, label, ret_r)
            print(f"[label] {symbol}: done")
        except Exception as e:
            print(f"[label][skip] {symbol}: {e}")


if __name__ == "__main__":
    run()
