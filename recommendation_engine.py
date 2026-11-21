from preprocessing import match_skills, normalize_text

# Scoring weights
TITLE_SKILL_WEIGHT = 20
BODY_SKILL_WEIGHT = 8

GOOD_FIRST_ISSUE_BONUS = 5
HELP_WANTED_BONUS = 3
UP_FOR_GRABS_BONUS = 2

# Ranking priorities
GOOD_FIRST_ISSUE_PRIORITY = 3
HELP_WANTED_PRIORITY = 2
UP_FOR_GRABS_PRIORITY = 1

DEFAULT_MIN_SCORE = 10

def normalize_label(label):
    label = normalize_text(label)
    label = label.replace("-", " ").replace("_", " ")
    return normalize_text(label)

def calculate_score(
    title_matched_skills,
    body_matched_skills,
    issue_labels
):
    score = 0

    # Title skill matches
    score += len(title_matched_skills) * TITLE_SKILL_WEIGHT

    # Description-only skill matches
    body_only_skills = [
        skill for skill in body_matched_skills
        if skill not in title_matched_skills
    ]

    score += len(body_only_skills) * BODY_SKILL_WEIGHT

    # Normalize labels
    normalized_labels = [
        normalize_label(label)
        for label in issue_labels
    ]

    # Contribution label bonuses
    if "good first issue" in normalized_labels:
        score += GOOD_FIRST_ISSUE_BONUS

    if "help wanted" in normalized_labels:
        score += HELP_WANTED_BONUS

    if "up for grabs" in normalized_labels:
        score += UP_FOR_GRABS_BONUS

    return score

def generate_explanation(
    title_matched_skills,
    body_matched_skills,
    issue_labels
):
    explanation = []

    # Title skill matches
    for skill in title_matched_skills:
        explanation.append(
            f"{skill} matched in title (+{TITLE_SKILL_WEIGHT})"
        )

    # Description-only skill matches
    body_only_skills = [
        skill for skill in body_matched_skills
        if skill not in title_matched_skills
    ]

    for skill in body_only_skills:
        explanation.append(
            f"{skill} matched in description (+{BODY_SKILL_WEIGHT})"
        )

    # Normalize labels
    normalized_labels = [
        normalize_label(label)
        for label in issue_labels
    ]

    # Contribution label bonuses
    if "good first issue" in normalized_labels:
        explanation.append(
            f"Good first issue label (+{GOOD_FIRST_ISSUE_BONUS})"
        )

    if "help wanted" in normalized_labels:
        explanation.append(
            f"Help wanted label (+{HELP_WANTED_BONUS})"
        )

    if "up for grabs" in normalized_labels:
        explanation.append(
            f"Up for grabs label (+{UP_FOR_GRABS_BONUS})"
        )

    return explanation

def calculate_match_percentage(
    developer_skills,
    title_matched_skills,
    body_matched_skills
):

    # Combine title and description matches
    # set() prevents duplicate skill counting
    matched_skills = set(
        title_matched_skills + body_matched_skills
    )

    if not developer_skills:
        return 0.0

    match_percentage = (
        len(matched_skills) / len(developer_skills)
    ) * 100

    return round(match_percentage, 2)

def calculate_label_priority(issue_labels):

    normalized_labels = [
        normalize_label(label)
        for label in issue_labels
    ]

    if "good first issue" in normalized_labels:
        return GOOD_FIRST_ISSUE_PRIORITY

    elif "help wanted" in normalized_labels:
        return HELP_WANTED_PRIORITY

    elif "up for grabs" in normalized_labels:
        return UP_FOR_GRABS_PRIORITY

    return 0

# --------------------------------
# 5. ISSUE RECOMMENDATION ENGINE
# --------------------------------

def recommend_issues(
    developer_skills,
    issues,
    min_score=DEFAULT_MIN_SCORE
):

    recommended = []

    for issue in issues:

        # Extract title and body
        title = issue.get("title") or ""
        body = issue.get("body") or ""

        # Extract GitHub issue labels
        issue_labels = [
            label.get("name", "")
            for label in issue.get("labels", [])
            if isinstance(label, dict)
        ]

        # Match skills independently
        title_matched_skills = match_skills(
            developer_skills,
            title
        )

        body_matched_skills = match_skills(
            developer_skills,
            body
        )

        # Calculate weighted score
        score = calculate_score(
            title_matched_skills,
            body_matched_skills,
            issue_labels
        )

        # Calculate skill match percentage
        match_percentage = calculate_match_percentage(
            developer_skills,
            title_matched_skills,
            body_matched_skills
        )

        # Apply minimum score filtering
        if score >= min_score:
            explanation = generate_explanation(
               title_matched_skills,
               body_matched_skills,
               issue_labels
               )

            recommended.append({
                "id": issue.get("id"),
                "title": title,
                "url": issue.get("html_url"),
                "repository_url": issue.get("repository_url"),
                "labels": issue_labels,
                "title_matched_skills": title_matched_skills,
                "body_matched_skills": body_matched_skills,
                "score": score,
                "match_percentage": match_percentage,
                "explanation": explanation,
                "created_at": issue.get("created_at", "")
            })

    # Sort recommendations using multiple ranking criteria
    recommended.sort(
        key=lambda item: (
            item["score"],
            len(set(
                item["title_matched_skills"] +
                item["body_matched_skills"]
            )),
            calculate_label_priority(item["labels"]),
            item["created_at"]
        ),
        reverse=True
    )

    return recommended

