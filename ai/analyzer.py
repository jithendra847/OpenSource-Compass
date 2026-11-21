from models.analysis import Difficulty, DifficultyAnalysis


ADVANCED_KEYWORDS = {
    "architecture",
    "distributed",
    "concurrency",
    "security",
    "scalability",
    "migration",
    "redesign",
    "deadlock",
}

INTERMEDIATE_KEYWORDS = {
    "implement",
    "integration",
    "refactor",
    "database",
    "authentication",
    "endpoint",
    "api",
    "debug",
    "performance",
    "testing",
}

BEGINNER_KEYWORDS = {
    "documentation",
    "docs",
    "typo",
    "simple",
    "beginner",
    "small",
    "good first issue",
}


def analyze_difficulty(title: str, body: str = "", labels: list[str] | None = None) -> DifficultyAnalysis:
    """Estimate issue difficulty using keyword-based rules (baseline, not AI)."""

    text = f"{title} {body}".lower()
    label_text = " ".join(labels or []).lower()

    advanced_matches = sorted(
        keyword for keyword in ADVANCED_KEYWORDS if keyword in text
    )
    intermediate_matches = sorted(
        keyword for keyword in INTERMEDIATE_KEYWORDS if keyword in text
    )
    beginner_matches = sorted(
        keyword for keyword in BEGINNER_KEYWORDS
        if keyword in text or keyword in label_text
    )

    if len(advanced_matches) >= 2 or len(intermediate_matches) >= 4:
        difficulty = Difficulty.ADVANCED
        evidence = advanced_matches + intermediate_matches
        reason = (
            "The issue contains multiple higher-complexity indicators: "
            + ", ".join(evidence)
            + "."
        )

    elif advanced_matches or len(intermediate_matches) >= 2:
        difficulty = Difficulty.INTERMEDIATE
        evidence = advanced_matches + intermediate_matches
        reason = (
            "The issue contains technical complexity indicators: "
            + ", ".join(evidence)
            + "."
        )

    elif intermediate_matches:
        difficulty = Difficulty.INTERMEDIATE
        reason = (
            "The issue involves a technical task: "
            + ", ".join(intermediate_matches)
            + "."
        )

    elif beginner_matches:
        difficulty = Difficulty.BEGINNER
        reason = (
            "The issue contains beginner-friendly indicators: "
            + ", ".join(beginner_matches)
            + "."
        )

    else:
        difficulty = Difficulty.BEGINNER
        reason = (
            "No strong complexity indicators were found. "
            "This is a tentative beginner estimate and needs review."
        )

    return DifficultyAnalysis(difficulty=difficulty, reason=reason)
