from __future__ import annotations
from datetime import datetime, date
from zoneinfo import available_timezones
from pydantic import BaseModel, EmailStr, Field, field_validator


def validate_timezone(value: str) -> str:
    if value not in available_timezones():
        raise ValueError(f"'{value}' nu este un timezone valid")
    return value


class UserCreate(BaseModel):
    username: str = Field(..., min_length=3, max_length=50,
                          pattern=r"^[a-zA-Z0-9_-]+$")
    email: EmailStr
    password: str = Field(..., min_length=8, max_length=128)

    @field_validator("password")
    @classmethod
    def password_strength(cls, value: str) -> str:
        if not any(c.isdigit() for c in value):
            raise ValueError("Parola trebuie să conțină cel puțin o cifră")
        if not any(c.isalpha() for c in value):
            raise ValueError("Parola trebuie să conțină cel puțin o literă")
        return value


class UserUpdate(BaseModel):
    avatar_id: int | None = Field(None, ge=1, le=20)
    daily_goal_target: int | None = None
    timezone: str | None = None

    @field_validator("daily_goal_target")
    @classmethod
    def validate_goal_target(cls, value: int | None) -> int | None:
        if value is not None and value not in (3, 5, 10, 15):
            raise ValueError(
                "daily_goal_target trebuie să fie 3, 5, 10 sau 15")
        return value

    @field_validator("timezone")
    @classmethod
    def validate_tz(cls, value: str | None) -> str | None:
        if value is not None:
            return validate_timezone(value)
        return value


class UserStats(BaseModel):
    total_solved: int
    total_correct: int
    accuracy_percent: float
    favorite_category: str | None


class UserProfile(BaseModel):
    id: int
    username: str
    email: str
    avatar_id: int
    elo_rating: float
    rank: str
    current_streak: int
    max_streak: int
    daily_goal_target: int
    timezone: str
    last_activity_date: date | None
    created_at: datetime
    stats: UserStats

    model_config = {"from_attributes": True}


class HistoryItem(BaseModel):
    id: int
    task_id: int
    task_title: str
    category_name: str
    is_correct: bool
    submitted_answer: str | None
    elo_before: float
    elo_after: float
    elo_delta: float
    time_taken: int | None
    solved_at: datetime

    model_config = {"from_attributes": True}


class HistoryResponse(BaseModel):
    items: list[HistoryItem]
    total: int
    limit: int
    offset: int


class LeaderboardEntry(BaseModel):
    rank: int
    user_id: int
    username: str
    elo_rating: float
    avatar_id: int
    rank_name: str


class LeaderboardResponse(BaseModel):
    top_10: list[LeaderboardEntry]
    current_user: LeaderboardEntry
    neighbors: list[LeaderboardEntry]
