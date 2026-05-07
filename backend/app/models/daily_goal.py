from datetime import datetime, date
from sqlalchemy import Integer, Float, Boolean, Date, DateTime, ForeignKey, UniqueConstraint, func
from sqlalchemy.orm import Mapped, mapped_column, relationship
from app.database import Base
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from app.models.user import User


class DailyGoal(Base):
    __tablename__ = "daily_goals"

    id: Mapped[int] = mapped_column(
        Integer, primary_key=True, autoincrement=True)

    user_id: Mapped[int] = mapped_column(
        Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True
    )

    # Data în timezone-ul utilizatorului
    goal_date: Mapped[date] = mapped_column(Date, nullable=False)

    # Contoare
    tasks_solved_count: Mapped[int] = mapped_column(
        Integer, default=0, nullable=False)
    correct_answers_count: Mapped[int] = mapped_column(
        Integer, default=0, nullable=False)

    # Snapshot al obiectivului la momentul creării înregistrării
    goal_target: Mapped[int] = mapped_column(
        Integer, default=5, nullable=False)

    # Stare recompensă
    is_goal_reached: Mapped[bool] = mapped_column(
        Boolean, default=False, nullable=False)
    is_reward_claimed: Mapped[bool] = mapped_column(
        Boolean, default=False, nullable=False)

    # Protecție împotriva dublei acordări
    bonus_elo_granted: Mapped[float] = mapped_column(
        Float, default=0.0, nullable=False)

    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), nullable=False
    )

    # Un utilizator = o înregistrare pe zi
    __table_args__ = (
        UniqueConstraint("user_id", "goal_date",
                         name="uq_daily_goal_user_date"),
    )

    # Relații
    user: Mapped["User"] = relationship("User", back_populates="daily_goals")

    def __repr__(self):
        return f"<DailyGoal user={self.user_id} date={self.goal_date} {self.correct_answers_count}/{self.goal_target}>"
