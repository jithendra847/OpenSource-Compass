import requests
import app as app_module
from fastapi.testclient import TestClient


client = TestClient(app_module.app)


def test_recommendations_success(monkeypatch):

    # Sample GitHub issue
    sample_issues = [
        {
            "id": 101,
            "title": "Fix Python authentication bug",
            "body": "Improve Python authentication handling.",
            "repository_url": "https://api.github.com/repos/example/project",
            "html_url": "https://github.com/example/project/issues/101",
            "labels": [
                {"name": "good first issue"}
            ]
        }
    ]

    # Replace the real GitHub API call with our sample data
    monkeypatch.setattr(
        app_module,
        "fetch_issues",
        lambda language, label, count: sample_issues
    )

    response = client.post(
        "/recommendations",
        json={
            "skills": ["Python"],
            "language": "python",
            "min_score": 10
        }
    )

    assert response.status_code == 200

    data = response.json()

    assert data["total"] == 1
    assert data["recommendations"][0]["title"] == "Fix Python authentication bug"
    assert data["recommendations"][0]["repository"] == "example/project"
    assert data["recommendations"][0]["score"] == 25
    recommendation = data["recommendations"][0]
    assert set(recommendation.keys()) == {
        "id",
        "title",
        "repository",
        "labels",
        "url",
        "title_matched_skills",
        "body_matched_skills",
        "score",
        "match_percentage",
        "explanation"
    }

    assert recommendation["id"] == 101
    assert recommendation["url"] == "https://github.com/example/project/issues/101"
    assert recommendation["labels"] == ["good first issue"]

    assert recommendation["title_matched_skills"] == ["Python"]
    assert recommendation["body_matched_skills"] == ["Python"]

    assert recommendation["match_percentage"] == 100.0
    assert recommendation["explanation"] == [
        "Python matched in title (+20)",
        "Good first issue label (+5)"
    ]

    assert data["total"] == len(data["recommendations"])

    assert isinstance(recommendation["score"], int)

    assert 0.0 <= recommendation["match_percentage"] <= 100.0

def test_recommendations_no_matching_skills(monkeypatch):

    sample_issues = [
        {
            "id": 102,
            "title": "Fix Java database connection",
            "body": "Improve Java backend performance.",
            "repository_url": "https://api.github.com/repos/example/java-project",
            "html_url": "https://github.com/example/java-project/issues/102",
            "labels": [
                {"name": "bug"}
            ]
        }
    ]

    monkeypatch.setattr(
        app_module,
        "fetch_issues",
        lambda language, label, count: sample_issues
    )

    response = client.post(
        "/recommendations",
        json={
            "skills": ["Python"],
            "language": "python",
            "min_score": 10
        }
    )

    assert response.status_code == 200

    data = response.json()

    assert data["total"] == 0
    assert data["recommendations"] == []
    assert data["total"] == len(data["recommendations"])


def test_recommendations_empty_skills():

    response = client.post(
        "/recommendations",
        json={
            "skills": [],
            "language": "python"
        }
    )

    assert response.status_code == 422


def test_recommendations_github_timeout(monkeypatch):

    def mock_fetch_issues(language, label, count):
        raise requests.exceptions.Timeout

    monkeypatch.setattr(
        app_module,
        "fetch_issues",
        mock_fetch_issues
    )

    response = client.post(
        "/recommendations",
        json={
            "skills": ["Python"],
            "language": "python"
        }
    )

    assert response.status_code == 503

    assert response.json()["detail"] == (
        "GitHub API request timed out. Please try again."
    )


#testing the github connection error 
def test_recommendations_github_connection_error(monkeypatch):

    def mock_fetch_issues(language, label, count):
        raise requests.exceptions.ConnectionError

    monkeypatch.setattr(
        app_module,
        "fetch_issues",
        mock_fetch_issues
    )

    response = client.post(
        "/recommendations",
        json={
            "skills": ["Python"],
            "language": "python"
        }
    )

    assert response.status_code == 503

    assert response.json()["detail"] == (
        "Unable to connect to GitHub. Check your connection."
    )

# testing the github HTTP errors

