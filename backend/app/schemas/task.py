from __future__ import annotations
from datetime import datetime
from pydantic import BaseModel
from app.models.task import AnswerTypeEnum, DifficultyEnum


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
