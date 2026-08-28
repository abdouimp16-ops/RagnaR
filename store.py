import json
import os
import sqlite3
import config


def get_conn():
    os.makedirs(config.DATA_DIR, exist_ok=True)
    conn = sqlite3.connect(config.DB_PATH)
    return conn


def init_db():
    conn = get_conn()
    c = conn.cursor()

    c.execute("""
    CREATE TABLE IF NOT EXISTS candles (
        symbol TEXT, timeframe TEXT, ts INTEGER,
        open REAL, high REAL, low REAL, close REAL, volume REAL,
        PRIMARY KEY (symbol, timeframe, ts)
    )
    """)

    c.execute("""
    CREATE TABLE IF NOT EXISTS micro (
        symbol TEXT, ts INTEGER,
        mid REAL, spread_bps REAL, bid_vol REAL, ask_vol REAL,
        near_imbalance REAL, funding_rate REAL, open_interest REAL,
        long_short REAL, cvd REAL, basis_bps REAL,
        PRIMARY KEY (symbol, ts)
    )
    """)

    c.execute("""
    CREATE TABLE IF NOT EXISTS labels (
        symbol TEXT, ts INTEGER, horizon INTEGER,
        label INTEGER, return_r REAL,
        PRIMARY KEY (symbol, ts, horizon)
    )
    """)

    c.execute("""
    CREATE TABLE IF NOT EXISTS trades (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        ts INTEGER, symbol TEXT, side TEXT, entry REAL, sl REAL,
        tp1 REAL, tp2 REAL, tp3 REAL, size REAL, risk_pct REAL,
        conviction TEXT, model_hash TEXT, status TEXT
    )
    """)

    c.execute("""
    CREATE TABLE IF NOT EXISTS model_registry (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        ts INTEGER, name TEXT, hash TEXT, auc REAL, pbo REAL,
        deflated_sharpe REAL, status TEXT
    )
    """)

    c.execute("""
    CREATE TABLE IF NOT EXISTS drift_checks (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        ts INTEGER, max_psi REAL, action TEXT, details TEXT
    )
    """)

    c.execute("""
    CREATE TABLE IF NOT EXISTS signals (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        ts INTEGER, symbol TEXT, side TEXT, entry REAL, sl REAL,
        score REAL, prob REAL, conviction TEXT, reasons TEXT
    )
    """)

    conn.commit()
    conn.close()


def insert_candles(df, symbol: str, timeframe: str):
    conn = get_conn()
    df.to_sql("candles", conn, if_exists="append", index=False)
    conn.commit()
    conn.close()


def insert_micro(micro: dict, ts: int):
    conn = get_conn()
    c = conn.cursor()
    c.execute("""
    INSERT OR REPLACE INTO micro
    (symbol, ts, mid, spread_bps, bid_vol, ask_vol, near_imbalance,
     funding_rate, open_interest, long_short, cvd, basis_bps)
    VALUES (?,?,?,?,?,?,?,?,?,?,?,?)
    """, (
        micro.get("symbol"),
        ts,
        micro.get("mid", 0),
        micro.get("spread_bps", 0),
        micro.get("bid_vol", 0),
        micro.get("ask_vol", 0),
        micro.get("near_imbalance", 0),
        micro.get("funding_rate", 0),
        micro.get("open_interest", 0),
        micro.get("long_short", 0),
        micro.get("cvd", 0),
        micro.get("basis_bps", 0),
    ))
    conn.commit()
    conn.close()


def insert_label(symbol: str, ts: int, horizon: int, label: int, ret_r: float):
    conn = get_conn()
    c = conn.cursor()
    c.execute("""
    INSERT OR REPLACE INTO labels (symbol, ts, horizon, label, return_r)
    VALUES (?,?,?,?,?)
    """, (symbol, ts, horizon, label, ret_r))
    conn.commit()
    conn.close()


def insert_signal(signal: dict):
    conn = get_conn()
    c = conn.cursor()
    c.execute("""
    INSERT INTO signals (ts, symbol, side, entry, sl, score, prob, conviction, reasons)
    VALUES (?,?,?,?,?,?,?,?,?)
    """, (
        signal["ts"], signal["symbol"], signal["side"],
        signal["entry"], signal["sl"], signal["score"],
        signal["prob"], signal["conviction"],
        json.dumps(signal.get("reasons", []), ensure_ascii=False),
    ))
    conn.commit()
    conn.close()
