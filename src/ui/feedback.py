"""Feedback form for collecting post-generation feedback."""

from typing import Optional

from prompt_toolkit import prompt as pt_prompt
from rich.console import Console
from rich.panel import Panel


def ask_feedback(
    console: Console,
    nicknames: list[str],
    questions_asked: list[dict],
) -> Optional[dict]:
    """Show optional feedback form after nickname generation.

    Args:
        console: Rich console for output.
        nicknames: List of generated nickname strings.
        questions_asked: Q/A transcript dicts with 'question_id', 'question', 'answer'.

    Returns:
        Dict with feedback fields, or None if the user skipped.
    """
    console.print()
    console.print(
        Panel(
            "[bold]Help us improve! Press Enter to skip.[/bold]",
            title="Quick Feedback (optional)",
            border_style="cyan",
        )
    )
    console.print()

    opt_in = pt_prompt("Give quick feedback? [y/N]: ")
    if opt_in.strip().lower() != "y":
        return None

    console.print()

    favorite_name = _ask_favorite_name(console, nicknames)

    # Only show answered questions for helpful/unhelpful selectors
    answered = [qa for qa in questions_asked if qa.get("answer")]

    helpful = _ask_multi_select_questions(
        console, answered, "Which questions were most helpful?"
    )
    unhelpful = _ask_multi_select_questions(
        console, answered, "Which questions were least helpful?"
    )

    console.print("[bold cyan]What would make this questionnaire more helpful? Feel free to add your own questions.[/bold cyan]")
    console.print("[dim]Enter to skip[/dim]")
    suggested_questions = pt_prompt("> ")
    console.print()

    console.print("[bold cyan]What do you think is a good playa name for you?[/bold cyan]")
    console.print("[dim]Enter to skip[/dim]")
    self_suggested_name = pt_prompt("> ")
    console.print()

    console.print("[green]Thanks for the feedback![/green]")

    return {
        "favorite_name": favorite_name,
        "helpful_questions": helpful,
        "unhelpful_questions": unhelpful,
        "suggested_questions": suggested_questions,
        "self_suggested_name": self_suggested_name,
    }


def _ask_favorite_name(console: Console, nicknames: list[str]) -> Optional[str]:
    """Single-select for favorite nickname."""
    console.print("[bold cyan]Which name is your favorite?[/bold cyan]")
    console.print("[dim]Enter to skip[/dim]")
    console.print()
    console.print("  [bold cyan]\\[0][/bold cyan] No favorite")
    for i, name in enumerate(nicknames, 1):
        console.print(f"  [bold cyan]\\[{i}][/bold cyan] {name}")
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
        console.print(f"[red]Enter a number 0-{len(nicknames)}[/red]")


def _ask_multi_select_questions(
    console: Console,
    questions: list[dict],
    label: str,
) -> list[str]:
    """Multi-select for question_ids from answered questions."""
    if not questions:
        return []

    console.print(f"[bold cyan]{label}[/bold cyan]")
    console.print("[dim]Comma-separated numbers, or Enter to skip[/dim]")
    console.print()
    for i, qa in enumerate(questions, 1):
        console.print(f"  [bold cyan]\\[{i}][/bold cyan] {qa['question']}")
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
