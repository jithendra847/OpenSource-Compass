from ai.summarizer import clean_markdown, summarize_issue


def test_summary_uses_issue_body():
    result = summarize_issue(
        "Improve API",
        "Add retry handling for failed HTTP requests."
    )
    assert "retry handling" in result.summary


def test_summary_falls_back_to_title_when_body_is_empty():
    result = summarize_issue("Fix database connection")
    assert result.summary == "Fix database connection"


def test_empty_title_and_body_returns_fallback():
    result = summarize_issue("", "")
    assert result.summary == "No issue description is available."


def test_markdown_headings_are_removed():
    result = summarize_issue(
        "Example",
        "## Task\nImprove the API response."
    )
    assert "##" not in result.summary
    assert "Task" in result.summary


def test_markdown_links_are_cleaned():
    result = summarize_issue(
        "Example",
        "Read [the API documentation](https://example.com) first."
    )
    assert "the API documentation" in result.summary
    assert "https://example.com" not in result.summary


def test_inline_code_formatting_is_removed():
    result = summarize_issue(
        "Example",
        "Update the `request_handler` function."
    )
    assert "`" not in result.summary
    assert "request_handler" in result.summary


def test_multiple_sentences_are_limited_to_two():
    result = summarize_issue(
        "Example",
        "First sentence. Second sentence. Third sentence. Fourth sentence."
    )
    assert result.summary == "First sentence. Second sentence."


def test_markdown_bullet_symbols_are_cleaned():
    result = summarize_issue(
        "Example",
        "- Add retry logic\n- Handle timeouts"
    )
    assert "-" not in result.summary
    assert "Add retry logic" in result.summary


def test_whitespace_is_normalized():
    result = summarize_issue(
        "Example",
        "  Add   retry\n\n handling   for API. "
    )
    assert "  " not in result.summary


def test_clean_markdown_handles_empty_input():
    assert clean_markdown("") == ""


def test_summary_model_returns_non_empty_text():
    result = summarize_issue("Fix issue", "Improve error handling.")
    assert result.summary.strip()
