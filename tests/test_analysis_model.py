import pytest
from pydantic import ValidationError

from models.analysis import Difficulty, DifficultyAnalysis


def test_beginner_difficulty_is_valid():
    result = DifficultyAnalysis(
        difficulty=Difficulty.BEGINNER,
        reason="The issue requires only basic Python knowledge."
    )

    assert result.difficulty == Difficulty.BEGINNER


def test_intermediate_difficulty_is_valid():
    result = DifficultyAnalysis(
        difficulty=Difficulty.INTERMEDIATE,
        reason="The task requires debugging existing API logic."
    )

    assert result.difficulty == Difficulty.INTERMEDIATE


def test_advanced_difficulty_is_valid():
    result = DifficultyAnalysis(
        difficulty=Difficulty.ADVANCED,
        reason="The task requires architectural changes across several modules."
    )

    assert result.difficulty == Difficulty.ADVANCED


def test_difficulty_accepts_string_value():
    result = DifficultyAnalysis(
        difficulty="Beginner",
        reason="A simple task."
    )

    assert result.difficulty == Difficulty.BEGINNER


def test_invalid_difficulty_is_rejected():
    with pytest.raises(ValidationError):
        DifficultyAnalysis(
            difficulty="Expert",
            reason="A task requiring extensive experience."
        )


def test_empty_reason_is_rejected():
    with pytest.raises(ValidationError):
        DifficultyAnalysis(
            difficulty=Difficulty.BEGINNER,
            reason=""
        )
