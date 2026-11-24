from ai.issue_analyzer import analyze_issue
from models.analysis import IssueSummary


def test_issue_analyzer_integrates_all_components(monkeypatch):
    # Arrange
    ai_summary = IssueSummary(
        summary="Add validation to prevent API crashes on empty email inputs."
    )

    def mock_generate_structured(*args, **kwargs):
        return ai_summary

    monkeypatch.setattr(
        "ai.summarizer.generate_structured",
        mock_generate_structured,
    )

    title = "Fix crash when email is empty"
    body = (
        "The API crashes when users submit an empty email. "
        "Add validation and return a proper error response."
    )

    # Act
    result = analyze_issue(
        title=title,
        body=body,
        labels=["bug"],
        user_skills=["Python", "FastAPI"],
    )

    # Assert
    assert result.summary == ai_summary.summary
    assert result.difficulty is not None
    assert result.difficulty_reason
    assert isinstance(result.required_skills, list)
    assert result.suitability is not None