# Importăm toate modelele ca Alembic să le detecteze automat
from app.models.category import Category
from app.models.user import User
from app.models.task import Task, DifficultyEnum, AnswerTypeEnum, DIFFICULTY_ELO, TASK_ELO_MIN, TASK_ELO_MAX
from app.models.user_task_history import UserTaskHistory
from app.models.daily_goal import DailyGoal
from app.models.refresh_token import RefreshToken
from app.models.achievement import Achievement, UserAchievement, AchievementCategoryEnum

__all__ = [
    "Category",
    "User",
    "Task",
    "DifficultyEnum",
    "AnswerTypeEnum",
    "DIFFICULTY_ELO",
    "TASK_ELO_MIN",
    "TASK_ELO_MAX",
    "UserTaskHistory",
    "DailyGoal",
    "RefreshToken",
    "Achievement",
    "UserAchievement",
    "AchievementCategoryEnum",
]
