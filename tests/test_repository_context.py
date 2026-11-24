
from ai.repository_context import (
    extract_keywords,
    calculate_file_score,
    select_relevant_files,
)


def test_extract_keywords():
    keywords = extract_keywords(
        "Fix authentication token validation"
    )

    assert "authentication" in keywords
    assert "token" in keywords
    assert "validation" in keywords
    assert "fix" not in keywords


def test_filename_match_gets_higher_score():
    keywords = {"authentication"}

    relevant_score = calculate_file_score(
        "src/authentication.py",
        keywords,
        "authentication issue",
    )

    unrelated_score = calculate_file_score(
        "src/database.py",
        keywords,
        "authentication issue",
    )

    assert relevant_score > unrelated_score


def test_directory_match_is_considered():
    keywords = {"authentication"}

    score = calculate_file_score(
        "src/authentication/service.py",
        keywords,
        "authentication issue",
    )

    assert score > 0


def test_test_files_get_priority_when_testing_is_mentioned():
    keywords = {"authentication"}

    score = calculate_file_score(
        "tests/test_authentication.py",
        keywords,
        "authentication regression test",
    )

    assert score > 0


def test_ignored_directories_are_excluded():
    tree = [
        {"path": "src/authentication.py", "type": "blob"},
        {
            "path": "node_modules/authentication.js",
            "type": "blob",
        },
    ]

    result = select_relevant_files(
        tree,
        "Fix authentication",
    )

    assert "src/authentication.py" in result
    assert "node_modules/authentication.js" not in result


def test_only_source_files_are_selected():
    tree = [
        {"path": "README.md", "type": "blob"},
        {"path": "src/authentication.py", "type": "blob"},
    ]

    result = select_relevant_files(
        tree,
        "Fix authentication",
    )

    assert "README.md" not in result
    assert "src/authentication.py" in result


def test_maximum_file_limit():
    tree = [
        {
            "path": f"src/authentication_{i}.py",
            "type": "blob",
        }
        for i in range(20)
    ]

    result = select_relevant_files(
        tree,
        "Fix authentication",
        max_files=5,
    )

    assert len(result) == 5


def test_directories_are_not_selected():
    tree = [
        {"path": "src/authentication", "type": "tree"},
        {"path": "src/authentication.py", "type": "blob"},
    ]

    result = select_relevant_files(
        tree,
        "Fix authentication",
    )

    assert "src/authentication" not in result
    assert "src/authentication.py" in result
