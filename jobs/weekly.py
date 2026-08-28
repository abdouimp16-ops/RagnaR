import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import sqlite3
import config
import pandas as pd
from notify import send
from report import format_weekly_report


def run():
    conn = sqlite3.connect(config.DB_PATH)

    trades = pd.read_sql("""
        SELECT * FROM trades
        WHERE ts > datetime('now', '-7 days')
    """, conn) if os.path.exists(config.DB_PATH) else pd.DataFrame()

    conn.close()

    stats = {
        "trades": trades.to_dict("records") if len(trades) else [],
        "total_r": trades["pnl_r"].sum() if "pnl_r" in trades and len(trades) else 0,
        "wins": len(trades[trades["pnl_r"] > 0]) if "pnl_r" in trades and len(trades) else 0,
    }

    msg = format_weekly_report(stats)
    send(msg)

    # المحكمة الأسبوعية
    total_r = stats["total_r"]
    if total_r <= -8:
        verdict = "إيقاف"
    elif total_r <= -4:
        verdict = "إعادة تدريب"
    else:
        verdict = "استمرار"

    send(f"⚖️ <b>حكم المحكمة الأسبوعية:</b> {verdict}")
    return verdict


if __name__ == "__main__":
    run()
