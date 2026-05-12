from __future__ import annotations
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from pydantic import BaseModel
from app.database import get_db
from app.dependencies import get_current_user
from app.models.user import User
from app.services.daily_goal_service import get_or_create_daily_goal, claim_reward

router = APIRouter(prefix="/api/daily-goal", tags=["Daily Goal"])


class DailyGoalOut(BaseModel):
    correct: int
    target: int
    is_reached: bool
    is_claimed: bool
    bonus_elo: float


@router.get("/today", response_model=DailyGoalOut)
async def get_today_goal(
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    goal = await get_or_create_daily_goal(db, current_user)
    return DailyGoalOut(
        correct=goal.correct_answers_count,
        target=goal.goal_target,
        is_reached=goal.is_goal_reached,
        is_claimed=goal.is_reward_claimed,
        bonus_elo=goal.bonus_elo_granted,
    )


@router.post("/claim", response_model=DailyGoalOut)
async def claim_daily_reward(
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    goal = await get_or_create_daily_goal(db, current_user)

    if not goal.is_goal_reached:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Obiectivul zilnic nu a fost atins încă"
        )

    await claim_reward(db, current_user, goal)

    return DailyGoalOut(
        correct=goal.correct_answers_count,
        target=goal.goal_target,
        is_reached=goal.is_goal_reached,
        is_claimed=goal.is_reward_claimed,
        bonus_elo=goal.bonus_elo_granted,
    )
