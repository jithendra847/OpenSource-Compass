from ai.analyzer import analyze_difficulty
from ai.skill_extractor import extract_required_skills
from ai.summarizer import summarize_issue
from ai.suitability import analyze_suitability

from models.analysis import IssueAnalysis


def analyze_issue(
    title: str,
    body: str = "",
    labels: list[str] | None = None,
    user_skills: list[str] | None = None,
) -> IssueAnalysis:
    """Perform a complete analysis of a GitHub issue."""

    labels = labels or []
    user_skills = user_skills or []

    # 1. Analyze issue difficulty
    difficulty_result = analyze_difficulty(
        title, body, labels
    )

    # 2. Extract required skills
    required_skills = extract_required_skills(
        title, body, labels
    )

    # 3. Generate a beginner-friendly summary
    summary_result = summarize_issue(
        title, body
    )

    # 4. Evaluate suitability for the user
    suitability_result = analyze_suitability(
        user_skills,
        required_skills,
        difficulty_result.difficulty,
    )

    # 5. Combine all results into one response
    return IssueAnalysis(
        difficulty=difficulty_result.difficulty,
        difficulty_reason=difficulty_result.reason,
        required_skills=required_skills,
        summary=summary_result.summary,
        suitability=suitability_result,
    )