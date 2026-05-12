from __future__ import annotations
from sqlalchemy import select, func
from sqlalchemy.ext.asyncio import AsyncSession
from app.models.achievement import Achievement, UserAchievement
from app.models.user import User
from app.models.user_task_history import UserTaskHistory


async def check_and_award(
    db: AsyncSession,
    user: User,
    time_taken: int | None = None,
) -> list[Achievement]:
    already_earned = await db.execute(
        select(UserAchievement.achievement_id).where(
            UserAchievement.user_id == user.id
        )
    )
    earned_ids = set(already_earned.scalars().all())

    all_achievements = await db.execute(select(Achievement))
    achievements = all_achievements.scalars().all()

    total_correct = await db.scalar(
        select(func.count()).where(
            UserTaskHistory.user_id == user.id,
            UserTaskHistory.is_correct == True,
        )
    ) or 0

    daily_goals_claimed = 0
    from app.models.daily_goal import DailyGoal
    daily_goals_claimed = await db.scalar(
        select(func.count()).where(
            DailyGoal.user_id == user.id,
            DailyGoal.is_reward_claimed == True,
        )
    ) or 0

    newly_earned = []

    for achievement in achievements:
        if achievement.id in earned_ids:
            continue

        earned = False

        if achievement.code == "first_solve":
            earned = total_correct >= 1

        elif achievement.code == "streak_3":
            earned = user.current_streak >= 3

        elif achievement.code == "streak_7":
            earned = user.current_streak >= 7

        elif achievement.code == "streak_30":
            earned = user.current_streak >= 30

        elif achievement.code == "tasks_10":
            earned = total_correct >= 10

        elif achievement.code == "tasks_50":
            earned = total_correct >= 50

        elif achievement.code == "tasks_100":
            earned = total_correct >= 100

        elif achievement.code == "elo_1000":
            earned = user.elo_rating >= 1000

        elif achievement.code == "elo_1400":
            earned = user.elo_rating >= 1400

        elif achievement.code == "elo_1800":
            earned = user.elo_rating >= 1800

        elif achievement.code == "daily_goal_3":
            earned = daily_goals_claimed >= 3

        elif achievement.code == "speed_demon":
            earned = (
                time_taken is not None
                and time_taken < 10
            )

        if earned:
            user_achievement = UserAchievement(
                user_id=user.id,
                achievement_id=achievement.id,
            )
            db.add(user_achievement)
            newly_earned.append(achievement)

    return newly_earned
