import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import config
from data import fetch_ohlcv
from indicators import enrich
from execution import chandelier_stop, check_time_exit
from notify import send


def run():
    # Placeholder: in production this reads open trades from DB
    # and manages exits (partial, breakeven, chandelier, time exit)

    open_trades = []  # TODO: load from store

    if not open_trades:
        return

    for trade in open_trades:
        try:
            df = enrich(fetch_ohlcv(trade["symbol"], config.TIMEFRAME, config.CANDLES))
            c = df.iloc[-1]

            # Breakeven after TP1
            if trade["side"] == "LONG":
                if c["high"] >= trade["tp1"]:
                    trade["sl"] = trade["entry"]
                chand = chandelier_stop(df, "LONG")
                if c["close"] < max(trade["sl"], chand):
                    close_trade(trade, "chandelier")
            else:
                if c["low"] <= trade["tp1"]:
                    trade["sl"] = trade["entry"]
                chand = chandelier_stop(df, "SHORT")
                if c["close"] > min(trade["sl"], chand):
                    close_trade(trade, "chandelier")

            if check_time_exit(trade.get("bars_held", 0)):
                close_trade(trade, "time_exit")

        except Exception as e:
            print(f"[monitor][skip] {trade['symbol']}: {e}")


def close_trade(trade: dict, reason: str):
    print(f"[close] {trade['symbol']} @ {reason}")
    # TODO: update DB, send notification
    send(f"🔒 <b>إغلاق صفقة</b>\n{trade['symbol']} | السبب: {reason}")


if __name__ == "__main__":
    run()
