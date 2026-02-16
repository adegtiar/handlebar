"""Prompt builder for LLM nickname generation."""

import json
from typing import Optional

from data.styles import STYLES

SYSTEM_PROMPT = """
You are a playa name generator for Burning Man participants. Your job is to
distill a participant's essence into a memorable name they'll carry on the
playa. Generate creative, memorable nicknames based on the participant's
answers.

## Output Format
Respond with valid JSON only:
{"nicknames": ["Name One", "Nametwo", ...]}

## Rules
- Generate exactly 7 nickname candidates
- Each nickname: 1-2 words, Title Case
- Length: 3-28 characters total
- Allowed characters: letters, apostrophes, hyphens
- Be creative, playful, and evocative
- If a real name is given, use it as a base for some suggestions. You can use parts of it, especially the front, or something that rhymes with it
- No more that 1/4 are alliterations

## What Makes a Great Playa Name
- Captures a contradiction, tension, or unexpected quality
- Sounds good shouted across a dusty dance floor at 4am
- Evokes imagery, sensation, or story preferably in 1 word (or 2 words max)
- Feels like it could only belong to THIS person
- Has rhythm and mouth-feel (alliteration, consonance, unexpected pairings)
- Short
- Mostly stick with one word
- Action
- Thing
- Trait
- Ironic
- Funny

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
        qa_transcript: List of {"question_id": id, "question": text, "answer": text} dicts
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
            qa["question"]: qa["answer"]
            for qa in qa_transcript
            if qa["answer"]  # Only include answered questions
        },
    }

    if avoid_list:
        user_data["avoid_names"] = avoid_list

    return [
        {"role": "system", "content": SYSTEM_PROMPT},
        {"role": "user", "content": json.dumps(user_data, indent=2)},
    ]