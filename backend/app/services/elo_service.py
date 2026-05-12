from __future__ import annotations
from app.models.task import TASK_ELO_MIN, TASK_ELO_MAX

PLAYER_K_FACTOR = 32
TASK_K_FACTOR_PROVISIONAL = 32
TASK_K_FACTOR_STABLE = 16
PROVISIONAL_THRESHOLD = 30
PLAYER_ELO_MIN = 100.0
DAILY_GOAL_BONUS_ELO = 50.0


def expected_score(rating_a: float, rating_b: float) -> float:
    return 1.0 / (1.0 + 10 ** ((rating_b - rating_a) / 400.0))


def calculate_elo(
    player_elo: float,
    task_elo: float,
    is_correct: bool,
    task_solve_count: int,
    is_first_correct: bool = True,
) -> tuple[float, float]:
    e_player = expected_score(player_elo, task_elo)

    k_task = (
        TASK_K_FACTOR_PROVISIONAL
        if task_solve_count < PROVISIONAL_THRESHOLD
        else TASK_K_FACTOR_STABLE
    )

    actual = 1.0 if is_correct else 0.0

    if is_correct and not is_first_correct:
        player_delta = 0.0
        task_delta = 0.0
    else:
        player_delta = PLAYER_K_FACTOR * (actual - e_player)
        task_delta = k_task * ((1 - actual) - (1 - e_player))

    new_player_elo = max(PLAYER_ELO_MIN, player_elo + player_delta)
    new_task_elo = max(TASK_ELO_MIN, min(TASK_ELO_MAX, task_elo + task_delta))

    return new_player_elo, new_task_elo
