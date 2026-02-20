"""LLM client package."""

import os

from llm.base import LLMClient, LLMError
from llm.claude_client import ClaudeClient
from llm.ollama_client import OllamaClient
from llm.openai_client import OpenAIClient


def get_client() -> LLMClient:
    """Factory to get configured LLM client."""
    provider = os.environ.get("LLM_PROVIDER", "claude").lower()
    if provider == "ollama":
        return OllamaClient()
    elif provider == "openai":
        return OpenAIClient()
    return ClaudeClient()


__all__ = ["LLMClient", "LLMError", "ClaudeClient", "OllamaClient", "OpenAIClient", "get_client"]
