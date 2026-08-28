import config
from datetime import datetime, timezone, timedelta


MACRO_EVENTS = [
    "CPI", "FOMC", "NFP", "PPI", "GDP",
    "PMI", "UNEMPLOYMENT", "RETAIL_SALES",
    "ECB", "FED", "POWELL", "INTEREST_RATE",
]


def is_macro_blocked(now: datetime | None = None) -> bool:
    now = now or datetime.now(timezone.utc)

    for event in MACRO_EVENTS:
        # Placeholder: in production this would check a real calendar
        pass

    return False


def get_block_window() -> tuple:
    return (
        config.MACRO_BLOCK_HOURS_BEFORE,
        config.MACRO_BLOCK_HOURS_AFTER,
    )


def is_blocked_window(now: datetime, event_time: datetime) -> bool:
    start = event_time - timedelta(hours=config.MACRO_BLOCK_HOURS_BEFORE)
    end = event_time + timedelta(hours=config.MACRO_BLOCK_HOURS_AFTER)
    return start <= now <= end


def get_next_macro_events() -> list:
    # Placeholder - would fetch from external API in production
    return []
