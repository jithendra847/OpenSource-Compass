
import json

from ai.llm_client import generate_structured, LLMResponseError
from models.repository_analysis import RepositoryAnalysis


MAX_FILES = 8
MAX_CHARS_PER_FILE = 6_000
MAX_TOTAL_SOURCE_CHARS = 30_000


SYSTEM_PROMPT = """
You are a senior open-source software engineer helping developers
understand and contribute to GitHub repositories.

Your task is to analyze a GitHub issue using the actual source code
provided in the prompt.

STRICT RULES:

1. Use only the supplied issue details and repository source files.
2. Never invent filenames, functions, classes, APIs, or code.
3. Every relevant_files.path must exactly match a supplied file path.
4. Every implementation_steps.file_path must be null or an exact
   supplied file path.
5. The evidence field must contain a short, exact code excerpt
   copied from the corresponding supplied source file.
6. Distinguish confirmed observations from hypotheses.
7. Do not claim to have identified the root cause unless the
   supplied source code establishes it.
8. If there is insufficient evidence, explain what needs
   further investigation.
9. Explain implementation steps in beginner-friendly language.
10. Make testing suggestions relevant to the supplied code.

Return only data matching the requested JSON structure.
"""


def prepare_source_files(files):
    """Limit source code included in the LLM prompt."""

    prepared_files = []
    total_chars = 0

    for file in files[:MAX_FILES]:
        path = file["path"]
        content = file["content"]

        remaining = MAX_TOTAL_SOURCE_CHARS - total_chars

        if remaining <= 0:
            break

        content = content[:min(MAX_CHARS_PER_FILE, remaining)]

        if not content.strip():
            continue

        prepared_files.append({
            "path": path,
            "content": content,
        })

        total_chars += len(content)

    return prepared_files


def analyze_repository_issue(
    title,
    body,
    labels,
    user_skills,
    repository_context,
):
    """
    Generate an evidence-based contribution guide
    using actual repository source code.
    """

    files = prepare_source_files(
        repository_context.get("files", [])
    )

    if not files:
        raise LLMResponseError(
            "No relevant repository source files were available "
            "for analysis."
        )

    repository_data = {
        "repository": repository_context["repository"],
        "default_branch": repository_context["default_branch"],
        "issue": {
            "title": title,
            "body": body or "",
            "labels": labels or [],
        },
        "developer_skills": user_skills or [],
        "source_files": files,
        "repository_tree_truncated": repository_context.get(
            "tree_truncated",
            False,
        ),
    }

    prompt = f"""
Analyze this GitHub issue using the supplied repository source code.

REPOSITORY CONTEXT:

{json.dumps(repository_data, indent=2)}

Return a detailed contribution guide with these fields:

- repository_summary:
  Explain what the repository or relevant component does.

- issue_interpretation:
  Explain the problem or requested feature in beginner-friendly terms.

- relevant_files:
  List the supplied files that matter. Explain their purpose and
  include an exact, short code excerpt as evidence.

- investigation_notes:
  Explain what a developer should inspect before making changes.

- implementation_steps:
  Give ordered, practical steps. Include the exact supplied file
  path when a change belongs in a retrieved file. Use null if the
  location cannot be determined.

- testing_strategy:
  Explain which tests should be run and what new tests may be needed.

- uncertainty_notes:
  Clearly state anything that cannot be confirmed from the supplied
  files. Mention if the repository file tree was truncated.

Be specific and educational. Explain what to change, how to change it,
and why the change is needed.
"""

    result = generate_structured(
        prompt=prompt,
        response_model=RepositoryAnalysis,
        system_prompt=SYSTEM_PROMPT,
    )

    # Validate that the AI did not invent repository file paths.
    available_paths = {
        file["path"] for file in files
    }

    for relevant_file in result.relevant_files:
        if relevant_file.path not in available_paths:
            raise LLMResponseError(
                "The AI returned a file path that was not retrieved "
                f"from GitHub: {relevant_file.path}"
            )

        # Evidence must actually occur in the supplied source file.
        source = next(
            file["content"]
            for file in files
            if file["path"] == relevant_file.path
        )

        if relevant_file.evidence not in source:
            raise LLMResponseError(
                "The AI returned source evidence that could not be "
                f"verified in {relevant_file.path}."
            )

    for step in result.implementation_steps:
        if (
            step.file_path is not None
            and step.file_path not in available_paths
        ):
            raise LLMResponseError(
                "The AI returned an implementation file path "
                f"that was not retrieved: {step.file_path}"
            )

    return result
