import pytest
from unittest.mock import Mock

from ai.llm_client import (
    generate_text,
    generate_structured,
    LLMAPIError,
    LLMResponseError,
)
from models.analysis import IssueSummary

def create_mock_response(content):
    response = Mock()
    response.choices = [
        Mock(message=Mock(content=content))
    ]
    return response

def test_generate_structured_success(monkeypatch):
    mock_response = create_mock_response(
        '{"summary": "The API crashes when email is empty."}'
    )

    monkeypatch.setattr(
        "ai.llm_client.client.chat.completions.create",
        lambda **kwargs: mock_response,
    )

    result = generate_structured(
        "Summarize this issue",
        response_model=IssueSummary,
    )

    assert isinstance(result, IssueSummary)
    assert result.summary == "The API crashes when email is empty."


def test_generate_structured_invalid_json(monkeypatch):
    mock_response = create_mock_response(
        "This is not valid JSON"
    )

    monkeypatch.setattr(
        "ai.llm_client.client.chat.completions.create",
        lambda **kwargs: mock_response,
    )

    with pytest.raises(Exception):
        generate_structured(
            "Summarize this issue",
            response_model=IssueSummary,
        )


def test_generate_structured_validation_error(monkeypatch):
    mock_response = create_mock_response(
        '{"wrong_field": "some value"}'
    )

    monkeypatch.setattr(
        "ai.llm_client.client.chat.completions.create",
        lambda **kwargs: mock_response,
    )

    with pytest.raises(Exception):
        generate_structured(
            "Summarize this issue",
            response_model=IssueSummary,
        )


def test_generate_structured_sends_json_mode(monkeypatch):
    mock_response = create_mock_response(
        '{"summary": "A short summary"}'
    )

    mock_create = Mock(return_value=mock_response)

    monkeypatch.setattr(
        "ai.llm_client.client.chat.completions.create",
        mock_create,
    )

    generate_structured(
        "Summarize this issue",
        response_model=IssueSummary,
    )

    call_kwargs = mock_create.call_args.kwargs

    assert call_kwargs["response_format"] == {
        "type": "json_object"
    }

def test_generate_text_empty_response(monkeypatch):
    mock_response = create_mock_response("")

    monkeypatch.setattr(
        "ai.llm_client.client.chat.completions.create",
        lambda **kwargs: mock_response,
    )

    with pytest.raises(LLMResponseError):
        generate_text("Explain APIs")


def test_generate_text_api_error(monkeypatch):
    from openai import APIError

    mock_create = Mock(
        side_effect=APIError(
            message="Provider unavailable",
            request=None,
            body=None,
        )
    )

    monkeypatch.setattr(
        "ai.llm_client.client.chat.completions.create",
        mock_create,
    )

    with pytest.raises(LLMAPIError):
        generate_text("Explain APIs")


def test_generate_structured_empty_response(monkeypatch):
    mock_response = create_mock_response("")

    monkeypatch.setattr(
        "ai.llm_client.client.chat.completions.create",
        lambda **kwargs: mock_response,
    )

    with pytest.raises(LLMResponseError):
        generate_structured(
            "Summarize issue",
            response_model=IssueSummary,
        )