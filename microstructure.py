import ccxt
import numpy as np
import pandas as pd


_exchange = getattr(ccxt, "binance")({"enableRateLimit": True})


def fetch_orderbook(symbol: str, depth_pct: float = 0.002):
    ob = _exchange.fetch_order_book(symbol)
    best_bid = ob["bids"][0][0]
    best_ask = ob["asks"][0][0]
    mid = (best_bid + best_ask) / 2
    lo = mid * (1 - depth_pct)
    hi = mid * (1 + depth_pct)

    bid_vol = sum(v for p, v in ob["bids"] if p >= lo)
    ask_vol = sum(v for p, v in ob["asks"] if p <= hi)

    spread_bps = (best_ask - best_bid) / mid * 10000

    return {
        "mid": mid,
        "spread_bps": spread_bps,
        "bid_vol": bid_vol,
        "ask_vol": ask_vol,
        "near_imbalance": (bid_vol - ask_vol) / (bid_vol + ask_vol) if (bid_vol + ask_vol) > 0 else 0,
    }


def fetch_funding(symbol: str):
    funding = _exchange.fetch_funding_rate(symbol)
    info = funding.get("info", {})
    next_rate = float(info.get("lastFundingRate", 0) or 0)
    return {
        "funding_rate": funding.get("fundingRate", 0) or 0,
        "next_rate": next_rate,
    }


def fetch_open_interest(symbol: str):
    try:
        oi = _exchange.fetch_open_interest(symbol)
        return oi.get("openInterestAmount", 0) or 0
    except Exception:
        return None


def fetch_long_short(symbol: str):
    try:
        data = _exchange.fapiPublicGetGlobalLongShortAccountRatio({
            "symbol": symbol.replace("/USDT", "USDT"),
            "period": "5m",
        })
        return float(data[0]["longShortRatio"])
    except Exception:
        return None


def fetch_taker_flow(symbol: str):
    try:
        trades = _exchange.fetch_trades(symbol, limit=200)
        df = pd.DataFrame(trades, columns=["price", "amount", "side"])
        df["signed"] = np.where(df["side"] == "buy", df["amount"], -df["amount"])
        cvd = df["signed"].cumsum().iloc[-1]
        return float(cvd)
    except Exception:
        return None


def fetch_basis(symbol: str):
    try:
        spot = _exchange.fetch_ticker(symbol)["last"]
        futures_symbol = symbol.replace("/USDT", "/USDT:USDT")
        futures = _exchange.fetch_ticker(futures_symbol)["last"]
        return (futures - spot) / spot * 10000
    except Exception:
        return None


def collect_micro(symbol: str) -> dict:
    out = {"symbol": symbol}
    try:
        out.update(fetch_orderbook(symbol))
    except Exception:
        pass
    try:
        out.update(fetch_funding(symbol))
    except Exception:
        pass
    try:
        oi = fetch_open_interest(symbol)
        if oi:
            out["open_interest"] = oi
    except Exception:
        pass
    try:
        ls = fetch_long_short(symbol)
        if ls:
            out["long_short"] = ls
    except Exception:
        pass
    try:
        flow = fetch_taker_flow(symbol)
        if flow:
            out["cvd"] = flow
    except Exception:
        pass
    try:
        basis = fetch_basis(symbol)
        if basis:
            out["basis_bps"] = basis
    except Exception:
        pass
    return out
