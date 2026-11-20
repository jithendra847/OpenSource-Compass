from recommendation_engine import (
    calculate_label_priority,
    recommend_issues,
    calculate_match_percentage,
    generate_explanation
)

def test_good_first_issue_priority():
    assert calculate_label_priority(
        ["good first issue"]
    ) == 3


def test_help_wanted_priority():
    assert calculate_label_priority(
        ["help wanted"]
    ) == 2


def test_up_for_grabs_priority():
    assert calculate_label_priority(
        ["up for grabs"]
    ) == 1


def test_unknown_label_priority():
    assert calculate_label_priority(
        ["bug"]
    ) == 0


def test_highest_priority_wins():
    assert calculate_label_priority(
        ["help wanted", "good first issue"]
    ) == 3


def test_recommend_issues_returns_matching_issue():
    issues = [
        {
            "id": 101,
            "title": "Python developer needed",
            "body": "Work with Python backend services",
            "html_url": "https://github.com/example/repo/issues/101",
            "repository_url": "https://api.github.com/repos/example/repo",
            "labels": [{"name": "good first issue"}]
        }
    ]

    result = recommend_issues(
        ["Python"],
        issues
    )

    assert len(result) == 1
    assert result[0]["id"] == 101
    assert result[0]["title_matched_skills"] == ["Python"]
    assert result[0]["body_matched_skills"] == ["Python"]


def test_minimum_score_filtering():
    issues = [
        {
            "id": 102,
            "title": "Python developer needed",
            "body": "",
            "labels": [],
        }
    ]

    result = recommend_issues(
        ["Python"],
        issues,
        min_score=30
    )

    assert result == []


def test_recommend_issues_sorted_by_score():
    issues = [
        {
            "id": 103,
            "title": "Python developer",
            "body": "",
            "labels": []
        },
        {
            "id": 104,
            "title": "JavaScript developer",
            "body": "",
            "labels": [{"name": "good first issue"}]
        }
    ]

    result = recommend_issues(
        ["Python", "JavaScript"],
        issues
    )

    assert result[0]["id"] == 104
    assert result[1]["id"] == 103


def test_empty_issues_list():
    result = recommend_issues(
        ["Python"],
        []
    )

    assert result == []


def test_no_matching_skills():
    issues = [
        {
            "id": 105,
            "title": "Frontend developer needed",
            "body": "Work with HTML and CSS",
            "labels": []
        }
    ]

    result = recommend_issues(
        ["Python"],
        issues
    )

    assert result == []


def test_more_matched_skills_get_higher_rank():
    issues = [
        {
            "id": 201,
            "title": "Python developer",
            "body": "",
            "labels": []
        },
        {
            "id": 202,
            "title": "Python JavaScript developer",
            "body": "",
            "labels": []
        }
    ]

    result = recommend_issues(
        ["Python", "JavaScript"],
        issues
    )

    assert result[0]["id"] == 202


def test_label_priority_breaks_tie():
    issues = [
        {
            "id": 203,
            "title": "Python developer",
            "body": "",
            "labels": [{"name": "help wanted"}]
        },
        {
            "id": 204,
            "title": "Python developer",
            "body": "",
            "labels": [{"name": "good first issue"}]
        }
    ]

    result = recommend_issues(
        ["Python"],
        issues
    )

    assert result[0]["id"] == 204


def test_missing_title_and_body():
    issues = [
        {
            "id": 301,
            "labels": [],
        }
    ]

    result = recommend_issues(
        ["Python"],
        issues
    )

    assert result == []


def test_multiple_labels():
    issues = [
        {
            "id": 302,
            "title": "Python developer",
            "body": "",
            "labels": [
                {"name": "help wanted"},
                {"name": "good first issue"}
            ]
        }
    ]

    result = recommend_issues(
        ["Python"],
        issues
    )

    assert len(result) == 1
    assert result[0]["labels"] == [
        "help wanted",
        "good first issue"
    ]


def test_empty_developer_skills():
    issues = [
        {
            "id": 303,
            "title": "Python developer",
            "body": "",
            "labels": []
        }
    ]

    result = recommend_issues(
        [],
        issues
    )

    assert result == []

def test_empty_skills_match_percentage():
    result = calculate_match_percentage(
        [],
        [],
        []
    )

    assert result == 0.0


def test_up_for_grabs_adds_score():
    issues = [
        {
            "id": 401,
            "title": "Python developer",
            "body": "",
            "labels": [{"name": "up for grabs"}]
        }
    ]

    result = recommend_issues(
        ["Python"],
        issues
    )

    assert len(result) == 1
    assert result[0]["score"] == 22

def test_generate_explanation():
    explanation = generate_explanation(
        title_matched_skills=["Python"],
        body_matched_skills=["Python", "FastAPI"],
        issue_labels=["good first issue", "help wanted"]
    )

    assert "Python matched in title (+20)" in explanation
    assert "FastAPI matched in description (+8)" in explanation
    assert "Good first issue label (+5)" in explanation
    assert "Help wanted label (+3)" in explanation
    assert len(explanation) == 4


def test_generate_explanation_no_matches():
    explanation = generate_explanation(
        title_matched_skills=[],
        body_matched_skills=[],
        issue_labels=[]
    )

    assert explanation == []

def test_newer_issue_breaks_tie():
    issues = [
        {
            "id": 101,
            "title": "Python bug fix",
            "body": "Fix a bug in Python",
            "labels": [{"name": "good first issue"}],
            "created_at": "2026-11-15T10:00:00Z"
        },
        {
            "id": 102,
            "title": "Python bug fix",
            "body": "Fix a bug in Python",
            "labels": [{"name": "good first issue"}],
            "created_at": "2026-11-19T10:00:00Z"
        }
    ]

    results = recommend_issues(
        developer_skills=["Python"],
        issues=issues
    )

    assert results[0]["id"] == 102
    assert results[1]["id"] == 101