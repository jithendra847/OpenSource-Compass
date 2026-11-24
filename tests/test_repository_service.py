
import base64

import repository_service


class MockResponse:
    def __init__(self, data):
        self.data = data

    def json(self):
        return self.data

    def raise_for_status(self):
        pass


def test_github_headers_without_token(monkeypatch):
    monkeypatch.delenv("GITHUB_TOKEN", raising=False)

    headers = repository_service.get_github_headers()

    assert headers["Accept"] == "application/vnd.github+json"
    assert "Authorization" not in headers


def test_github_headers_with_token(monkeypatch):
    monkeypatch.setenv("GITHUB_TOKEN", "test-token")

    headers = repository_service.get_github_headers()

    assert headers["Authorization"] == "Bearer test-token"


def test_fetch_repository_metadata(monkeypatch):
    def mock_get(url, **kwargs):
        assert url.endswith("/repos/example/project")
        return MockResponse({
            "default_branch": "main",
            "full_name": "example/project",
        })

    monkeypatch.setattr(repository_service.requests, "get", mock_get)

    result = repository_service.fetch_repository_metadata(
        "example",
        "project",
    )

    assert result["default_branch"] == "main"


def test_fetch_repository_tree(monkeypatch):
    def mock_get(url, **kwargs):
        assert url.endswith("/git/trees/main")
        assert kwargs["params"] == {"recursive": "1"}

        return MockResponse({
            "tree": [
                {"path": "src/main.py", "type": "blob"},
                {"path": "README.md", "type": "blob"},
            ],
            "truncated": False,
        })

    monkeypatch.setattr(repository_service.requests, "get", mock_get)

    result = repository_service.fetch_repository_tree(
        "example",
        "project",
        "main",
    )

    assert len(result["tree"]) == 2
    assert result["truncated"] is False


def test_fetch_source_file(monkeypatch):
    source = "def hello():\n    return 'Hello world'"

    encoded = base64.b64encode(
        source.encode("utf-8")
    ).decode("utf-8")

    def mock_get(url, **kwargs):
        assert url.endswith("/contents/src/main.py")

        return MockResponse({
            "type": "file",
            "size": len(source),
            "encoding": "base64",
            "content": encoded,
        })

    monkeypatch.setattr(repository_service.requests, "get", mock_get)

    result = repository_service.fetch_source_file(
        "example",
        "project",
        "src/main.py",
    )

    assert result == source


def test_fetch_source_file_rejects_large_file(monkeypatch):
    def mock_get(url, **kwargs):
        return MockResponse({
            "type": "file",
            "size": 150_000,
            "encoding": "base64",
            "content": "",
        })

    monkeypatch.setattr(repository_service.requests, "get", mock_get)

    result = repository_service.fetch_source_file(
        "example",
        "project",
        "large.py",
    )

    assert result is None


def test_fetch_source_file_rejects_non_file(monkeypatch):
    def mock_get(url, **kwargs):
        return MockResponse({
            "type": "dir",
            "size": 0,
        })

    monkeypatch.setattr(repository_service.requests, "get", mock_get)

    result = repository_service.fetch_source_file(
        "example",
        "project",
        "src",
    )

    assert result is None
