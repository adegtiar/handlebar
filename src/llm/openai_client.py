"""OpenAI LLM client implementation."""

import os

from openai import OpenAI, APIError

from llm.base import LLMError


class OpenAIClient:
    """OpenAI chat completion client."""

    def __init__(
        self,
        model: str = "gpt-5.2",
    ):
        api_key = os.environ.get("OPENAI_API_KEY")
        if not api_key:
            raise LLMError("OPENAI_API_KEY environment variable not set")
        self.client = OpenAI(api_key=api_key)
        self.model = model

    def generate(self, messages: list[dict]) -> str:
        """Send messages to OpenAI and return response text."""
        try:
            response = self.client.chat.completions.create(
                model=self.model,
                messages=messages,
            )
            return response.choices[0].message.content
        except APIError as e:
            raise LLMError(f"OpenAI API error: {e}") from e
