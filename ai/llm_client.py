
import os
import json

from pydantic import BaseModel, ValidationError
from dotenv import load_dotenv
from openai import OpenAI, APIError

# Load environment variables from .env
load_dotenv()

class LLMError(Exception):
    """Base exception for LLM-related errors."""
    pass


class LLMAPIError(LLMError):
    """Raised when the LLM provider request fails."""
    pass


class LLMResponseError(LLMError):
    """Raised when the LLM response is invalid or unusable."""
    pass
# Read OpenRouter API key
api_key = os.getenv("OPENROUTER_API_KEY")

if not api_key:
    raise ValueError("OPENROUTER_API_KEY is missing from environment variables.")

# Create OpenRouter client
client = OpenAI(
    base_url="https://openrouter.ai/api/v1",
    api_key=api_key,
    timeout=30.0,
    max_retries=2,
)

# Model we'll use
MODEL_NAME = os.getenv("OPENROUTER_MODEL", "openrouter/free")


def generate_text(
    prompt: str,
    system_prompt: str | None = None
) -> str:
    """Send a prompt to the LLM with optional system instructions."""

    messages = []

    if system_prompt:
        messages.append(
            {"role": "system", "content": system_prompt}
        )

    messages.append(
        {"role": "user", "content": prompt}
    )

    try:
        response = client.chat.completions.create(
            model=MODEL_NAME,
            messages=messages,
        )

        content = response.choices[0].message.content

        if not content or not content.strip():
            raise LLMResponseError("The LLM returned an empty response.")

        return content.strip()

    except LLMResponseError:
        raise

    except APIError as e:
        raise LLMAPIError(f"LLM provider request failed: {e}") from e


def generate_structured(
    prompt: str,
    response_model: type[BaseModel],
    system_prompt: str | None = None,
) -> BaseModel:
    """Generate JSON from the LLM and validate it with a Pydantic model."""

    messages = []

    if system_prompt:
        messages.append(
            {"role": "system", "content": system_prompt}
        )

    messages.append(
        {"role": "user", "content": prompt}
    )

    try:
        response = client.chat.completions.create(
            model=MODEL_NAME,
            messages=messages,
            response_format={"type": "json_object"},
        )

        response_text = response.choices[0].message.content

        if not response_text or not response_text.strip():
            raise LLMResponseError("The LLM returned an empty response.")

        data = json.loads(response_text)

        return response_model.model_validate(data)

    except LLMResponseError:
        raise

    except APIError as e:
        raise LLMAPIError(f"LLM provider request failed: {e}") from e

    except (json.JSONDecodeError, ValidationError) as e:
        raise LLMResponseError(
            f"The LLM returned invalid structured data: {e}"
        ) from e