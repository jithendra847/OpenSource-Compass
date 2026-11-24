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

    # Mock AI enrichment to avoid real AI/API calls
    # Mock AI enrichment to avoid real AI/API calls
    def mock_enrich_recommendations(recommendations, user_skills):

        enriched = []

        for recommendation in recommendations:
            enriched.append({
                **recommendation,
                "hybrid_score": 92.0,
                "analysis_status": "analyzed",
                "analysis": {
                    "difficulty": "Beginner",
                    "difficulty_reason": "A straightforward issue.",
                    "required_skills": ["Python"],
                    "summary": "Fix a Python authentication bug.",
                    "suitability": {
                        "fit_score": 90,
                        "suitable": True,
                        "matched_skills": ["Python"],
                        "missing_skills": [],
                        "recommendation": "Ready to try",
                        "reason": "Your skills match the issue.",
                        "preparation_skills": []
                    }
                }
            })

        return enriched

    monkeypatch.setattr(
        app_module,
        "enrich_recommendations",
        mock_enrich_recommendations
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
        "explanation",
        "hybrid_score",
        "analysis",
        "analysis_status"
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

    assert recommendation["hybrid_score"] == 92.0

    assert recommendation["analysis"]["difficulty"] == "Beginner"
    assert recommendation["analysis"]["required_skills"] == ["Python"]
    assert recommendation["analysis"]["suitability"]["fit_score"] == 90
    assert recommendation["analysis_status"] == "analyzed"

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


def test_recommendations_github_request_error(monkeypatch):

    def mock_fetch_issues(language, label, count):
        raise requests.exceptions.RequestException("GitHub request failed")

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
        "GitHub request failed. Please try again."
    )


def test_get_issues_github_request_error(monkeypatch):

    def mock_fetch_issues(language, label, count):
        raise requests.exceptions.RequestException("GitHub request failed")

    monkeypatch.setattr(
        app_module,
        "fetch_issues",
        mock_fetch_issues
    )

    response = client.get("/issues")

    assert response.status_code == 502
    assert response.json()["detail"] == (
        "GitHub request failed. Please try again."
    )


def test_get_issues_count_below_minimum():
    response = client.get("/issues", params={"count": 0})
    assert response.status_code == 422


def test_get_issues_count_above_maximum():
    response = client.get("/issues", params={"count": 51})
    assert response.status_code == 422


def test_recommendations_count_below_minimum():
    response = client.post(
        "/recommendations",
        json={"skills": ["Python"], "count": 0}
    )
    assert response.status_code == 422


def test_recommendations_count_above_maximum():
    response = client.post(
        "/recommendations",
        json={"skills": ["Python"], "count": 51}
    )
    assert response.status_code == 422


def test_recommendations_negative_min_score():
    response = client.post(
        "/recommendations",
        json={"skills": ["Python"], "min_score": -1}
    )
    assert response.status_code == 422


def test_get_issues_empty_language():
    response = client.get("/issues", params={"language": ""})
    assert response.status_code == 422


def test_recommendations_empty_language():
    response = client.post(
        "/recommendations",
        json={
            "skills": ["Python"],
            "language": ""
        }
    )

    assert response.status_code == 422

# --------------------------------
# M6.5 - API DOCUMENTATION TESTS
# --------------------------------

def test_openapi_api_metadata():
    response = client.get("/openapi.json")

    assert response.status_code == 200

    data = response.json()

    assert data["info"]["title"] == "OpenSource Compass API"
    assert data["info"]["version"] == "0.1.0"
    assert "beginner-friendly open-source issues" in data["info"]["description"]


def test_openapi_endpoint_tags():
    response = client.get("/openapi.json")
    data = response.json()

    assert data["paths"]["/"]["get"]["tags"] == ["General"]
    assert data["paths"]["/issues"]["get"]["tags"] == ["Issues"]
    assert data["paths"]["/search-preview"]["post"]["tags"] == ["Issues"]
    assert data["paths"]["/recommendations"]["post"]["tags"] == [
        "Recommendations"
    ]
    assert data["paths"]["/analyze-issue"]["post"]["tags"] == [
    "Analysis"
]


