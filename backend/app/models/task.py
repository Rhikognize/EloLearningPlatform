from datetime import datetime
from typing import Any
from sqlalchemy import Integer, String, Text, Float, Boolean, DateTime, ForeignKey, Enum, JSON, func
from sqlalchemy.orm import Mapped, mapped_column, relationship
import enum
from app.database import Base
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from app.models.user_task_history import UserTaskHistory
    from app.models.category import Category


class DifficultyEnum(str, enum.Enum):
    easy = "easy"
    medium = "medium"
    hard = "hard"
    expert = "expert"


class AnswerTypeEnum(str, enum.Enum):
    exact = "exact"
    numeric = "numeric"
    multiple_choice = "multiple_choice"


# ELO inițial în funcție de dificultate
DIFFICULTY_ELO = {
    DifficultyEnum.easy: 900.0,
    DifficultyEnum.medium: 1200.0,
    DifficultyEnum.hard: 1600.0,
    DifficultyEnum.expert: 2000.0,
}

# Limite ELO pentru sarcini
TASK_ELO_MIN = 800.0
TASK_ELO_MAX = 2500.0


class Task(Base):
    __tablename__ = "tasks"

    id: Mapped[int] = mapped_column(
        Integer, primary_key=True, autoincrement=True)
    category_id: Mapped[int] = mapped_column(
        Integer, ForeignKey("categories.id", ondelete="CASCADE"), nullable=False, index=True
    )
    title: Mapped[str] = mapped_column(String(255), nullable=False)

    # Condiția sarcinii — suportă Markdown + LaTeX ($...$)
    description: Mapped[str] = mapped_column(Text, nullable=False)

    # Tipul răspunsului
    answer_type: Mapped[AnswerTypeEnum] = mapped_column(
        Enum(AnswerTypeEnum), nullable=False, default=AnswerTypeEnum.numeric
    )

    # Răspunsul corect (normalizat)
    correct_answer: Mapped[str] = mapped_column(String(500), nullable=False)

    # Opțiuni pentru multiple_choice: ["A", "B", "C", "D"]
    answer_options: Mapped[Any | None] = mapped_column(JSON, nullable=True)

    # Indicii
    hint: Mapped[str | None] = mapped_column(Text, nullable=True)
    explanation: Mapped[str | None] = mapped_column(Text, nullable=True)

    # Dificultate și ELO
    difficulty: Mapped[DifficultyEnum] = mapped_column(
        Enum(DifficultyEnum), nullable=False, default=DifficultyEnum.medium, index=True
    )
    elo_rating: Mapped[float] = mapped_column(
        Float, default=1200.0, nullable=False)

    # Contor de rezolvări (pentru K-factor provisional vs stable)
    solve_count: Mapped[int] = mapped_column(
        Integer, default=0, nullable=False)

    is_active: Mapped[bool] = mapped_column(
        Boolean, default=True, nullable=False)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), nullable=False
    )

    # Relații
    category: Mapped["Category"] = relationship(
        "Category", back_populates="tasks")
    history: Mapped[list["UserTaskHistory"]] = relationship(
        "UserTaskHistory", back_populates="task"
    )

    def __repr__(self):
        return f"<Task id={self.id} title={self.title!r} elo={self.elo_rating}>"
