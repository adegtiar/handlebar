"""Base classes for LLM clients."""

from typing import Protocol


class LLMClient(Protocol):
    """Protocol for LLM clients. Implement generate() to create a new provider."""

    def generate(self, messages: list[dict]) -> str:
        """Send messages to LLM, return raw response text."""
        ...


class LLMError(Exception):
    """Raised when LLM request fails."""

    pass
