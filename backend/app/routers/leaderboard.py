from __future__ import annotations
from fastapi import APIRouter, Depends
from sqlalchemy import select, func
from sqlalchemy.ext.asyncio import AsyncSession
from app.database import get_db
from app.dependencies import get_current_user
from app.models.user import User
from app.schemas.user import LeaderboardEntry, LeaderboardResponse
from app.utils.ranks import get_rank

router = APIRouter(prefix="/api/leaderboard", tags=["Leaderboard"])


async def get_user_rank(db: AsyncSession, user: User) -> int:
    """Calculează poziția utilizatorului în clasament."""
    rank = await db.scalar(
        select(func.count()).where(
            User.elo_rating > user.elo_rating,
            User.is_active == True,
        )
    )
    return (rank or 0) + 1


@router.get("", response_model=LeaderboardResponse)
async def get_leaderboard(
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    # Top 10 utilizatori
    top_result = await db.execute(
        select(User)
        .where(User.is_active == True)
        .order_by(User.elo_rating.desc())
        .limit(10)
    )
    top_users = top_result.scalars().all()

    top_10 = [
        LeaderboardEntry(
            rank=idx + 1,
            user_id=u.id,
            username=u.username,
            elo_rating=round(u.elo_rating, 1),
            avatar_id=u.avatar_id,
            rank_name=get_rank(u.elo_rating),
        )
        for idx, u in enumerate(top_users)
    ]

    # Rangul utilizatorului curent
    current_rank = await get_user_rank(db, current_user)

    current_user_entry = LeaderboardEntry(
        rank=current_rank,
        user_id=current_user.id,
        username=current_user.username,
        elo_rating=round(current_user.elo_rating, 1),
        avatar_id=current_user.avatar_id,
        rank_name=get_rank(current_user.elo_rating),
    )

    # Vecinii — 2 deasupra și 2 dedesubt
    top_ids = {u.id for u in top_users}

    neighbors_above = await db.execute(
        select(User)
        .where(
            User.is_active == True,
            User.elo_rating > current_user.elo_rating,
            User.id.not_in(top_ids),
            User.id != current_user.id,
        )
        .order_by(User.elo_rating.asc())
        .limit(2)
    )

    neighbors_below = await db.execute(
        select(User)
        .where(
            User.is_active == True,
            User.elo_rating < current_user.elo_rating,
            User.id.not_in(top_ids),
            User.id != current_user.id,
        )
        .order_by(User.elo_rating.desc())
        .limit(2)
    )

    above = neighbors_above.scalars().all()
    below = neighbors_below.scalars().all()

    neighbors = []
    for u in above:
        rank = await get_user_rank(db, u)
        neighbors.append(LeaderboardEntry(
            rank=rank,
            user_id=u.id,
            username=u.username,
            elo_rating=round(u.elo_rating, 1),
            avatar_id=u.avatar_id,
            rank_name=get_rank(u.elo_rating),
        ))

    neighbors.append(current_user_entry)

    for u in below:
        rank = await get_user_rank(db, u)
        neighbors.append(LeaderboardEntry(
            rank=rank,
            user_id=u.id,
            username=u.username,
            elo_rating=round(u.elo_rating, 1),
            avatar_id=u.avatar_id,
            rank_name=get_rank(u.elo_rating),
        ))

    return LeaderboardResponse(
        top_10=top_10,
        current_user=current_user_entry,
        neighbors=neighbors,
    )
