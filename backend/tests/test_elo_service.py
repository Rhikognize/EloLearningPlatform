from app.services.elo_service import calculate_elo, expected_score


def test_correct_answer_raises_player_elo():
    new_player, _ = calculate_elo(1200, 1200, True, 10)
    assert new_player > 1200


def test_wrong_answer_lowers_player_elo():
    new_player, _ = calculate_elo(1200, 1200, False, 10)
    assert new_player < 1200


def test_correct_answer_lowers_task_elo():
    _, new_task = calculate_elo(1200, 1200, True, 10)
    assert new_task < 1200


def test_wrong_answer_raises_task_elo():
    _, new_task = calculate_elo(1200, 1200, False, 10)
    assert new_task > 1200


def test_repeat_correct_no_elo_change():
    new_player, new_task = calculate_elo(
        1200, 1200, True, 10, is_first_correct=False)
    assert new_player == 1200
    assert new_task == 1200


def test_player_elo_floor():
    new_player, _ = calculate_elo(101, 2500, False, 10)
    assert new_player >= 100


def test_task_elo_ceiling():
    _, new_task = calculate_elo(100, 2499, False, 10)
    assert new_task <= 2500


def test_task_elo_floor():
    _, new_task = calculate_elo(2500, 801, True, 10)
    assert new_task >= 800


def test_hard_task_gives_more_elo():
    new_player_easy, _ = calculate_elo(1200, 900, True, 10)
    new_player_hard, _ = calculate_elo(1200, 1800, True, 10)
    assert new_player_hard > new_player_easy


def test_provisional_k_factor():
    new_player_prov, _ = calculate_elo(1200, 1200, True, 5)
    new_player_stable, _ = calculate_elo(1200, 1200, True, 50)
    assert new_player_prov == new_player_stable
