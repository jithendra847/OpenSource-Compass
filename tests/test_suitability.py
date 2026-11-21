from ai.suitability import analyze_suitability
from models.analysis import Difficulty, Recommendation


def test_full_skill_match_is_ready():
    result = analyze_suitability(
        ["Python", "Git", "SQL"],
        ["Python", "Git", "SQL"],
        Difficulty.BEGINNER,
    )

    assert result.fit_score == 100
    assert result.suitable is True
    assert result.recommendation == Recommendation.READY
    assert result.missing_skills == []


def test_skill_matching_is_case_insensitive():
    result = analyze_suitability(
        ["python", "GIT"],
        ["Python", "Git"],
        Difficulty.BEGINNER,
    )

    assert result.fit_score == 100
    assert result.matched_skills == ["Python", "Git"]


def test_80_percent_match_is_ready():
    result = analyze_suitability(
        ["Python", "Git", "SQL", "Docker"],
        ["Python", "Git", "SQL", "Docker", "Testing"],
        Difficulty.INTERMEDIATE,
    )

    assert result.fit_score == 80
    assert result.recommendation == Recommendation.READY
    assert result.suitable is True
    assert result.missing_skills == ["Testing"]


def test_70_percent_match_is_suitable_but_prepare_first():
    result = analyze_suitability(
        ["Python", "Git", "SQL", "Docker", "Testing", "HTML", "CSS"],
        ["Python", "Git", "SQL", "Docker", "Testing",
         "HTML", "CSS", "JavaScript", "React", "FastAPI"],
        Difficulty.BEGINNER,
    )

    assert result.fit_score == 70
    assert result.suitable is True
    assert result.recommendation == Recommendation.PREPARE


def test_50_percent_match_recommends_preparation():
    result = analyze_suitability(
        ["Python", "Git"],
        ["Python", "Git", "SQL", "Docker"],
        Difficulty.INTERMEDIATE,
    )

    assert result.fit_score == 50
    assert result.recommendation == Recommendation.PREPARE
    assert result.suitable is False
    assert result.preparation_skills == ["SQL", "Docker"]


def test_low_match_is_stretch_challenge():
    result = analyze_suitability(
        ["Python"],
        ["Python", "Git", "SQL", "Docker"],
        Difficulty.BEGINNER,
    )

    assert result.fit_score == 25
    assert result.recommendation == Recommendation.STRETCH
    assert result.suitable is False


def test_zero_skill_match_is_stretch():
    result = analyze_suitability(
        ["Java"],
        ["Python", "Git", "SQL"],
        Difficulty.INTERMEDIATE,
    )

    assert result.fit_score == 0
    assert result.matched_skills == []
    assert result.recommendation == Recommendation.STRETCH


def test_advanced_issue_requires_preparation_even_with_high_match():
    result = analyze_suitability(
        ["Python", "Git", "SQL", "Docker"],
        ["Python", "Git", "SQL", "Docker", "Testing"],
        Difficulty.ADVANCED,
    )

    assert result.fit_score == 80
    assert result.suitable is False
    assert result.recommendation == Recommendation.PREPARE


def test_advanced_issue_with_low_match_is_stretch():
    result = analyze_suitability(
        ["Python"],
        ["Python", "Git", "SQL", "Docker"],
        Difficulty.ADVANCED,
    )

    assert result.fit_score == 25
    assert result.recommendation == Recommendation.STRETCH


def test_advanced_issue_with_50_percent_match_is_stretch():
    result = analyze_suitability(
        ["Python", "Git"],
        ["Python", "Git", "SQL", "Docker"],
        Difficulty.ADVANCED,
    )

    assert result.fit_score == 50
    assert result.recommendation == Recommendation.STRETCH


def test_missing_skills_are_returned_for_preparation():
    result = analyze_suitability(
        ["Python"],
        ["Python", "Git", "SQL"],
        Difficulty.INTERMEDIATE,
    )

    assert result.matched_skills == ["Python"]
    assert result.missing_skills == ["Git", "SQL"]
    assert result.preparation_skills == ["Git", "SQL"]


def test_no_required_skills_can_be_evaluated():
    result = analyze_suitability(
        ["Python", "Git"],
        [],
        Difficulty.BEGINNER,
    )

    assert result.fit_score == 0
    assert result.suitable is False
    assert result.recommendation == Recommendation.PREPARE
    assert result.matched_skills == []
    assert result.missing_skills == []
    assert result.preparation_skills == []


def test_fit_score_rounding():
    result = analyze_suitability(
        ["Python"],
        ["Python", "Git", "SQL"],
        Difficulty.BEGINNER,
    )

    assert result.fit_score == 33


def test_reason_is_provided():
    result = analyze_suitability(
        ["Python", "Git"],
        ["Python", "Git", "SQL"],
        Difficulty.INTERMEDIATE,
    )

    assert isinstance(result.reason, str)
    assert len(result.reason) > 0