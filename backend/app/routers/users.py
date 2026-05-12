from __future__ import annotations
from fastapi import APIRouter, Depends, Query
from sqlalchemy import select, func
from sqlalchemy.ext.asyncio import AsyncSession
from app.database import get_db
from app.dependencies import get_current_user
from app.models.user import User
from app.models.user_task_history import UserTaskHistory
from app.models.task import Task
from app.models.category import Category
from app.models.daily_goal import DailyGoal
from app.schemas.user import (
    UserProfile, UserStats, UserUpdate,
    HistoryItem, HistoryResponse
)
from app.utils.ranks import get_rank

router = APIRouter(prefix="/api/users", tags=["Users"])


@router.get("/me", response_model=UserProfile)
async def get_my_profile(
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    # Total rezolvări
    total_solved = await db.scalar(
        select(func.count()).where(
            UserTaskHistory.user_id == current_user.id
        )
    ) or 0

    # Total corecte
    total_correct = await db.scalar(
        select(func.count()).where(
            UserTaskHistory.user_id == current_user.id,
            UserTaskHistory.is_correct == True,
        )
    ) or 0

    # Acuratețe
    accuracy = round((total_correct / total_solved * 100),
                     1) if total_solved > 0 else 0.0

    # Categoria favorită
    fav_result = await db.execute(
        select(Category.name, func.count(UserTaskHistory.id).label("cnt"))
        .join(Task, Task.id == UserTaskHistory.task_id)
        .join(Category, Category.id == Task.category_id)
        .where(
            UserTaskHistory.user_id == current_user.id,
            UserTaskHistory.is_correct == True,
        )
        .group_by(Category.name)
        .order_by(func.count(UserTaskHistory.id).desc())
        .limit(1)
    )
    fav_row = fav_result.first()
    favorite_category = fav_row[0] if fav_row else None

    return UserProfile(
        id=current_user.id,
        username=current_user.username,
        email=current_user.email,
        avatar_id=current_user.avatar_id,
        elo_rating=current_user.elo_rating,
        rank=get_rank(current_user.elo_rating),
        current_streak=current_user.current_streak,
        max_streak=current_user.max_streak,
        daily_goal_target=current_user.daily_goal_target,
        timezone=current_user.timezone,
        last_activity_date=current_user.last_activity_date,
        created_at=current_user.created_at,
        stats=UserStats(
            total_solved=total_solved,
            total_correct=total_correct,
            accuracy_percent=accuracy,
            favorite_category=favorite_category,
        ),
    )


@router.get("/me/history", response_model=HistoryResponse)
async def get_my_history(
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
    limit: int = Query(20, ge=1, le=100),
    offset: int = Query(0, ge=0),
):
    # Total înregistrări
    total = await db.scalar(
        select(func.count()).where(
            UserTaskHistory.user_id == current_user.id
        )
    ) or 0

    # Istoricul cu JOIN la task și categorie
    result = await db.execute(
        select(
            UserTaskHistory,
            Task.title.label("task_title"),
            Category.name.label("category_name"),
        )
        .join(Task, Task.id == UserTaskHistory.task_id)
        .join(Category, Category.id == Task.category_id)
        .where(UserTaskHistory.user_id == current_user.id)
        .order_by(UserTaskHistory.solved_at.desc())
        .limit(limit)
        .offset(offset)
    )
    rows = result.all()

    items = [
        HistoryItem(
            id=row.UserTaskHistory.id,
            task_id=row.UserTaskHistory.task_id,
            task_title=row.task_title,
            category_name=row.category_name,
            is_correct=row.UserTaskHistory.is_correct,
            submitted_answer=row.UserTaskHistory.submitted_answer,
            elo_before=row.UserTaskHistory.elo_before,
            elo_after=row.UserTaskHistory.elo_after,
            elo_delta=row.UserTaskHistory.elo_delta,
            time_taken=row.UserTaskHistory.time_taken,
            solved_at=row.UserTaskHistory.solved_at,
        )
        for row in rows
    ]

    return HistoryResponse(
        items=items,
        total=total,
        limit=limit,
        offset=offset,
    )


@router.patch("/me", response_model=UserProfile)
async def update_my_profile(
    body: UserUpdate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    if body.avatar_id is not None:
        current_user.avatar_id = body.avatar_id

    if body.daily_goal_target is not None:
        current_user.daily_goal_target = body.daily_goal_target

    if body.timezone is not None:
        current_user.timezone = body.timezone

    await db.flush()

    # Returnăm profilul actualizat
    return await get_my_profile(db=db, current_user=current_user)
