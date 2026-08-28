import time
import requests
import config
import telegram_bot as tg
from strategy import best_setup
from risk import build_trade


def poll():
    offset = None
    while True:
        try:
            r = requests.get(f"{tg.API}/getUpdates", params={"timeout": 50, "offset": offset}, timeout=60).json()
            for u in r.get("result", []):
                offset = u["update_id"] + 1
                msg = u.get("message", {})
                text = (msg.get("text") or "").strip().lower()
                chat = str(msg.get("chat", {}).get("id"))

                if text.startswith("/signal"):
                    setup, top5 = best_setup()
                    trade = build_trade(setup) if setup else None
                    if trade:
                        tg.send(tg.format_signal(trade), chat)
                    else:
                        tg.send(tg.format_no_trade(top5), chat)

                elif text.startswith("/status"):
                    tg.send("✅ البوت يعمل.\nالإشارة اليومية الساعة "
                            f"{config.SIGNAL_HOUR_UTC}:00 UTC", chat)

                elif text.startswith("/start"):
                    tg.send("مرحباً 👋\nأوامر البوت:\n"
                            "/signal — فحص فوري\n"
                            "/status — حالة البوت", chat)

                elif text.startswith("/help"):
                    tg.send("الأوامر المتاحة:\n"
                            "/signal — إشارة فورية\n"
                            "/status — حالة البوت\n"
                            "/start — ترحيب", chat)

        except Exception as e:
            print("poll error:", e)
            time.sleep(5)


if __name__ == "__main__":
    poll()