def test_openapi_endpoint_documentation():
    response = client.get("/openapi.json")
    data = response.json()

    endpoints = [
        data["paths"]["/"]["get"],
        data["paths"]["/issues"]["get"],
        data["paths"]["/search-preview"]["post"],
        data["paths"]["/recommendations"]["post"]
    ]

    for endpoint in endpoints:
        assert endpoint["summary"]
        assert endpoint["description"]


def test_openapi_request_model_documentation():
    response = client.get("/openapi.json")
    data = response.json()

    schemas = data["components"]["schemas"]

    recommendation_schema = schemas["RecommendationRequest"]["properties"]

    assert recommendation_schema["skills"]["minItems"] == 1
    assert recommendation_schema["skills"]["description"]

    assert recommendation_schema["count"]["minimum"] == 1
    assert recommendation_schema["count"]["maximum"] == 50

    assert recommendation_schema["min_score"]["minimum"] == 0
    assert recommendation_schema["min_score"]["description"]

    issue_search_schema = schemas["IssueSearch"]["properties"]

    assert issue_search_schema["count"]["minimum"] == 1
    assert issue_search_schema["count"]["maximum"] == 50
    assert issue_search_schema["language"]["description"]

    issue_analysis_schema = schemas["IssueAnalysisRequest"]["properties"]

    assert issue_analysis_schema["title"]["minLength"] == 1
    assert issue_analysis_schema["title"]["description"]

    assert issue_analysis_schema["body"]["description"]
    assert issue_analysis_schema["labels"]["description"]
    assert issue_analysis_schema["user_skills"]["description"]

        # Verify IssueAnalysis response schema
    analysis_schema = schemas["IssueAnalysis"]["properties"]

    assert "difficulty" in analysis_schema
    assert "difficulty_reason" in analysis_schema
    assert "required_skills" in analysis_schema
    assert "summary" in analysis_schema
    assert "suitability" in analysis_schema

    # Verify suitability response schema
    suitability_schema = schemas["SuitabilityAnalysis"]["properties"]

    assert "fit_score" in suitability_schema
    assert "matched_skills" in suitability_schema
    assert "missing_skills" in suitability_schema
    assert "recommendation" in suitability_schema
    assert "preparation_skills" in suitability_schema


# --------------------------------
# M8.9 - ISSUE ANALYSIS API TESTS
# --------------------------------

def test_analyze_issue_success(monkeypatch):

    def mock_analyze_issue(title, body, labels, user_skills):
        return {
            "difficulty": "Beginner",
            "difficulty_reason": "A straightforward issue.",
            "required_skills": ["Python"],
            "summary": "Fix a Python authentication bug.",
            "suitability": {
                "fit_score": 90,
                "suitable": True,
                "matched_skills": ["Python"],
                "missing_skills": [],
                "recommendation": "Ready to try",
                "reason": "Your skills match the issue.",
                "preparation_skills": []
            }
        }

    monkeypatch.setattr(
        app_module,
        "analyze_issue",
        mock_analyze_issue
    )

    response = client.post(
        "/analyze-issue",
        json={
            "title": "Fix Python authentication bug",
            "body": "Improve authentication handling.",
            "labels": ["good first issue"],
            "user_skills": ["Python"]
        }
    )

    assert response.status_code == 200

    data = response.json()

    assert data["difficulty"] == "Beginner"
    assert data["required_skills"] == ["Python"]
    assert data["summary"] == "Fix a Python authentication bug."
    assert data["suitability"]["fit_score"] == 90
    assert data["suitability"]["recommendation"] == "Ready to try"

def test_analyze_issue_empty_title():

    response = client.post(
        "/analyze-issue",
        json={
            "title": "",
            "body": "Some issue description.",
            "labels": ["bug"],
            "user_skills": ["Python"]
        }
    )

    assert response.status_code == 422