from ai.analyzer import analyze_difficulty
from models.analysis import Difficulty


def test_documentation_issue_is_beginner():
    result = analyze_difficulty("Fix documentation typo")
    assert result.difficulty == Difficulty.BEGINNER


def test_beginner_label_supports_beginner_classification():
    result = analyze_difficulty("Update a small example", labels=["good first issue"])
    assert result.difficulty == Difficulty.BEGINNER


def test_single_api_task_is_intermediate():
    result = analyze_difficulty("Implement API endpoint")
    assert result.difficulty == Difficulty.INTERMEDIATE


def test_multiple_technical_indicators_are_intermediate():
    result = analyze_difficulty("Implement API integration")
    assert result.difficulty == Difficulty.INTERMEDIATE


def test_multiple_complexity_indicators_are_advanced():
    result = analyze_difficulty(
        "Redesign distributed architecture with concurrency"
    )
    assert result.difficulty == Difficulty.ADVANCED


def test_security_architecture_issue_is_advanced():
    result = analyze_difficulty("Improve security architecture")
    assert result.difficulty == Difficulty.ADVANCED


def test_body_content_is_analyzed():
    result = analyze_difficulty(
        "Improve system",
        body="Implement database integration and performance testing."
    )
    assert result.difficulty == Difficulty.ADVANCED


def test_labels_are_case_insensitive():
    result = analyze_difficulty("Update example", labels=["GOOD FIRST ISSUE"])
    assert result.difficulty == Difficulty.BEGINNER


def test_unknown_issue_gets_tentative_beginner_estimate():
    result = analyze_difficulty("Update the project")
    assert result.difficulty == Difficulty.BEGINNER
    assert "tentative" in result.reason.lower()


def test_reason_is_always_provided():
    result = analyze_difficulty("Fix documentation typo")
    assert result.reason.strip() != ""
