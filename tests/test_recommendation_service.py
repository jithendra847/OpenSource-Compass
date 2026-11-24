from ai import recommendation_service
from models.analysis import (
    Difficulty,
    IssueAnalysis,
    Recommendation,
    SuitabilityAnalysis,
)


def test_enrich_recommendations_success(monkeypatch):
    recommendation = {
        "id": 1,
        "title": "Add a Python API endpoint",
        "body": "Implement an endpoint using FastAPI.",
        "labels": ["good first issue"],
        "match_percentage": 80.0,
        "score": 25,
    }

    mock_analysis = IssueAnalysis(
        difficulty=Difficulty.BEGINNER,
        difficulty_reason="Simple implementation task.",
        required_skills=["Python"],
        summary="Add a Python API endpoint.",
        suitability=SuitabilityAnalysis(
            fit_score=100,
            suitable=True,
            matched_skills=["Python"],
            missing_skills=[],
            recommendation=Recommendation.READY,
            reason="You have the required skills.",
            preparation_skills=[],
        ),
    )

    monkeypatch.setattr(
        recommendation_service,
        "analyze_issue",
        lambda **kwargs: mock_analysis,
    )

    result = recommendation_service.enrich_recommendations(
        recommendations=[recommendation],
        user_skills=["Python"],
    )

    assert len(result) == 1
    assert result[0]["hybrid_score"] == 90.0
    assert result[0]["analysis"] == mock_analysis

def test_enrich_recommendations_empty():
    result = recommendation_service.enrich_recommendations(
        recommendations=[],
        user_skills=["Python"],
    )

    assert result == []

def make_analysis(difficulty, fit_score=100):
    return IssueAnalysis(
        difficulty=difficulty,
        difficulty_reason="Test difficulty reason.",
        required_skills=["Python"],
        summary="Test issue summary.",
        suitability=SuitabilityAnalysis(
            fit_score=fit_score,
            suitable=True,
            matched_skills=["Python"],
            missing_skills=[],
            recommendation=Recommendation.READY,
            reason="Good skill match.",
            preparation_skills=[],
        ),
    )

def test_enrich_recommendations_sorts_by_hybrid_score(monkeypatch):
    recommendations = [
        {
            "title": "Advanced issue",
            "body": "Advanced task.",
            "labels": [],
            "match_percentage": 80.0,
            "score": 50,
        },
        {
            "title": "Beginner issue",
            "body": "Beginner task.",
            "labels": [],
            "match_percentage": 80.0,
            "score": 20,
        },
        {
            "title": "Intermediate issue",
            "body": "Intermediate task.",
            "labels": [],
            "match_percentage": 80.0,
            "score": 30,
        },
    ]

    analyses = {
        "Advanced issue": make_analysis(Difficulty.ADVANCED),
        "Beginner issue": make_analysis(Difficulty.BEGINNER),
        "Intermediate issue": make_analysis(Difficulty.INTERMEDIATE),
    }

    monkeypatch.setattr(
        recommendation_service,
        "analyze_issue",
        lambda **kwargs: analyses[kwargs["title"]],
    )

    result = recommendation_service.enrich_recommendations(
        recommendations,
        ["Python"],
    )

    assert [item["title"] for item in result] == [
        "Beginner issue",
        "Intermediate issue",
        "Advanced issue",
    ]

def test_enrich_recommendations_uses_score_as_tiebreaker(monkeypatch):
    recommendations = [
        {
            "title": "Issue A",
            "labels": [],
            "match_percentage": 80.0,
            "score": 20,
        },
        {
            "title": "Issue B",
            "labels": [],
            "match_percentage": 80.0,
            "score": 40,
        },
    ]

    mock_analysis = make_analysis(Difficulty.BEGINNER)

    monkeypatch.setattr(
        recommendation_service,
        "analyze_issue",
        lambda **kwargs: mock_analysis,
    )

    result = recommendation_service.enrich_recommendations(
        recommendations,
        ["Python"],
    )

    assert result[0]["title"] == "Issue B"
    assert result[1]["title"] == "Issue A"

