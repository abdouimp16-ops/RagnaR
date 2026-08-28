import json
from datetime import datetime, timezone


def format_weekly_report(stats: dict) -> str:
    trades = stats.get("trades", [])
    total = len(trades)
    wins = sum(1 for t in trades if t.get("pnl_r", 0) > 0)
    losses = sum(1 for t in trades if t.get("pnl_r", 0) <= 0)
    total_r = sum(t.get("pnl_r", 0) for t in trades)
    wr = (wins / total * 100) if total > 0 else 0

    return (
        "<b>📊 التقرير الأسبوعي</b>\n"
        f"────────────────────\n"
        f"الصفقات: <b>{total}</b>\n"
        f"رابحة: <b>{wins}</b> | خاسرة: <b>{losses}</b>\n"
        f"نسبة النجاح: <b>{wr:.1f}%</b>\n"
        f"صافي R: <b>{total_r:+.2f}R</b>\n"
        f"────────────────────\n"
        f"🟢 الحالة: {'مستمر ✅' if total_r > -2 else 'مراجعة ⚠️'}"
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


def format_trade_result(trade: dict) -> str:
    emoji = "✅" if trade.get("pnl_r", 0) > 0 else "❌"
    return (
        f"{emoji} <b>{trade['symbol']}</b> | {trade['side']}\n"
        f"الدخول: {trade['entry']} | الوقف: {trade['sl']}\n"
        f"النتيجة: {trade.get('pnl_r', 0):+.2f}R\n"
        f"السبب: {trade.get('exit_reason', '')}"
    )


def format_daily_summary(signals: list) -> str:
    if not signals:
        return "<b>📋 لا إشارات اليوم</b>"
    rows = "\n".join(
        f"{i+1}. {s['symbol']} — {s['side']} — {s['prob']:.2f}"
        for i, s in enumerate(signals)
    )
    return f"<b>📋 إشارات اليوم:</b>\n{rows}"
