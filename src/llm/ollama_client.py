"""Ollama LLM client implementation using OpenAI-compatible API."""

import os

from openai import OpenAI, APIError

from llm.base import LLMError


class OllamaClient:
    """Ollama chat completion client via OpenAI-compatible endpoint."""

    def __init__(self):
        base_url = os.environ.get("OLLAMA_HOST", "http://localhost:11434/v1")
        model = os.environ.get("OLLAMA_MODEL", "llama3.2")
        self.client = OpenAI(base_url=base_url, api_key="ollama")
        self.model = model

    def generate(self, messages: list[dict]) -> str:
        """Send messages to Ollama and return response text."""
        try:
            response = self.client.chat.completions.create(
                model=self.model,
                messages=messages,
            )
            return response.choices[0].message.content
        except APIError as e:
            raise LLMError(f"Ollama API error: {e}") from e
