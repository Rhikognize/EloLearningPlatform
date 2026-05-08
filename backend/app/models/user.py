from datetime import datetime, date
from sqlalchemy import Integer, String, Float, Boolean, Date, DateTime, Index, func
from sqlalchemy.orm import Mapped, mapped_column, relationship
from app.database import Base
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from app.models.user_task_history import UserTaskHistory
    from app.models.daily_goal import DailyGoal
    from app.models.refresh_token import RefreshToken
    from app.models.achievement import UserAchievement


class User(Base):
    __tablename__ = "users"

    id: Mapped[int] = mapped_column(
        Integer, primary_key=True, autoincrement=True)
    username: Mapped[str] = mapped_column(
        String(50), unique=True, nullable=False, index=True)
    email: Mapped[str] = mapped_column(
        String(255), unique=True, nullable=False, index=True)

    # Parola poate fi null pentru utilizatorii Google OAuth
    password_hash: Mapped[str | None] = mapped_column(
        String(255), nullable=True)
    google_id: Mapped[str | None] = mapped_column(
        String(255), unique=True, nullable=True)

    # Personalizare
    avatar_id: Mapped[int] = mapped_column(Integer, default=1, nullable=False)
    timezone: Mapped[str] = mapped_column(
        String(50), default="Europe/Moscow", nullable=False)
    daily_goal_target: Mapped[int] = mapped_column(
        Integer, default=5, nullable=False)

    # ELO și gamificare
    elo_rating: Mapped[float] = mapped_column(
        Float, default=1200.0, nullable=False)
    current_streak: Mapped[int] = mapped_column(
        Integer, default=0, nullable=False)
    max_streak: Mapped[int] = mapped_column(Integer, default=0, nullable=False)
    last_activity_date: Mapped[date | None] = mapped_column(
        Date, nullable=True)

    # Permisiuni
    is_active: Mapped[bool] = mapped_column(
        Boolean, default=True, nullable=False)
    is_superuser: Mapped[bool] = mapped_column(
        Boolean, default=False, nullable=False)

    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), nullable=False
    )

    # Relații
    task_history: Mapped[list["UserTaskHistory"]] = relationship(
        "UserTaskHistory", back_populates="user"
    )
    daily_goals: Mapped[list["DailyGoal"]] = relationship(
        "DailyGoal", back_populates="user"
    )
    refresh_tokens: Mapped[list["RefreshToken"]] = relationship(
        "RefreshToken", back_populates="user"
    )
    achievements: Mapped[list["UserAchievement"]] = relationship(
        "UserAchievement", back_populates="user"
    )
    __table_args__ = (
        Index("ix_users_elo_rating", "elo_rating"),
        Index("ix_users_is_active", "is_active"),
    )

    def __repr__(self):
        return f"<User id={self.id} username={self.username} elo={self.elo_rating}>"