def test_enrich_recommendations_does_not_modify_original(monkeypatch):
    recommendation = {
        "title": "Python issue",
        "body": "Implement a feature.",
        "labels": [],
        "match_percentage": 80.0,
        "score": 20,
    }

    original = recommendation.copy()

    monkeypatch.setattr(
        recommendation_service,
        "analyze_issue",
        lambda **kwargs: make_analysis(Difficulty.BEGINNER),
    )

    recommendation_service.enrich_recommendations(
        [recommendation],
        ["Python"],
    )

    assert recommendation == original
    assert "analysis" not in recommendation
    assert "hybrid_score" not in recommendation

def test_enrich_recommendations_passes_correct_arguments(monkeypatch):
    recommendation = {
        "title": "Python API endpoint",
        "body": "Build an endpoint using FastAPI.",
        "labels": ["good first issue"],
        "match_percentage": 80.0,
        "score": 25,
    }

    captured = {}

    def mock_analyze_issue(**kwargs):
        captured.update(kwargs)
        return make_analysis(Difficulty.BEGINNER)

    monkeypatch.setattr(
        recommendation_service,
        "analyze_issue",
        mock_analyze_issue,
    )

    recommendation_service.enrich_recommendations(
        [recommendation],
        ["Python", "FastAPI"],
    )

    assert captured["title"] == "Python API endpoint"
    assert captured["body"] == "Build an endpoint using FastAPI."
    assert captured["labels"] == ["good first issue"]
    assert captured["user_skills"] == ["Python", "FastAPI"]



def test_enrich_recommendations_respects_ai_analysis_limit(monkeypatch):
    recommendations = [
        {
            "id": i,
            "title": f"Issue {i}",
            "body": "A Python issue.",
            "labels": [],
            "match_percentage": 80.0,
            "score": 20,
        }
        for i in range(12)
    ]

    analyzed_titles = []

    def mock_analyze_issue(**kwargs):
        analyzed_titles.append(kwargs["title"])
        return make_analysis(Difficulty.BEGINNER)

    monkeypatch.setattr(
        recommendation_service,
        "analyze_issue",
        mock_analyze_issue,
    )

    result = recommendation_service.enrich_recommendations(
        recommendations,
        ["Python"],
    )

    # Exactly 10 issues should receive AI analysis.
    assert len(analyzed_titles) == recommendation_service.AI_ANALYSIS_LIMIT

    # All 12 recommendations should be preserved.
    assert len(result) == 12

    # The first 10 should be analyzed.
    analyzed = [
        item for item in result
        if item["analysis_status"] == "analyzed"
    ]

    assert len(analyzed) == 10

    # The remaining 2 should not be analyzed.
    not_analyzed = [
        item for item in result
        if item["analysis_status"] == "not_analyzed"
    ]

    assert len(not_analyzed) == 2

    for item in not_analyzed:
        assert item["analysis"] is None
        assert item["hybrid_score"] is None


def test_all_recommendations_analyzed_when_below_limit(monkeypatch):
    recommendations = [
        {
            "title": f"Issue {i}",
            "body": "A Python issue.",
            "labels": [],
            "match_percentage": 80.0,
            "score": 20,
        }
        for i in range(3)
    ]

    analyzed_titles = []

    def mock_analyze_issue(**kwargs):
        analyzed_titles.append(kwargs["title"])
        return make_analysis(Difficulty.BEGINNER)

    monkeypatch.setattr(
        recommendation_service,
        "analyze_issue",
        mock_analyze_issue,
    )

    result = recommendation_service.enrich_recommendations(
        recommendations,
        ["Python"],
    )

    assert len(analyzed_titles) == 3
    assert len(result) == 3

    for item in result:
        assert item["analysis_status"] == "analyzed"
        assert item["analysis"] is not None
        assert item["hybrid_score"] is not None

