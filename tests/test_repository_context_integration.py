
import repository_service
from ai.repository_context import fetch_repository_context


def test_fetch_repository_context(monkeypatch):
    monkeypatch.setattr(
        repository_service,
        "fetch_repository_metadata",
        lambda owner, repo: {"default_branch": "main"},
    )

    monkeypatch.setattr(
        repository_service,
        "fetch_repository_tree",
        lambda owner, repo, branch: {
            "tree": [
                {"path": "src/authentication.py", "type": "blob"},
                {"path": "src/database.py", "type": "blob"},
            ],
            "truncated": False,
        },
    )

    monkeypatch.setattr(
        repository_service,
        "fetch_source_file",
        lambda owner, repo, path: "def authenticate(): pass",
    )

    result = fetch_repository_context(
        "example",
        "project",
        "Fix authentication",
    )

    assert result["repository"] == "example/project"
    assert result["default_branch"] == "main"
    assert len(result["files"]) == 1
    assert result["files"][0]["path"] == "src/authentication.py"
    assert result["tree_truncated"] is False


def test_fetch_repository_context_without_default_branch(monkeypatch):
    monkeypatch.setattr(
        repository_service,
        "fetch_repository_metadata",
        lambda owner, repo: {},
    )

    try:
        fetch_repository_context(
            "example",
            "project",
            "Fix authentication",
        )
        assert False, "Expected ValueError"
    except ValueError as error:
        assert "default branch" in str(error)
