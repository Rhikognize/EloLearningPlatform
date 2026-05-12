from __future__ import annotations
from datetime import date, timedelta
from zoneinfo import ZoneInfo
from datetime import datetime
from app.models.user import User


def get_user_today(timezone: str) -> date:
    try:
        return datetime.now(ZoneInfo(timezone)).date()
    except Exception:
        return datetime.now(ZoneInfo("Europe/Bucharest")).date()


def update_streak(user: User) -> None:
    today = get_user_today(user.timezone)
    last = user.last_activity_date

    if last is None:
        user.current_streak = 1
    elif last == today:
        return
    elif last == today - timedelta(days=1):
        user.current_streak += 1
    else:
        user.current_streak = 1

    if user.current_streak > user.max_streak:
        user.max_streak = user.current_streak

    user.last_activity_date = today
