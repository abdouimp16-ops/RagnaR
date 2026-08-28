import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import config
import sqlite3
from datetime import datetime, timezone
from notify import send, send_admin, format_health_report
from drift import check_psi_drift, load_model_registry
import pandas as pd


def run():
    checks = {}

    # 1. DB exists
    db_ok = os.path.exists(config.DB_PATH)
    checks["قاعدة البيانات"] = db_ok

    # 2. Model exists
    model = load_model_registry("champion")
    checks["النموذج موجود"] = model is not None

    # 3. Data freshness
    try:
        conn = sqlite3.connect(config.DB_PATH)
        df = pd.read_sql("SELECT MAX(ts) as last_ts FROM candles", conn)
        conn.close()
        last_ts = df.iloc[0]["last_ts"]
        age_hours = (int(datetime.now(timezone.utc).timestamp() * 1000) - last_ts) / 3600000
        checks["البيانات حديثة (<24h)"] = age_hours < 24
    except Exception:
        checks["البيانات حديثة (<24h)"] = False

    # 4. Telegram config
    checks["التوكن موجود"] = bool(config.TELEGRAM_BOT_TOKEN)
    checks["معرف القناة موجود"] = bool(config.TELEGRAM_CHAT_ID)

    # 5. Paper mode safety
    checks["وضع الورق مفعل"] = config.PAPER_MODE

    msg = format_health_report(checks)
    send(msg)
    if not all(checks.values()):
        send_admin("⚠️ <b>تنبيه صحة:</b>\n" + msg)


if __name__ == "__main__":
    run()
