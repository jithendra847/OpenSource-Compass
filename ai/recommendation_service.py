
from ai.issue_analyzer import analyze_issue
from ai.ranking import calculate_hybrid_score


# Maximum number of recommendations to send for AI analysis.
AI_ANALYSIS_LIMIT = 10


def enrich_recommendations(
    recommendations: list[dict],
    user_skills: list[str],
) -> list[dict]:
    """Apply AI analysis to a limited number of recommendations."""

    # Select only the top-ranked recommendations for AI analysis.
    recommendations_to_analyze = recommendations[:AI_ANALYSIS_LIMIT]

    # Keep the remaining recommendations without AI analysis.
    recommendations_without_analysis = recommendations[AI_ANALYSIS_LIMIT:]

    enriched = []

    for recommendation in recommendations_to_analyze:
        analysis = analyze_issue(
            title=recommendation["title"],
            body=recommendation.get("body", ""),
            labels=recommendation["labels"],
            user_skills=user_skills,
        )

        hybrid_score = calculate_hybrid_score(
            match_percentage=recommendation["match_percentage"],
            fit_score=analysis.suitability.fit_score,
            difficulty=analysis.difficulty,
        )

        enriched_recommendation = recommendation.copy()
        enriched_recommendation["analysis"] = analysis
        enriched_recommendation["hybrid_score"] = hybrid_score
        enriched_recommendation["analysis_status"] = "analyzed"

        enriched.append(enriched_recommendation)

    # Sort AI-analyzed recommendations by hybrid score.
    enriched.sort(
        key=lambda item: (
            item["hybrid_score"],
            item["score"],
        ),
        reverse=True,
    )

    # Preserve the remaining recommendations without making AI calls.
    for recommendation in recommendations_without_analysis:
        basic_recommendation = recommendation.copy()
        basic_recommendation["analysis"] = None
        basic_recommendation["hybrid_score"] = None
        basic_recommendation["analysis_status"] = "not_analyzed"

        enriched.append(basic_recommendation)

    return enriched
