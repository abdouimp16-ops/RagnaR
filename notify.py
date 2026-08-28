import requests
import config

API = f"https://api.telegram.org/bot{config.TELEGRAM_BOT_TOKEN}"


def send(text: str, chat_id: str | None = None):
    r = requests.post(f"{API}/sendMessage", json={
        "chat_id": chat_id or config.TELEGRAM_CHAT_ID,
        "text": text,
        "parse_mode": "HTML",
        "disable_web_page_preview": True,
    }, timeout=20)
    if not r.ok:
        print("Telegram error:", r.text)
    return r.ok


def send_admin(text: str):
    if config.TELEGRAM_ADMIN_ID:
        return send(text, config.TELEGRAM_ADMIN_ID)
    return False


def fmt(x: float) -> str:
    if x >= 100:
        return f"{x:,.2f}"
    if x >= 1:
        return f"{x:,.4f}"
    return f"{x:.6f}"


def format_signal(s: dict) -> str:
    arrow = "🟢 شراء LONG" if s["side"] == "LONG" else "🔴 بيع SHORT"
    reasons = "\n".join(f" ✓ {r}" for r in s.get("reasons", []))

    return (
        f"<b>⚡ صفقة اليوم — {s['symbol']}</b>\n"
        f"{arrow} | فريم 4H\n"
        f"────────────────────\n"
        f"🎯 <b>الدخول:</b> {fmt(s['entry'])}\n"
        f"🛑 <b>وقف الخسارة:</b> {fmt(s['sl'])}\n"
        f"🏁 <b>هدف 1:</b> {fmt(s['tp'][0])} (اخرج 40%)\n"
        f"🏁 <b>هدف 2:</b> {fmt(s['tp'][1])} (اخرج 40%)\n"
        f"🏁 <b>هدف 3:</b> {fmt(s['tp'][2])} (اترك 20%)\n"
        f"────────────────────\n"
        f"📊 الجودة: <b>{s['score']:.1f}/100</b> | R:R = <b>1:{s['rr']}</b>\n"
        f"🎯 الاحتمال: <b>{s['prob']:.2f}</b> | الفئة: <b>{s['conviction']}</b>\n"
        f"💰 حجم المركز: {s['size']:.4f} (مخاطرة {s['risk_cash']}$)\n"
        f"────────────────────\n"
        f"<b>الأسباب:</b>\n{reasons}\n\n"
        f"🔒 حرّك الوقف للتعادل بعد الهدف 1.\n"
        f"<i>ليست نصيحة مالية.</i>"
    )


def format_no_trade(top5: list) -> str:
    rows = "\n".join(
        f"{i+1}. {r['symbol']} — {r['score']:.1f}/100 ({r['side']})"
        for i, r in enumerate(top5)
    ) or "لا مرشحين"

    return (
        "<b>🕓 تقرير اليوم: لا صفقة</b>\n"
        "لم تتحقق شروط الجودة الكاملة، والانتظار قرار رابح.\n\n"
        f"<b>أقرب المرشحين:</b>\n{rows}"
    )


def format_drift_alert(result: dict) -> str:
    return (
        "🚨 <b>انحراف بيانات مكتشف</b>\n"
        f"الحد الأقصى PSI: <b>{result['max_psi']}</b>\n"
        f"الإجراء: <b>{result['action']}</b>\n\n"
        f"التفاصيل:\n{result['per_feature']}"
    )
def format_health_report(checks: dict) -> str:
    rows = "\n".join(
        f" {'✅' if v else '❌'} {k}"
        for k, v in checks.items()
    )
    return (
        "<b>🏥 فحص الصحة</b>\n"
        f"────────────────────\n{rows}"
    )
