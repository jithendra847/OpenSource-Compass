
from models.analysis import Difficulty, Recommendation, SuitabilityAnalysis


def analyze_suitability(
    user_skills: list[str],
    required_skills: list[str],
    difficulty: Difficulty,
) -> SuitabilityAnalysis:
    """Evaluate how suitable a GitHub issue is for a user."""

    # Convert the user's skills to lowercase for comparison
    user_skill_set = {skill.strip().lower() for skill in user_skills}

    # Identify skills the user already knows
    matched_skills = [
        skill for skill in required_skills
        if skill.strip().lower() in user_skill_set
    ]

    # Identify skills the user is missing
    missing_skills = [
        skill for skill in required_skills
        if skill.strip().lower() not in user_skill_set
    ]

    total_required = len(required_skills)

    # Handle issues where no required skills were identified
    if total_required == 0:
        return SuitabilityAnalysis(
            fit_score=0,
            suitable=False,
            matched_skills=[],
            missing_skills=[],
            recommendation=Recommendation.PREPARE,
            reason=(
                "No required skills could be identified. "
                "Review the issue manually before deciding."
            ),
            preparation_skills=[],
        )

    # Calculate skill coverage percentage
    fit_score = round((len(matched_skills) / total_required) * 100)

    # Advanced issues require extra caution
    if difficulty == Difficulty.ADVANCED:
        if fit_score >= 80:
            recommendation = Recommendation.PREPARE
            reason = (
                "You match most required skills, but the issue is advanced. "
                "Review its technical complexity before attempting it."
            )
        else:
            recommendation = Recommendation.STRETCH
            reason = (
                "This is an advanced issue and you have some skill gaps. "
                "Build the missing skills before attempting it."
            )

    # Strong skill match
    elif fit_score >= 80:
        recommendation = Recommendation.READY
        reason = (
            "You have a strong match with the required skills. "
            "You can likely attempt this issue."
        )

    # Partial skill match
    elif fit_score >= 50:
        recommendation = Recommendation.PREPARE
        reason = (
            "You have a partial skill match. Review the missing skills "
            "before starting this issue."
        )

    # Low skill match
    else:
        recommendation = Recommendation.STRETCH
        reason = (
            "You are missing several required skills. "
            "Learn the fundamentals before attempting this issue."
        )

    # Decide if the issue is currently suitable to attempt
    suitable = (
        fit_score >= 70
        and difficulty != Difficulty.ADVANCED
    )

    # Build and return the final analysis
    return SuitabilityAnalysis(
        fit_score=fit_score,
        suitable=suitable,
        matched_skills=matched_skills,
        missing_skills=missing_skills,
        recommendation=recommendation,
        reason=reason,
        preparation_skills=missing_skills,
    )
