from datetime import datetime
from sqlalchemy import Integer, String, DateTime, ForeignKey, UniqueConstraint, Enum, func
from sqlalchemy.orm import Mapped, mapped_column, relationship
import enum
from app.database import Base
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from app.models.user import User


class AchievementCategoryEnum(str, enum.Enum):
    streak = "streak"
    elo = "elo"
    tasks = "tasks"
    special = "special"


class Achievement(Base):
    __tablename__ = "achievements"

    id: Mapped[int] = mapped_column(
        Integer, primary_key=True, autoincrement=True)

    # Identificator unic pentru logică (ex: "streak_7", "elo_1400")
    code: Mapped[str] = mapped_column(String(50), unique=True, nullable=False)
    title: Mapped[str] = mapped_column(String(100), nullable=False)
    description: Mapped[str] = mapped_column(String(255), nullable=False)
    icon_name: Mapped[str] = mapped_column(
        String(50), nullable=False, default="award")
    category: Mapped[AchievementCategoryEnum] = mapped_column(
        Enum(AchievementCategoryEnum), nullable=False
    )

    # Relații
    user_achievements: Mapped[list["UserAchievement"]] = relationship(
        "UserAchievement", back_populates="achievement"
    )

    def __repr__(self):
        return f"<Achievement code={self.code} title={self.title}>"


class UserAchievement(Base):
    __tablename__ = "user_achievements"

    id: Mapped[int] = mapped_column(
        Integer, primary_key=True, autoincrement=True)

    user_id: Mapped[int] = mapped_column(
        Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True
    )
    achievement_id: Mapped[int] = mapped_column(
        Integer, ForeignKey("achievements.id", ondelete="CASCADE"), nullable=False
    )

    earned_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), nullable=False
    )

    # Un utilizator poate obține fiecare achievement o singură dată
    __table_args__ = (
        UniqueConstraint("user_id", "achievement_id",
                         name="uq_user_achievement"),
    )

    # Relații
    user: Mapped["User"] = relationship("User", back_populates="achievements")
    achievement: Mapped["Achievement"] = relationship(
        "Achievement", back_populates="user_achievements"
    )

    def __repr__(self):
        return f"<UserAchievement user={self.user_id} achievement={self.achievement_id}>"
