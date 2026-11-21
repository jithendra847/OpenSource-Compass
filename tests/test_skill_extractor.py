from ai.skill_extractor import extract_required_skills


def test_extracts_programming_languages():
    skills = extract_required_skills(
        "Implement Python and JavaScript support"
    )
    assert "Python" in skills
    assert "JavaScript" in skills


def test_extracts_backend_frameworks():
    skills = extract_required_skills(
        "Build a REST API using FastAPI"
    )
    assert "FastAPI" in skills
    assert "REST APIs" in skills


def test_extracts_database_skills():
    skills = extract_required_skills(
        "Improve PostgreSQL database queries"
    )
    assert "PostgreSQL" in skills
    assert "SQL" in skills


def test_extracts_testing_and_debugging():
    skills = extract_required_skills(
        "Debug the issue and add unit tests"
    )
    assert "Debugging" in skills
    assert "Testing" in skills


def test_extracts_retry_and_error_handling_concepts():
    skills = extract_required_skills(
        "Implement retry logic and exception handling"
    )
    assert "Retry Logic" in skills
    assert "Error Handling" in skills


def test_extracts_skills_from_body():
    skills = extract_required_skills(
        "Improve the request handler",
        "Use Python, HTTP networking, caching and Docker."
    )
    assert "Python" in skills
    assert "Networking" in skills
    assert "Caching" in skills
    assert "Docker" in skills


def test_extracts_skills_from_labels():
    skills = extract_required_skills(
        "Improve the project",
        labels=["JavaScript", "testing"]
    )
    assert "JavaScript" in skills
    assert "Testing" in skills


def test_skill_results_are_unique():
    skills = extract_required_skills(
        "Python API",
        "Build a Python REST API with Python tests."
    )
    assert skills.count("Python") == 1
    assert skills.count("REST APIs") == 1


def test_matching_is_case_insensitive():
    skills = extract_required_skills(
        "IMPLEMENT FASTAPI WITH POSTGRESQL"
    )
    assert "FastAPI" in skills
    assert "PostgreSQL" in skills


def test_unknown_issue_returns_empty_list():
    skills = extract_required_skills(
        "Update the project description",
        "Change the wording of the introduction."
    )
    assert skills == []


def test_go_does_not_match_unrelated_words():
    skills = extract_required_skills(
        "Improve the ongoing documentation"
    )
    assert "Go" not in skills


def test_detects_multiple_technical_concepts():
    skills = extract_required_skills(
        "Improve security and performance using concurrency and CI/CD"
    )
    assert "Security" in skills
    assert "Performance Optimization" in skills
    assert "Concurrency" in skills
    assert "CI/CD" in skills
