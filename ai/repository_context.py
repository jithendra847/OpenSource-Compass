
import re
from pathlib import PurePosixPath
import repository_service


MAX_SELECTED_FILES = 8

SOURCE_EXTENSIONS = {
    ".py",
    ".js",
    ".jsx",
    ".ts",
    ".tsx",
    ".java",
    ".cpp",
    ".c",
    ".h",
    ".go",
    ".rs",
    ".php",
    ".rb",
    ".cs",
    ".vue",
    ".sql",
}

TEST_KEYWORDS = {
    "test",
    "tests",
    "testing",
    "spec",
    "specs",
}


IGNORED_DIRECTORIES = {
    "node_modules",
    "vendor",
    "dist",
    "build",
    "__pycache__",
    ".git",
    ".venv",
    "venv",
    "coverage",
}


STOP_WORDS = {
    "the", "and", "for", "with", "from",
    "this", "that", "into", "when", "where",
    "what", "which", "have", "has", "should",
    "could", "would", "will", "your", "their",
    "there", "then", "than", "been", "being",
    "are", "was", "were", "not", "but",
    "issue", "fix", "bug", "feature",
}


def extract_keywords(text):
    """Extract useful technical keywords from issue text."""

    words = re.findall(r"[a-zA-Z][a-zA-Z0-9_+-]*", text.lower())

    return {
        word
        for word in words
        if len(word) > 2 and word not in STOP_WORDS
    }


def calculate_file_score(file_path, issue_keywords, issue_text):
    """Calculate how relevant a repository file is to an issue."""

    path = PurePosixPath(file_path)

    filename = path.stem.lower()
    directory_parts = {
        part.lower()
        for part in path.parts[:-1]
    }

    filename_keywords = extract_keywords(
    filename.replace("_", " ").replace("-", " ")
)

    score = 0

    # Filename matches are strong evidence of relevance.
    for keyword in issue_keywords:
        if keyword in filename_keywords:
            score += 10

    # Directory matches indicate relevant modules.
    for keyword in issue_keywords:
       if keyword in directory_parts:
        score += 6

    # Ignore files without a filename or directory keyword match.
    if score == 0:
        return 0

    if path.suffix.lower() in SOURCE_EXTENSIONS:
        score += 4
    else:
        return 0

    # Give test files extra relevance when testing is mentioned.
    mentions_testing = any(
        word in issue_text.lower()
        for word in ("test", "testing", "spec", "regression")
    )

    is_test_file = any(
        part in TEST_KEYWORDS
        or part.startswith("test_")
        or part.endswith("_test")
        for part in path.parts
    )

    if mentions_testing and is_test_file:
        score += 8

    return score


def select_relevant_files(
    file_tree,
    issue_title,
    issue_body="",
    max_files=MAX_SELECTED_FILES,
):
    """
    Rank repository source files against an issue
    and return the most relevant file paths.
    """

    issue_text = f"{issue_title} {issue_body}"

    issue_keywords = extract_keywords(issue_text)

    candidates = []

    for item in file_tree:

        if item.get("type") != "blob":
            continue

        file_path = item.get("path", "")

        if not file_path:
            continue

        path = PurePosixPath(file_path)

        # Ignore generated, dependency and environment folders.
        if any(
            part.lower() in IGNORED_DIRECTORIES
            for part in path.parts
        ):
            continue

        score = calculate_file_score(
            file_path,
            issue_keywords,
            issue_text,
        )

        if score > 0:
            candidates.append((score, file_path))

    # Higher scores first; alphabetical order breaks ties.
    candidates.sort(
        key=lambda item: (-item[0], item[1].lower())
    )

    return [
        file_path
        for score, file_path in candidates[:max_files]
    ]

def fetch_repository_context(
    owner,
    repo,
    issue_title,
    issue_body="",
):
    """
    Fetch relevant source code from a GitHub repository
    for analyzing a particular issue.
    """

    # Step 1: Get repository metadata
    metadata = repository_service.fetch_repository_metadata(
        owner,
        repo,
    )

    default_branch = metadata.get("default_branch")

    if not default_branch:
        raise ValueError("Repository has no default branch.")

    # Step 2: Get the repository file tree
    tree_data = repository_service.fetch_repository_tree(
        owner,
        repo,
        default_branch,
    )

    file_tree = tree_data["tree"]

    # Step 3: Select files relevant to the issue
    selected_paths = select_relevant_files(
        file_tree,
        issue_title,
        issue_body,
    )

    # Step 4: Fetch the actual source code
    files = []

    for path in selected_paths:
        content = repository_service.fetch_source_file(
            owner,
            repo,
            path,
        )

        if content is None:
            continue

        files.append({
            "path": path,
            "content": content,
        })

    return {
        "repository": f"{owner}/{repo}",
        "default_branch": default_branch,
        "files": files,
        "tree_truncated": tree_data["truncated"],
    }