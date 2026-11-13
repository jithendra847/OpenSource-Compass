from preprocessing import match_skills
from preprocessing import calculate_label_priority


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

def test_good_first_issue_priority():
    assert calculate_label_priority(
        ["good first issue"]
    ) == 3


def test_help_wanted_priority():
    assert calculate_label_priority(
        ["help wanted"]
    ) == 2


def test_up_for_grabs_priority():
    assert calculate_label_priority(
        ["up for grabs"]
    ) == 1


def test_unknown_label_priority():
    assert calculate_label_priority(
        ["bug"]
    ) == 0


def test_highest_priority_wins():
    assert calculate_label_priority(
        ["help wanted", "good first issue"]
    ) == 3