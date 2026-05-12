from __future__ import annotations
import math
from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy import select, func, and_
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload
from app.database import get_db
from app.dependencies import get_current_user
from app.models.task import Task, DifficultyEnum
from app.models.category import Category
from app.models.user import User
from app.models.user_task_history import UserTaskHistory
from app.schemas.task import TaskOut, TaskListResponse

router = APIRouter(prefix="/api/tasks", tags=["Tasks"])


def task_to_out(task: Task) -> TaskOut:
    """
    Convertește obiectul Task SQLAlchemy în schema TaskOut.
    Adaugă category_name din relația cu Category.
    """
    return TaskOut(
        id=task.id,
        category_id=task.category_id,
        category_name=task.category.name if task.category else "Necunoscut",
        title=task.title,
        description=task.description,
        answer_type=task.answer_type,
        answer_options=task.answer_options,
        hint=task.hint,
        difficulty=task.difficulty,
        elo_rating=task.elo_rating,
        solve_count=task.solve_count,
        created_at=task.created_at,
    )


# ══════════════════════════════════════════════════════
# IMPORTANT — /recommended trebuie înregistrat ÎNAINTE de /{id}
# Altfel FastAPI interpretează "recommended" ca și cum ar fi un ID
# și încearcă să îl convertească în integer → eroare 422
# ══════════════════════════════════════════════════════

@router.get("/recommended", response_model=list[TaskOut])
async def get_recommended_tasks(
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """
    Returnează 5 sarcini recomandate pentru utilizatorul curent.

    Criterii de selecție:
    - ELO sarcină în intervalul [user_elo - 200, user_elo + 200]
    - Utilizatorul nu a rezolvat corect sarcina anterior
    - Sarcina este activă
    """
    user_elo = current_user.elo_rating
    elo_min = user_elo - 200
    elo_max = user_elo + 200

    # Subquery — ID-urile sarcinilor rezolvate corect de utilizator
    solved_subquery = (
        select(UserTaskHistory.task_id)
        .where(
            UserTaskHistory.user_id == current_user.id,
            UserTaskHistory.is_correct == True,
        )
    )

    result = await db.execute(
        select(Task)
        .options(selectinload(Task.category))
        .where(
            Task.is_active == True,
            Task.elo_rating >= elo_min,
            Task.elo_rating <= elo_max,
            Task.id.not_in(solved_subquery),
        )
        .order_by(func.random())
        .limit(5)
    )
    tasks = result.scalars().all()

    return [task_to_out(task) for task in tasks]


@router.get("", response_model=TaskListResponse)
async def get_tasks(
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
    category_id: int | None = Query(None),
    difficulty: DifficultyEnum | None = Query(None),
    search: str | None = Query(None),
    page: int = Query(1, ge=1),
    per_page: int = Query(20, ge=1, le=50),
):
    """
    Lista de sarcini cu filtrare și paginare.

    Filtre disponibile:
    - category_id — filtrare după categorie
    - difficulty — filtrare după dificultate
    - search — căutare după titlu (case insensitive)
    - page + per_page — paginare
    """
    # Construim query-ul de bază
    base_query = (
        select(Task)
        .options(selectinload(Task.category))
        .where(Task.is_active == True)
    )

    # Adăugăm filtrele opționale
    if category_id is not None:
        base_query = base_query.where(Task.category_id == category_id)

    if difficulty is not None:
        base_query = base_query.where(Task.difficulty == difficulty)

    if search is not None and search.strip():
        # ilike = case insensitive LIKE
        # %search% = conține textul oriunde în titlu
        base_query = base_query.where(
            Task.title.ilike(f"%{search.strip()}%")
        )

    # Numărăm totalul pentru paginare
    count_query = select(func.count()).select_from(base_query.subquery())
    total = await db.scalar(count_query)

    # Aplicăm paginarea
    offset = (page - 1) * per_page
    result = await db.execute(
        base_query
        .order_by(Task.difficulty, Task.elo_rating)
        .offset(offset)
        .limit(per_page)
    )
    tasks = result.scalars().all()

    total_pages = math.ceil(total / per_page) if total > 0 else 1

    return TaskListResponse(
        items=[task_to_out(task) for task in tasks],
        total=total,
        page=page,
        per_page=per_page,
        total_pages=total_pages,
    )


@router.get("/{task_id}", response_model=TaskOut)
async def get_task(
    task_id: int,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """
    O singură sarcină după ID.
    correct_answer nu apare în răspuns — schema TaskOut nu îl include.
    """
    result = await db.execute(
        select(Task)
        .options(selectinload(Task.category))
        .where(Task.id == task_id, Task.is_active == True)
    )
    task = result.scalar_one_or_none()

    if not task:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Sarcina nu a fost găsită"
        )

    return task_to_out(task)
