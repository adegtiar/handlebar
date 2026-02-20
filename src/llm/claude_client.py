"""Anthropic Claude LLM client implementation."""

import os

import anthropic

from llm.base import LLMError


class ClaudeClient:
    """Anthropic Claude messages client."""

    def __init__(self, model: str = "claude-opus-4-6"):
        api_key = os.environ.get("ANTHROPIC_API_KEY")
        if not api_key:
            raise LLMError("ANTHROPIC_API_KEY environment variable not set")
        self.client = anthropic.Anthropic(api_key=api_key)
        self.model = model

    def generate(self, messages: list[dict]) -> str:
        """Send messages to Claude and return response text."""
        system = ""
        user_messages = []
        for msg in messages:
            if msg["role"] == "system":
                system = msg["content"]
            else:
                user_messages.append(msg)
        try:
            response = self.client.messages.create(
                model=self.model,
                max_tokens=1024,
                system=system,
                messages=user_messages,
            )
            return response.content[0].text
        except Exception as e:
            raise LLMError(f"Claude API error: {e}") from e