def test_recommendations_github_http_error(monkeypatch):

    def mock_fetch_issues(language, label, count):
        raise requests.exceptions.HTTPError

    monkeypatch.setattr(
        app_module,
        "fetch_issues",
        mock_fetch_issues
    )

    response = client.post(
        "/recommendations",
        json={
            "skills": ["Python"],
            "language": "python"
        }
    )

    assert response.status_code == 502

    assert response.json()["detail"] == (
        "GitHub returned an unsuccessful response."
    )

def test_home_endpoint():

    response = client.get("/")

    assert response.status_code == 200

    assert response.json() == {
        "message": "Welcome to OpenSource Compass API!",
        "status": "running"
    }


def test_search_preview_success():

    response = client.post(
        "/search-preview",
        json={
            "language": "python",
            "label": "good first issue",
            "count": 15
        }
    )

    assert response.status_code == 200

    data = response.json()

    assert data["message"] == (
        "Search parameters validated successfully!"
    )

    assert data["language"] == "python"
    assert data["label"] == "good first issue"
    assert data["count"] == 15


def test_search_preview_count_below_minimum():

    response = client.post(
        "/search-preview",
        json={
            "language": "python",
            "count": 0
        }
    )

    assert response.status_code == 422


def test_search_preview_count_above_maximum():

    response = client.post(
        "/search-preview",
        json={
            "language": "python",
            "count": 51
        }
    )

    assert response.status_code == 422


def test_get_issues_success(monkeypatch):

    sample_issues = [
        {
            "title": "Fix Python bug",
            "repository_url": "https://api.github.com/repos/example/project",
            "html_url": "https://github.com/example/project/issues/101",
            "labels": [
                {"name": "good first issue"},
                {"name": "bug"}
            ]
        }
    ]

    monkeypatch.setattr(
        app_module,
        "fetch_issues",
        lambda language, label, count: sample_issues
    )

    response = client.get(
        "/issues",
        params={
            "language": "python",
            "label": "good first issue",
            "count": 10
        }
    )

    assert response.status_code == 200

    data = response.json()

    assert data["total"] == 1

    assert data["issues"][0]["title"] == "Fix Python bug"

    assert data["issues"][0]["repository"] == "example/project"

    assert data["issues"][0]["labels"] == [
        "good first issue",
        "bug"
    ]


def test_get_issues_github_timeout(monkeypatch):

    def mock_fetch_issues(language, label, count):
        raise requests.exceptions.Timeout

    monkeypatch.setattr(
        app_module,
        "fetch_issues",
        mock_fetch_issues
    )

    response = client.get("/issues")

    assert response.status_code == 503

    assert response.json()["detail"] == (
        "GitHub API request timed out. Please try again."
    )


def test_get_issues_github_connection_error(monkeypatch):

    def mock_fetch_issues(language, label, count):
        raise requests.exceptions.ConnectionError

    monkeypatch.setattr(
        app_module,
        "fetch_issues",
        mock_fetch_issues
    )

    response = client.get("/issues")

    assert response.status_code == 503

    assert response.json()["detail"] == (
        "Unable to connect to GitHub. Check your connection."
    )


def test_get_issues_github_http_error(monkeypatch):

    def mock_fetch_issues(language, label, count):
        raise requests.exceptions.HTTPError

    monkeypatch.setattr(
        app_module,
        "fetch_issues",
        mock_fetch_issues
    )

    response = client.get("/issues")

    assert response.status_code == 502

    assert response.json()["detail"] == (
        "GitHub returned an unsuccessful response."
    )

def test_recommendations_minimum_score_filter(monkeypatch):

    sample_issues = [
        {
            "id": 103,
            "title": "Fix Python bug",
            "body": "A simple issue.",
            "repository_url": "https://api.github.com/repos/example/project",
            "html_url": "https://github.com/example/project/issues/103",
            "labels": []
        }
    ]

    monkeypatch.setattr(
        app_module,
        "fetch_issues",
        lambda language, label, count: sample_issues
    )

    response = client.post(
        "/recommendations",
        json={
            "skills": ["Python"],
            "language": "python",
            "min_score": 21
        }
    )

    assert response.status_code == 200

    data = response.json()

    assert data["total"] == 0
    assert data["recommendations"] == []
    assert data["total"] == len(data["recommendations"])