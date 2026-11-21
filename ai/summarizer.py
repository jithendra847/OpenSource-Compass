import re

from models.analysis import IssueSummary


def clean_markdown(text: str) -> str:
    """Remove common Markdown formatting without changing the underlying text."""

    text = re.sub(r"```[\s\S]*?```", " ", text)
    text = re.sub(r"`([^`]+)`", r"\1", text)
    text = re.sub(r"!\[([^\]]*)\]\([^)]+\)", r"\1", text)
    text = re.sub(r"\[([^\]]+)\]\([^)]+\)", r"\1", text)
    text = re.sub(r"#{1,6}\s*", "", text)
    text = re.sub(r"(\*\*|\*|~~)", "", text)
    text = re.sub(r"(?<!\w)_([^_]+)_(?!\w)", r"\1", text)
    text = re.sub(r"^\s*[-*+]\s+", "", text, flags=re.MULTILINE)
    text = re.sub(r"^\s*\d+\.\s+", "", text, flags=re.MULTILINE)
    text = re.sub(r">\s*", "", text)
    text = re.sub(r"\s+", " ", text)
    return text.strip()


def summarize_issue(title: str, body: str = "") -> IssueSummary:
    """Create a basic cleaned fallback summary. This is not AI summarization."""

    cleaned_title = clean_markdown(title)
    cleaned_body = clean_markdown(body)

    if cleaned_body:
        sentences = re.split(r"(?<=[.!?])\s+", cleaned_body)
        selected = " ".join(sentences[:2]).strip()
        summary_text = selected if selected else cleaned_body
    elif cleaned_title:
        summary_text = cleaned_title
    else:
        summary_text = "No issue description is available."

    return IssueSummary(summary=summary_text)
