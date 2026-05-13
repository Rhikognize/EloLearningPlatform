from __future__ import annotations
from fastapi import APIRouter, Depends
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from pydantic import BaseModel
from app.database import get_db
from app.dependencies import get_current_user
from app.models.category import Category
from app.models.user import User

router = APIRouter(prefix="/api/categories", tags=["Categories"])


class CategoryOut(BaseModel):
    id: int
    name: str
    description: str | None
    icon_name: str

    model_config = {"from_attributes": True}


@router.get("", response_model=list[CategoryOut])
async def get_categories(
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    result = await db.execute(
        select(Category).order_by(Category.name)
    )
    return result.scalars().all()
