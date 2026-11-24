from ai.ranking import calculate_hybrid_score
from models.analysis import Difficulty


def test_calculate_hybrid_score_beginner():
    score = calculate_hybrid_score(
        match_percentage=80,
        fit_score=75,
        difficulty=Difficulty.BEGINNER,
    )

    assert score == 82.5


def test_calculate_hybrid_score_intermediate():
    score = calculate_hybrid_score(
        match_percentage=80,
        fit_score=75,
        difficulty=Difficulty.INTERMEDIATE,
    )

    assert score == 76.5


def test_calculate_hybrid_score_advanced():
    score = calculate_hybrid_score(
        match_percentage=80,
        fit_score=75,
        difficulty=Difficulty.ADVANCED,
    )

    assert score == 70.5

def test_calculate_hybrid_score_lowest_values():
    score = calculate_hybrid_score(
        match_percentage=0,
        fit_score=0,
        difficulty=Difficulty.ADVANCED,
    )

    assert score == 8.0


def test_calculate_hybrid_score_highest_values():
    score = calculate_hybrid_score(
        match_percentage=100,
        fit_score=100,
        difficulty=Difficulty.BEGINNER,
    )

    assert score == 100.0