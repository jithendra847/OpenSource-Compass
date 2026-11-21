import re


SKILL_PATTERNS = {
    "Python": [r"\bpython\b"],
    "Java": [r"\bjava\b"],
    "JavaScript": [r"\bjavascript\b", r"\bjs\b"],
    "TypeScript": [r"\btypescript\b"],
    "C++": [r"\bc\+\+(?!\w)"],
    "Go": [r"\bgolang\b", r"\bgo language\b"],
    "Rust": [r"\brust\b"],
    "HTML": [r"\bhtml\b"],
    "CSS": [r"\bcss\b"],
    "React": [r"\breact(?:\.js)?\b"],
    "Node.js": [r"\bnode(?:\.js)?\b"],
    "FastAPI": [r"\bfastapi\b"],
    "Flask": [r"\bflask\b"],
    "Django": [r"\bdjango\b"],
    "REST APIs": [r"\brest(?:ful)?\b", r"\bapi(?:s)?\b"],
    "SQL": [r"\bsql\b", r"\bqueries\b", r"\bdatabase queries\b"],
    "PostgreSQL": [r"\bpostgres(?:ql)?\b"],
    "MySQL": [r"\bmysql\b"],
    "MongoDB": [r"\bmongodb\b"],
    "Git": [r"\bgit\b", r"\bversion control\b"],
    "Docker": [r"\bdocker\b", r"\bcontainerization\b"],
    "CI/CD": [r"\bci/?cd\b", r"\bcontinuous integration\b", r"\bcontinuous deployment\b"],
    "Testing": [r"\btests?\b", r"\btesting\b", r"\bunit tests?\b"],
    "Debugging": [r"\bdebug(?:ging)?\b", r"\btroubleshoot(?:ing)?\b"],
    "Authentication": [r"\bauthentication\b", r"\bauth\b", r"\blogin\b"],
    "Security": [r"\bsecurity\b", r"\bvulnerabilit(?:y|ies)\b"],
    "Concurrency": [r"\bconcurren(?:cy|t)\b", r"\bparallelism\b", r"\bthreading\b"],
    "Caching": [r"\bcach(?:e|ing)\b"],
    "Error Handling": [r"\berror handling\b", r"\bexception handling\b"],
    "Retry Logic": [r"\bretr(?:y|ies|ying)\b", r"\bretry logic\b", r"\bbackoff\b"],
    "Performance Optimization": [r"\bperformance\b", r"\boptimiz(?:e|ation|ing)\b"],
    "Networking": [r"\bnetworking\b", r"\bnetwork requests?\b", r"\bhttp\b", r"\bhttps\b"],
    "Data Structures": [r"\bdata structures?\b"],
    "Algorithms": [r"\balgorithms?\b"],
    "Machine Learning": [r"\bmachine learning\b", r"\bml\b"],
    "Data Analysis": [r"\bdata analysis\b", r"\banalytics\b"],
}

def extract_required_skills(
    title: str,
    body: str = "",
    labels: list[str] | None = None
) -> list[str]:
    """Extract known skills and concepts from an issue's title, body, and labels."""

    text = f"{title} {body} {' '.join(labels or [])}".lower()

    found_skills = []

    for skill, patterns in SKILL_PATTERNS.items():
        if any(re.search(pattern, text, re.IGNORECASE) for pattern in patterns):
            found_skills.append(skill)

    return found_skills

