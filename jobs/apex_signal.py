import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import config
from data import fetch_ohlcv
from quant import enrich
from microstructure import collect_micro
from strategy_apex import compute_rule_score, build_features, classify_conviction, rank_candidates
from ensemble import CalibratedEnsemble
from risk import build_trade
from notify import send, format_signal, format_no_trade
from store import insert_signal
import numpy as np
import time


def run(ensemble: CalibratedEnsemble | None = None, regime_clf=None):
    candidates = []

    for symbol in config.SYMBOLS:
        try:
            df = enrich(fetch_ohlcv(symbol, config.TIMEFRAME, config.CANDLES))
            if len(df) < 210:
                continue

            c = df.iloc[-1]
            p = df.iloc[-2]

            # اتجاه
            direction = None
            if c["close"] > c["ema200"] and c["close"] > c["ema50"]:
                direction = "LONG"
            elif c["close"] < c["ema200"] and c["close"] < c["ema50"]:
                direction = "SHORT"

            if not direction:
                continue

            micro = collect_micro(symbol)
            score = compute_rule_score(df, micro, direction)

            if score < 62:
                continue

            features = build_features(df, micro, direction)

            prob = 0.5
            if ensemble is not None:
                try:
                    prob = float(ensemble.predict_proba(features.reshape(1, -1))[0])
                except Exception:
                    prob = 0.5

            if prob < config.MIN_PROB:
                continue

            conviction = classify_conviction(prob)

            candidates.append({
                "symbol": symbol,
                "side": direction,
                "score": score,
                "prob": prob,
                "conviction": conviction,
                "features": features,
                "df": df,
                "micro": micro,
            })

            print(f"[candidate] {symbol} {direction} score={score:.1f} prob={prob:.2f} {conviction}")

        except Exception as e:
            print(f"[skip] {symbol}: {e}")

        time.sleep(0.5)

    if not candidates:
        send(format_no_trade([]))
        return None

    # الترتيب المقطعي
    ranked = rank_candidates(candidates)
    if not ranked:
        send(format_no_trade(candidates[:5]))
        return None

    best = ranked[0]

    # التوقع بعد الكلفة
    rr = 3.2
    cost_r = 0.026
    expectancy = best["prob"] * rr - (1 - best["prob"]) * 1 - cost_r
    if expectancy < config.MIN_EXPECTANCY_R:
        send(format_no_trade(candidates[:5]))
        return None

    trade = build_trade({
        "symbol": best["symbol"],
        "side": best["side"],
        "price": float(best["df"].iloc[-1]["close"]),
        "atr": float(best["df"].iloc[-1]["atr"]),
        "score": best["score"],
        "prob": best["prob"],
        "conviction": best["conviction"],
    })

    if trade:
        send(format_signal(trade))
        insert_signal({
            "ts": int(time.time() * 1000),
            "symbol": trade["symbol"],
            "side": trade["side"],
            "entry": trade["entry"],
            "sl": trade["sl"],
            "score": trade["score"],
            "prob": trade["prob"],
            "conviction": trade["conviction"],
            "reasons": [],
        })
        return trade

    send(format_no_trade(candidates[:5]))
    return None


if __name__ == "__main__":
    run()
