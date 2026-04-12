"""LLM client package."""

import logging
import os

from llm.base import LLMClient, LLMError
from llm.claude_client import ClaudeClient
from llm.ollama_client import OllamaClient
from llm.openai_client import OpenAIClient

log = logging.getLogger(__name__)


def _create_client(provider: str) -> LLMClient:
    """Create an LLM client for the given provider name."""
    if provider == "ollama":
        return OllamaClient()
    elif provider == "openai":
        return OpenAIClient()
    return ClaudeClient()


class FallbackClient:
    """Wraps a primary and backup LLM client, falling back on error."""

    def __init__(self, primary: LLMClient, backup: LLMClient) -> None:
        self.primary = primary
        self.backup = backup
        self.used_backup = False
        self.on_fallback = None

    def generate(self, messages: list[dict]) -> str:
        self.used_backup = False
        try:
            return self.primary.generate(messages)
        except LLMError as primary_err:
            log.warning("Primary LLM failed (%s), falling back to backup", primary_err)
            try:
                if self.on_fallback:
                    self.on_fallback()
                result = self.backup.generate(messages)
                self.used_backup = True
                return result
            except LLMError:
                raise primary_err


def get_client() -> LLMClient:
    """Factory to get configured LLM client."""
    provider = os.environ.get("LLM_PROVIDER", "claude").lower()
    primary = _create_client(provider)

    backup_provider = os.environ.get("LLM_PROVIDER_BACKUP", "").lower()
    if backup_provider:
        backup = _create_client(backup_provider)
        return FallbackClient(primary, backup)

    return primary


__all__ = [
    "LLMClient", "LLMError", "ClaudeClient", "OllamaClient", "OpenAIClient",
    "FallbackClient", "get_client",
]
