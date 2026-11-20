from preprocessing import match_skills

def test_javascript_alias():
    assert match_skills(
        ["JavaScript"],
        "We need a JS developer"
    ) == ["JavaScript"]


def test_python_alias():
    assert match_skills(
        ["Python"],
        "Experience with Py is required"
    ) == ["Python"]


def test_cpp_alias():
    assert match_skills(
        ["C++"],
        "Experience with CPP is preferred"
    ) == ["C++"]


def test_typescript_alias():
    assert match_skills(
        ["TypeScript"],
        "We use TS for development"
    ) == ["TypeScript"]


def test_no_false_java_match():
    assert match_skills(
        ["Java"],
        "We need a JavaScript developer"
    ) == []


def test_no_match():
    assert match_skills(
        ["Python"],
        "We need a frontend developer"
    ) == []


def test_empty_skill_is_skipped():
    assert match_skills(
        ["Python", ""],
        "Python developer needed"
    ) == ["Python"]

