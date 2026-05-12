from __future__ import annotations
from sqlalchemy import select
from sqlalchemy.dialects.postgresql import insert as pg_insert
from sqlalchemy.ext.asyncio import AsyncSession
from app.models.daily_goal import DailyGoal
from app.models.user import User
from app.services.streak_service import get_user_today
from app.services.elo_service import DAILY_GOAL_BONUS_ELO


async def get_or_create_daily_goal(
    db: AsyncSession,
    user: User,
) -> DailyGoal:
    today = get_user_today(user.timezone)

    result = await db.execute(
        select(DailyGoal).where(
            DailyGoal.user_id == user.id,
            DailyGoal.goal_date == today,
        )
    )
    goal = result.scalar_one_or_none()

    if goal is None:
        goal = DailyGoal(
            user_id=user.id,
            goal_date=today,
            goal_target=user.daily_goal_target,
        )
        db.add(goal)
        await db.flush()

    return goal


async def record_attempt(
    goal: DailyGoal,
    is_correct: bool,
    is_first_correct: bool = True,
) -> bool:
    goal.tasks_solved_count += 1

    # Contorizăm pentru obiectivul zilnic doar prima rezolvare corectă
    # Dacă rezolvi aceeași sarcină de 5 ori corect — contează o singură dată
    if is_correct and is_first_correct:
        goal.correct_answers_count += 1
    elif not is_correct:
        # Greșelile le contorizăm întotdeauna (pentru statistici)
        pass

    was_reached_before = goal.is_goal_reached

    if (
        not was_reached_before
        and goal.correct_answers_count >= goal.goal_target
    ):
        goal.is_goal_reached = True
        return True

    return False


async def claim_reward(
    db: AsyncSession,
    user: User,
    goal: DailyGoal,
) -> float:
    today = get_user_today(user.timezone)

    if goal.goal_date != today:
        return 0.0

    if not goal.is_goal_reached:
        return 0.0

    if goal.is_reward_claimed:
        return 0.0

    goal.is_reward_claimed = True
    goal.bonus_elo_granted = DAILY_GOAL_BONUS_ELO
    user.elo_rating += DAILY_GOAL_BONUS_ELO

    return DAILY_GOAL_BONUS_ELO
