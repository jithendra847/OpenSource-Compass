
import re

# --------------------------------
# SKILL ALIASES
# --------------------------------

SKILL_ALIASES = {
    "javascript": ["js"],
    "python": ["py"],
    "c++": ["cpp"],
    "typescript": ["ts"],
}

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

        # Get alternative names for the skill
        aliases = SKILL_ALIASES.get(normalized_skill, [])

        # Check both original skill and its aliases
        skill_variations = [normalized_skill] + aliases

        for variation in skill_variations:

            pattern = (
                r"(?<!\w)"
                + re.escape(variation)
                + r"(?!\w)"
            )

            if re.search(pattern, issue_text):

                matched_skills.append(skill)

                # Avoid duplicate matches for the same skill
                break

    return matched_skills



