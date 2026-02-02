"""Prompt builder for LLM nickname generation."""

import json
from typing import Optional

from data.styles import STYLES

SYSTEM_PROMPT = """You are a playa name generator for Burning Man participants. Generate creative, memorable nicknames based on the participant's answers.

## Output Format
Respond with valid JSON only:
{"nicknames": ["Name One", "Name Two",...]}

## Rules
- Generate exactly 20 nickname candidates
- Each nickname: 1-2 words, Title Case
- Length: 3-28 characters total
- Allowed characters: letters, apostrophes, hyphens
- Be creative, playful, and evocative
- If a real name is given, use it as a base for some suggestions. You can use parts of it, especially the front, or something that rhymes with it
- No more that 1/4 are alliterations

## Suggestions for good nicknames:
Short
Mostly one word
Action
Thing
Trait
Ironic
Funny

## Examples
Here are some examples and why there are good:
Nurse Noise - Alliteration, reflects her DJ interest
Flutter - Verb, reflects her active nature, and high energy
Danimal - Takes his name, Dan, and combines it with animal
Shimmer - Nice quality, gives a ethereal vibe
Maculate - Uses last name but converts it from immaculate
Badazzler - Takes a funny decor meme and adds bad. There's a story behind it.
Yardsale - Went to burningmand and lost all his stuff (wallet, keys, phone)
Sunshine - fun, positive, good vibes
Chuckles - funny, ironic because his stoic and grumpy (sometimes)
Sir Bear - Big furry guy with big presence
Captain T-Bag - funny name, maybe there is a story"""

"""
- NO real names, insults, slurs, or protected traits
{"nicknames": [{"name": "Name One", "explanation": "Brief explanation of how this name connects to the answers"}, ...]}

"""

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
