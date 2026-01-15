"""LLM client package."""

from llm.base import LLMClient, LLMError
from llm.openai_client import OpenAIClient


def get_client() -> LLMClient:
    """Factory to get configured LLM client."""
    return OpenAIClient()


__all__ = ["LLMClient", "LLMError", "OpenAIClient", "get_client"]
