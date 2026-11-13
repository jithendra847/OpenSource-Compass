
import re


# --------------------------------
# 1. TEXT NORMALIZATION
# --------------------------------

def normalize_text(text):
    text = text.lower()
    text = re.sub(r"\s+", " ", text).strip()

    return text


# --------------------------------
# 2. SKILL MATCHING
# --------------------------------

def match_skills(developer_skills, issue_text):

    matched_skills = []

    issue_text = normalize_text(issue_text)

    for skill in developer_skills:

        normalized_skill = normalize_text(skill)

        if not normalized_skill:
            continue

        pattern = (
          r"(?<!\w)"
          + re.escape(normalized_skill)
          + r"(?!\w)"
          )

        if re.search(pattern, issue_text):
            matched_skills.append(skill)

    return matched_skills


# --------------------------------
# 3. WEIGHTED SCORE CALCULATION
# --------------------------------

def calculate_score(
    title_matched_skills,
    body_matched_skills,
    issue_labels
):

    score = 0

    # Title skill matches: 20 points each
    score += len(title_matched_skills) * 20

    # Description-only skill matches: 8 points each
    body_only_skills = [
        skill for skill in body_matched_skills
        if skill not in title_matched_skills
    ]

    score += len(body_only_skills) * 8

    # Normalize labels
    normalized_labels = [
        normalize_text(label)
        for label in issue_labels
    ]

    # Contribution label bonuses
    if "good first issue" in normalized_labels:
        score += 5

    if "help wanted" in normalized_labels:
        score += 3

    if "up for grabs" in normalized_labels:
        score += 2

    return score


# --------------------------------
# 4. MATCH PERCENTAGE CALCULATION
# --------------------------------

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


# --------------------------------
# 5. ISSUE RECOMMENDATION ENGINE
# --------------------------------

def recommend_issues(
    developer_skills,
    issues,
    min_score=10
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

            recommended.append({
                "id": issue.get("id"),
                "title": title,
                "url": issue.get("html_url"),
                "repository_url": issue.get("repository_url"),
                "labels": issue_labels,
                "title_matched_skills": title_matched_skills,
                "body_matched_skills": body_matched_skills,
                "score": score,
                "match_percentage": match_percentage
            })

# Sort recommendations using multiple ranking criteria
    recommended.sort(
     key=lambda item: (
        item["score"],

        len(set(
            item["title_matched_skills"] +
            item["body_matched_skills"]
        )),

        any(
            normalize_text(label) in {
                "good first issue",
                "help wanted",
                "up for grabs"
            }
            for label in item["labels"]
        )
    ),
    reverse=True
)

    return recommended

