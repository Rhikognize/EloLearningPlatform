from __future__ import annotations
from datetime import datetime
from pydantic import BaseModel, Field
from app.models.task import AnswerTypeEnum, DifficultyEnum
from app.models.achievement import Achievement


class TaskOut(BaseModel):
    """
    Ce trimitem clientului pentru o sarcină.
    correct_answer lipsește intenționat — nu îl dezvăluim niciodată în GET.
    """
    id: int
    category_id: int
    category_name: str
    title: str
    description: str
    answer_type: AnswerTypeEnum
    answer_options: list[str] | None
    hint: str | None
    difficulty: DifficultyEnum
    elo_rating: float
    solve_count: int
    created_at: datetime

    model_config = {"from_attributes": True}


class TaskListResponse(BaseModel):
    """Răspuns paginat pentru lista de sarcini."""
    items: list[TaskOut]
    total: int
    page: int
    per_page: int
    total_pages: int


class AchievementOut(BaseModel):
    code: str
    title: str
    icon_name: str

    model_config = {"from_attributes": True}


class DailyGoalProgress(BaseModel):
    correct: int
    target: int
    is_reached: bool


class SolveRequest(BaseModel):
    answer: str = Field(..., min_length=1, max_length=500)
    time_taken: int | None = Field(None, ge=0, le=86400)


class SolveResponse(BaseModel):
    is_correct: bool
    correct_answer: str | None = None
    hint: str | None = None
    explanation: str | None = None
    show_explanation: bool
    elo_before: float
    elo_after: float
    elo_delta: float
    streak: int
    daily_goal_progress: DailyGoalProgress
    achievements_earned: list[AchievementOut]
