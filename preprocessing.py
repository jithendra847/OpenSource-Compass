
import re


# --------------------------------
# 1. TEXT NORMALIZATION
# --------------------------------

def normalize_text(text):
    text = text.lower()
    text = re.sub(r"[^\w\s]", "", text)
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

        pattern = r"\b" + re.escape(normalized_skill) + r"\b"

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

    # 15 points for every skill found in the title
    score += len(title_matched_skills) * 15

    # Find skills present only in the description
    body_only_skills = [
        skill for skill in body_matched_skills
        if skill not in title_matched_skills
    ]

    # 5 points for every description-only skill
    score += len(body_only_skills) * 5

    # 5 bonus points for good first issue
    if any(
        normalize_text(label) == "good first issue"
        for label in issue_labels
    ):
        score += 5

    return score


# --------------------------------
# 4. ISSUE RECOMMENDATION ENGINE
# --------------------------------

def recommend_issues(developer_skills, issues,min_score=10):

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
            developer_skills, title
        )

        body_matched_skills = match_skills(
            developer_skills, body
        )

        # Calculate weighted score
        score = calculate_score(
            title_matched_skills,
            body_matched_skills,
            issue_labels
        )

        # Store recommendation details
        if score>=min_score:
         recommended.append({
            "id": issue.get("id"),
            "title": title,
            "url": issue.get("html_url"),
            "repository_url": issue.get("repository_url"),
            "labels": issue_labels,
            "title_matched_skills": title_matched_skills,
            "body_matched_skills": body_matched_skills,
            "score": score
        })

    # Sort recommendations by score (highest first)
    recommended.sort(
        key=lambda item: item["score"],
        reverse=True
    )

    return recommended

