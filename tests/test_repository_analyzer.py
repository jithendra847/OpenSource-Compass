
import pytest

from ai import repository_analyzer
from ai.repository_analyzer import analyze_repository_issue
from ai.llm_client import LLMResponseError
from models.repository_analysis import (
    RepositoryAnalysis,
    RelevantFile,
    ImplementationStep,
)


@pytest.fixture
def repository_context():
    return {
        "repository": "example/project",
        "default_branch": "main",
        "tree_truncated": False,
        "files": [
            {
                "path": "src/authentication.py",
                "content": (
                    "def authenticate(token):\n"
                    "    return validate_token(token)\n"
                ),
            }
        ],
    }


def valid_analysis():
    return RepositoryAnalysis(
        repository_summary="Authentication module.",
        issue_interpretation="Fix token validation.",
        relevant_files=[
            RelevantFile(
                path="src/authentication.py",
                purpose="Handles authentication.",
                evidence="def authenticate(token):",
            )
        ],
        investigation_notes=["Inspect token validation."],
        implementation_steps=[
            ImplementationStep(
                step=1,
                file_path="src/authentication.py",
                instruction="Inspect the validation function.",
                reason="It handles authentication.",
            )
        ],
        testing_strategy=["Add invalid-token tests."],
        uncertainty_notes=[],
    )


def test_analyzer_accepts_valid_evidence(
    monkeypatch,
    repository_context,
):
    monkeypatch.setattr(
        repository_analyzer,
        "generate_structured",
        lambda **kwargs: valid_analysis(),
    )

    result = analyze_repository_issue(
        title="Fix authentication",
        body="Invalid tokens are accepted.",
        labels=["bug"],
        user_skills=["Python"],
        repository_context=repository_context,
    )

    assert result.repository_summary == "Authentication module."
    assert result.relevant_files[0].path == "src/authentication.py"


def test_analyzer_rejects_invented_file_path(
    monkeypatch,
    repository_context,
):
    result = valid_analysis()
    result.relevant_files[0].path = "src/fake.py"

    monkeypatch.setattr(
        repository_analyzer,
        "generate_structured",
        lambda **kwargs: result,
    )

    with pytest.raises(LLMResponseError, match="not retrieved"):
        analyze_repository_issue(
            "Fix authentication",
            "",
            [],
            ["Python"],
            repository_context,
        )


def test_analyzer_rejects_fabricated_evidence(
    monkeypatch,
    repository_context,
):
    result = valid_analysis()
    result.relevant_files[0].evidence = "def invented_function():"

    monkeypatch.setattr(
        repository_analyzer,
        "generate_structured",
        lambda **kwargs: result,
    )

    with pytest.raises(LLMResponseError, match="could not be verified"):
        analyze_repository_issue(
            "Fix authentication",
            "",
            [],
            ["Python"],
            repository_context,
        )


def test_analyzer_rejects_invented_implementation_path(
    monkeypatch,
    repository_context,
):
    result = valid_analysis()
    result.implementation_steps[0].file_path = "src/fake.py"

    monkeypatch.setattr(
        repository_analyzer,
        "generate_structured",
        lambda **kwargs: result,
    )

    with pytest.raises(LLMResponseError, match="not retrieved"):
        analyze_repository_issue(
            "Fix authentication",
            "",
            [],
            ["Python"],
            repository_context,
        )


def test_analyzer_rejects_empty_source_files(
    monkeypatch,
):
    context = {
        "repository": "example/project",
        "default_branch": "main",
        "files": [],
    }

    with pytest.raises(LLMResponseError, match="No relevant"):
        analyze_repository_issue(
            "Fix authentication",
            "",
            [],
            ["Python"],
            context,
        )
