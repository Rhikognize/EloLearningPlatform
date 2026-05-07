from datetime import datetime
from sqlalchemy import Integer, Float, Boolean, DateTime, ForeignKey, String, Index, func
from sqlalchemy.orm import Mapped, mapped_column, relationship
from app.database import Base
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from app.models.user import User
    from app.models.task import Task


class UserTaskHistory(Base):
    __tablename__ = "user_task_history"

    id: Mapped[int] = mapped_column(
        Integer, primary_key=True, autoincrement=True)

    user_id: Mapped[int] = mapped_column(
        Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=False
    )
    task_id: Mapped[int] = mapped_column(
        Integer, ForeignKey("tasks.id", ondelete="CASCADE"), nullable=False
    )

    is_correct: Mapped[bool] = mapped_column(Boolean, nullable=False)
    solved_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), nullable=False
    )

    # Timpul de rezolvare în secunde
    time_taken: Mapped[int | None] = mapped_column(Integer, nullable=True)

    # Snapshot ELO — OBLIGATORIU pentru graficul din profil
    elo_before: Mapped[float] = mapped_column(Float, nullable=False)
    elo_after: Mapped[float] = mapped_column(Float, nullable=False)
    elo_delta: Mapped[float] = mapped_column(Float, nullable=False)

    # Ce a introdus utilizatorul
    submitted_answer: Mapped[str | None] = mapped_column(
        String(500), nullable=True)

    # Relații
    user: Mapped["User"] = relationship("User", back_populates="task_history")
    task: Mapped["Task"] = relationship("Task", back_populates="history")

    # Index compus pentru cooldown și calcul penalități (Issue #5)
    __table_args__ = (
        Index("ix_history_user_task_solved",
              "user_id", "task_id", "solved_at"),
    )

    def __repr__(self):
        return f"<History user={self.user_id} task={self.task_id} correct={self.is_correct} delta={self.elo_delta:+.1f}>"
