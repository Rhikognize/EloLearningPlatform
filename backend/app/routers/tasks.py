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
from datetime import datetime, timezone
from sqlalchemy import select, func, and_
from app.models.user_task_history import UserTaskHistory
from app.schemas.task import SolveRequest, SolveResponse, AchievementOut, DailyGoalProgress
from app.services.elo_service import calculate_elo
from app.services.streak_service import update_streak
from app.services.daily_goal_service import get_or_create_daily_goal, record_attempt
from app.services.achievement_service import check_and_award
from app.services.answer_service import normalize_answer

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


@router.post("/{task_id}/solve", response_model=SolveResponse)
async def solve_task(
    task_id: int,
    body: SolveRequest,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    # ── 1. Verifică că sarcina există ────────────────────
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

    # ── 2. Cooldown — 10 secunde între încercări ─────────
    last_attempt = await db.scalar(
        select(UserTaskHistory.solved_at)
        .where(
            UserTaskHistory.user_id == current_user.id,
            UserTaskHistory.task_id == task_id,
        )
        .order_by(UserTaskHistory.solved_at.desc())
        .limit(1)
    )

    if last_attempt:
        last_attempt_utc = last_attempt.replace(tzinfo=timezone.utc)
        seconds_since = (datetime.now(timezone.utc) -
                         last_attempt_utc).total_seconds()
        if seconds_since < 10:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Așteaptă {int(10 - seconds_since)} secunde înainte de următoarea încercare"
            )

    # ── 3. Verifică răspunsul ─────────────────────────────
    user_answer = normalize_answer(body.answer, task.answer_type)
    correct_answer = normalize_answer(task.correct_answer, task.answer_type)
    is_correct = user_answer == correct_answer

    # ── 4. Anti-farming — prima rezolvare corectă ─────────
    first_correct = await db.scalar(
        select(func.count()).where(
            UserTaskHistory.user_id == current_user.id,
            UserTaskHistory.task_id == task_id,
            UserTaskHistory.is_correct == True,
        )
    )
    is_first_correct = first_correct == 0

    # ── 5. Max 3 penalizări per sarcină ──────────────────
    wrong_count = await db.scalar(
        select(func.count()).where(
            UserTaskHistory.user_id == current_user.id,
            UserTaskHistory.task_id == task_id,
            UserTaskHistory.is_correct == False,
        )
    )
    elo_penalty_applies = wrong_count < 3

    # ── 6. Calculează ELO ─────────────────────────────────
    elo_before = current_user.elo_rating
    task_elo_before = task.elo_rating

    if is_correct and not is_first_correct:
        new_player_elo = elo_before
        new_task_elo = task_elo_before
    elif not is_correct and not elo_penalty_applies:
        new_player_elo = elo_before
        new_task_elo = task_elo_before
    else:
        new_player_elo, new_task_elo = calculate_elo(
            player_elo=elo_before,
            task_elo=task_elo_before,
            is_correct=is_correct,
            task_solve_count=task.solve_count,
            is_first_correct=is_first_correct,
        )

    # ── 7. Aplică modificările ────────────────────────────
    current_user.elo_rating = new_player_elo
    task.elo_rating = new_task_elo
    task.solve_count += 1

    # ── 8. Actualizează streak ────────────────────────────
    update_streak(current_user)

    # ── 9. Actualizează daily goal ────────────────────────
    daily_goal = await get_or_create_daily_goal(db, current_user)
    await record_attempt(daily_goal, is_correct, is_first_correct)

    # ── 10. Salvează istoricul ────────────────────────────
    elo_delta = new_player_elo - elo_before
    history = UserTaskHistory(
        user_id=current_user.id,
        task_id=task_id,
        is_correct=is_correct,
        elo_before=elo_before,
        elo_after=new_player_elo,
        elo_delta=elo_delta,
        submitted_answer=body.answer,
        time_taken=body.time_taken,
    )
    db.add(history)
    await db.flush()

    # ── 11. Verifică achievements ─────────────────────────
    newly_earned = await check_and_award(
        db=db,
        user=current_user,
        time_taken=body.time_taken,
    )

    # ── 12. show_explanation ──────────────────────────────
    show_explanation = (
        not is_correct
        and wrong_count >= 2
        and task.explanation is not None
    )

    return SolveResponse(
        is_correct=is_correct,
        correct_answer=task.correct_answer if not is_correct else None,
        hint=task.hint if not is_correct else None,
        explanation=task.explanation if show_explanation else None,
        show_explanation=show_explanation,
        elo_before=elo_before,
        elo_after=new_player_elo,
        elo_delta=elo_delta,
        streak=current_user.current_streak,
        daily_goal_progress=DailyGoalProgress(
            correct=daily_goal.correct_answers_count,
            target=daily_goal.goal_target,
            is_reached=daily_goal.is_goal_reached,
        ),
        achievements_earned=[
            AchievementOut(
                code=a.code,
                title=a.title,
                icon_name=a.icon_name,
            )
            for a in newly_earned
        ],
    )
