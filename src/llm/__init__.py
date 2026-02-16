"""LLM client package."""

import os

from llm.base import LLMClient, LLMError
from llm.ollama_client import OllamaClient
from llm.openai_client import OpenAIClient


def get_client() -> LLMClient:
    """Factory to get configured LLM client."""
    provider = os.environ.get("LLM_PROVIDER", "openai").lower()
    if provider == "ollama":
        return OllamaClient()
    return OpenAIClient()


__all__ = ["LLMClient", "LLMError", "OllamaClient", "OpenAIClient", "get_client"]
