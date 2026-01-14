"""Prompt builder for LLM nickname generation."""

import json
from typing import Optional

from data.styles import STYLES

SYSTEM_PROMPT = """You are a playa name generator for Burning Man participants. Generate creative, memorable nicknames based on the participant's answers.

## Output Format
Respond with valid JSON only:
{"nicknames": ["Name One", "Name Two", ...]}

## Rules
- Generate exactly 10 nickname candidates
- Each nickname: 1-2 words, Title Case
- Length: 3-28 characters total
- Allowed characters: letters, apostrophes, hyphens
- NO real names, insults, slurs, or protected traits
- Be creative, playful, and evocative"""


def build_prompt(
    qa_transcript: list[dict],
    style_mode: str,
    avoid_list: Optional[list[str]] = None,
) -> list[dict]:
    """
    Build OpenAI-compatible messages array.

    Args:
        qa_transcript: List of {"q": question, "a": answer} dicts
        style_mode: Style key ("m", "y", "c", "z")
        avoid_list: Optional list of nicknames to avoid

    Returns:
        List of message dicts: [{"role": "system", "content": "..."}, ...]
    """
    # Build user message as structured JSON
    style = STYLES.get(style_mode, STYLES["m"])

    user_data = {
        "style": style["prompt_modifier"],
        "answers": {
            qa["q"]: qa["a"]
            for qa in qa_transcript
            if qa["a"]  # Only include answered questions
        },
    }

    if avoid_list:
        user_data["avoid_names"] = avoid_list

    return [
        {"role": "system", "content": SYSTEM_PROMPT},
        {"role": "user", "content": json.dumps(user_data, indent=2)},
    ]
