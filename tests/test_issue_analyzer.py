from ai import issue_analyzer
from models.analysis import (
    Difficulty,
    DifficultyAnalysis,
    IssueSummary,
    Recommendation,
    SuitabilityAnalysis,
)


def test_analyze_issue_success(monkeypatch):
    # Arrange
    title = "Add a REST API endpoint"
    body = "Create an endpoint using FastAPI."
    labels = ["good first issue"]
    user_skills = ["Python", "FastAPI"]

    difficulty_result = DifficultyAnalysis(
        difficulty=Difficulty.BEGINNER,
        reason="The issue requires basic API development.",
    )

    required_skills_result = ["Python", "FastAPI"]

    summary_result = IssueSummary(
        summary="Build a simple API endpoint using FastAPI."
    )

    suitability_result = SuitabilityAnalysis(
        fit_score=90,
        suitable=True,
        matched_skills=["Python", "FastAPI"],
        missing_skills=[],
        recommendation=Recommendation.READY,
        reason="The user has all the required skills.",
        preparation_skills=[],
    )

    calls = {}

    def mock_analyze_difficulty(t, b, l):
        calls["difficulty"] = (t, b, l)
        return difficulty_result

    def mock_extract_required_skills(t, b, l):
        calls["skills"] = (t, b, l)
        return required_skills_result

    def mock_summarize_issue(t, b):
        calls["summary"] = (t, b)
        return summary_result

    def mock_analyze_suitability(u, r, d):
        calls["suitability"] = (u, r, d)
        return suitability_result

    monkeypatch.setattr(
        issue_analyzer, "analyze_difficulty",
        mock_analyze_difficulty,
    )
    monkeypatch.setattr(
        issue_analyzer, "extract_required_skills",
        mock_extract_required_skills,
    )
    monkeypatch.setattr(
        issue_analyzer, "summarize_issue",
        mock_summarize_issue,
    )
    monkeypatch.setattr(
        issue_analyzer, "analyze_suitability",
        mock_analyze_suitability,
    )

    # Act
    result = issue_analyzer.analyze_issue(
        title, body, labels, user_skills
    )

    # Assert: output
    assert result.difficulty == Difficulty.BEGINNER
    assert result.difficulty_reason == difficulty_result.reason
    assert result.required_skills == required_skills_result
    assert result.summary == summary_result.summary
    assert result.suitability == suitability_result

    # Assert: dependencies received correct inputs
    assert calls["difficulty"] == (title, body, labels)
    assert calls["skills"] == (title, body, labels)
    assert calls["summary"] == (title, body)
    assert calls["suitability"] == (
        user_skills,
        required_skills_result,
        Difficulty.BEGINNER,
    )


def test_analyze_issue_defaults_none_inputs(monkeypatch):
    # Arrange
    difficulty_result = DifficultyAnalysis(
        difficulty=Difficulty.BEGINNER,
        reason="Simple issue.",
    )

    summary_result = IssueSummary(
        summary="A simple issue summary."
    )

    suitability_result = SuitabilityAnalysis(
        fit_score=0,
        suitable=False,
        matched_skills=[],
        missing_skills=["Python"],
        recommendation=Recommendation.PREPARE,
        reason="No user skills were provided.",
        preparation_skills=["Python"],
    )

    calls = {}

    def mock_analyze_difficulty(t, b, l):
        calls["labels"] = l
        return difficulty_result

    def mock_extract_required_skills(t, b, l):
        return ["Python"]

    def mock_summarize_issue(t, b):
        return summary_result

    def mock_analyze_suitability(u, r, d):
        calls["user_skills"] = u
        return suitability_result

    monkeypatch.setattr(
        issue_analyzer, "analyze_difficulty",
        mock_analyze_difficulty,
    )
    monkeypatch.setattr(
        issue_analyzer, "extract_required_skills",
        mock_extract_required_skills,
    )
    monkeypatch.setattr(
        issue_analyzer, "summarize_issue",
        mock_summarize_issue,
    )
    monkeypatch.setattr(
        issue_analyzer, "analyze_suitability",
        mock_analyze_suitability,
    )

    # Act
    result = issue_analyzer.analyze_issue(
        title="Test issue",
        body="",
        labels=None,
        user_skills=None,
    )

    # Assert
    assert calls["labels"] == []
    assert calls["user_skills"] == []
    assert result.difficulty == Difficulty.BEGINNER
    assert result.required_skills == ["Python"]
    assert result.suitability.recommendation == Recommendation.PREPARE