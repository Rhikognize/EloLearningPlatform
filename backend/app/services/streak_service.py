from __future__ import annotations
from datetime import date, timedelta, datetime
from zoneinfo import ZoneInfo
import logging
from app.models.user import User

DEFAULT_TZ = "Europe/Chisinau"


def get_user_today(timezone_str: str | None) -> date:
    try:
        tz_name = timezone_str if timezone_str else DEFAULT_TZ
        return datetime.now(ZoneInfo(tz_name)).date()
    except Exception as e:
        logging.error(f"Timezone error: {e}")
        return datetime.now().date()


def update_streak(user: User) -> None:
    today = get_user_today(user.timezone)
    last = user.last_activity_date
    if last is None or last < today - timedelta(days=1):
        user.current_streak = 1
    elif last == today - timedelta(days=1):
        user.current_streak += 1
    else:
        return
    if user.current_streak > user.max_streak:
        user.max_streak = user.current_streak

    user.last_activity_date = today
