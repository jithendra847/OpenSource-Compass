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
