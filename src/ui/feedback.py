"""Feedback form for collecting post-generation feedback."""

from typing import Optional

from prompt_toolkit import prompt as pt_prompt
from rich.align import Align
from rich.console import Console
from rich.text import Text

from data.questions import QUESTIONS
from ui.theme import (
    GRADIENT_NEON,
    STYLE_DIM,
    STYLE_ERROR,
    STYLE_KEY_BRACKET,
    STYLE_QUESTION,
    make_gradient_text,
    styled_rule,
)


def ask_feedback(
    console: Console,
    nicknames: list[str],
) -> Optional[dict]:
    """Show optional feedback form after nickname generation.

    Args:
        console: Rich console for output.
        nicknames: List of generated nickname strings.

    Returns:
        Dict with feedback fields, or None if the user skipped.
    """
    console.print()
    console.print(styled_rule("quick feedback (optional)"))
    console.print()
    console.print(Text("Help us improve!", style="bold white"))
    console.print()

    opt_in = pt_prompt("Give quick feedback? [Y/n]: ")
    if opt_in.strip().lower() == "n":
        return None

    console.print()

    favorite_name = _ask_favorite_name(console, nicknames)

    helpful = _ask_multi_select_questions(
        console, QUESTIONS, "Which questions were most helpful?"
    )
    unhelpful = _ask_multi_select_questions(
        console, QUESTIONS, "Which questions were least helpful?"
    )

    console.print(Text("What would make this questionnaire more helpful? Feel free to add your own questions.", style=STYLE_QUESTION))
    console.print(Text("Enter to skip", style=STYLE_DIM))
    suggested_questions = pt_prompt("> ")
    console.print()

    console.print(Text("What do you think is a good playa name for you?", style=STYLE_QUESTION))
    console.print(Text("Enter to skip", style=STYLE_DIM))
    self_suggested_name = pt_prompt("> ")
    console.print()

    console.print(Align.center(make_gradient_text("Thanks for the feedback!", GRADIENT_NEON, bold=True)))
    console.print()

    return {
        "favorite_name": favorite_name,
        "helpful_questions": helpful,
        "unhelpful_questions": unhelpful,
        "suggested_questions": suggested_questions,
        "self_suggested_name": self_suggested_name,
    }


def _ask_favorite_name(console: Console, nicknames: list[str]) -> Optional[str]:
    """Single-select for favorite nickname."""
    console.print(Text("Which name is your favorite?", style=STYLE_QUESTION))
    console.print(Text("Enter to skip", style=STYLE_DIM))
    console.print()

    line_zero = Text()
    line_zero.append("  [0]", style=STYLE_KEY_BRACKET)
    line_zero.append(" No favorite", style=STYLE_DIM)
    console.print(line_zero)

    for i, name in enumerate(nicknames, 1):
        line = Text()
        line.append(f"  [{i}]", style=STYLE_KEY_BRACKET)
        line.append(f" {name}")
        console.print(line)
    console.print()

    while True:
        raw = pt_prompt("Enter number [0]: ")
        if not raw.strip():
            return None
        try:
            choice = int(raw.strip())
            if choice == 0:
                return None
            if 1 <= choice <= len(nicknames):
                console.print()
                return nicknames[choice - 1]
        except ValueError:
            pass
        console.print(Text(f"Enter a number 0-{len(nicknames)}", style=STYLE_ERROR))


def _ask_multi_select_questions(
    console: Console,
    questions: list[dict],
    label: str,
) -> list[str]:
    """Multi-select for question_ids from answered questions."""
    if not questions:
        return []

    console.print(Text(label, style=STYLE_QUESTION))
    console.print(Text("Comma-separated numbers, or Enter to skip", style=STYLE_DIM))
    console.print()
    for i, qa in enumerate(questions, 1):
        line = Text()
        line.append(f"  [{i}]", style=STYLE_KEY_BRACKET)
        line.append(f" {qa['question']}")
        console.print(line)
    console.print()

    raw = pt_prompt("Enter numbers (e.g. 1,3): ")
    console.print()

    indices = _parse_comma_separated_ints(raw, len(questions))
    return [questions[i - 1]["question_id"] for i in indices]


def _parse_comma_separated_ints(raw: str, max_val: int) -> list[int]:
    """Parse '1,3,5' into [1, 3, 5], ignoring invalid entries."""
    if not raw.strip():
        return []
    results = []
    for part in raw.split(","):
        part = part.strip()
        try:
            num = int(part)
            if 1 <= num <= max_val and num not in results:
                results.append(num)
        except ValueError:
            continue
    return results
