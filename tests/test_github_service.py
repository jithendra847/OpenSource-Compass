
from unittest.mock import Mock

import github_service


def test_fetch_issues_success(monkeypatch):

    # Sample issues returned by GitHub
    sample_issues = [
        {
            "id": 101,
            "title": "Fix Python authentication bug"
        },
        {
            "id": 102,
            "title": "Improve Python documentation"
        }
    ]

    # Create a fake GitHub response
    mock_response = Mock()

    mock_response.json.return_value = {
        "items": sample_issues
    }

    mock_response.headers = {}

    # Replace the real HTTP request with a mock
    monkeypatch.setattr(
        github_service.requests,
        "get",
        lambda *args, **kwargs: mock_response
    )

    # Call the actual service function
    result = github_service.fetch_issues(
        language="python",
        label="good first issue",
        count=10
    )

    # Verify the returned issues
    assert result == sample_issues


def test_fetch_issues_request_parameters(monkeypatch):

    mock_response = Mock()

    mock_response.json.return_value = {
        "items": []
    }

    mock_response.headers = {}

    # Capture the arguments passed to requests.get()
    def mock_get(url, params, headers, timeout):

        assert url == "https://api.github.com/search/issues"

        assert params == {
            "q": 'is:issue is:open language:python label:"good first issue"',
            "per_page": 10,
            "sort": "updated",
            "order": "desc"
        }

        assert headers == {
            "Accept": "application/vnd.github+json"
        }

        assert timeout == 15

        return mock_response

    monkeypatch.setattr(
        github_service.requests,
        "get",
        mock_get
    )

    result = github_service.fetch_issues(
        language="python",
        label="good first issue",
        count=10
    )

    assert result == []


def test_fetch_issues_without_label(monkeypatch):

    mock_response = Mock()

    mock_response.json.return_value = {
        "items": []
    }

    mock_response.headers = {}

    def mock_get(url, params, headers, timeout):

        assert params["q"] == (
            "is:issue is:open language:python"
        )

        return mock_response

    monkeypatch.setattr(
        github_service.requests,
        "get",
        mock_get
    )

    result = github_service.fetch_issues(
        language="python",
        label=None,
        count=10
    )

    assert result == []


def test_fetch_issues_without_label(monkeypatch):

    mock_response = Mock()

    mock_response.json.return_value = {
        "items": []
    }

    mock_response.headers = {}

    def mock_get(url, params, headers, timeout):

        assert params["q"] == (
            "is:issue is:open language:python"
        )

        return mock_response

    monkeypatch.setattr(
        github_service.requests,
        "get",
        mock_get
    )

    result = github_service.fetch_issues(
        language="python",
        label=None,
        count=10
    )

    assert result == []
