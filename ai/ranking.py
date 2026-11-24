
from models.analysis import Difficulty


# Weight assigned to each ranking signal
SKILL_RELEVANCE_WEIGHT = 0.50
SKILL_COVERAGE_WEIGHT = 0.30
DIFFICULTY_WEIGHT = 0.20


# Higher scores indicate a better match for a beginner developer
DIFFICULTY_SCORES = {
    Difficulty.BEGINNER: 100,
    Difficulty.INTERMEDIATE: 70,
    Difficulty.ADVANCED: 40,
}


def calculate_hybrid_score(
    match_percentage: float,
    fit_score: int,
    difficulty: Difficulty,
) -> float:
    """Calculate an issue's final hybrid recommendation score."""

    difficulty_score = DIFFICULTY_SCORES[difficulty]

    hybrid_score = (
        match_percentage * SKILL_RELEVANCE_WEIGHT
        + fit_score * SKILL_COVERAGE_WEIGHT
        + difficulty_score * DIFFICULTY_WEIGHT
    )

    return round(hybrid_score, 2)
