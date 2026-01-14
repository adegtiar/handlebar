"""Questionnaire logic for collecting user answers."""

from typing import Optional

from prompt_toolkit import prompt as pt_prompt
from rich.console import Console
from rich.panel import Panel


def ask_questions(
    console: Console,
    questions: list[dict],
    prefill_answers: Optional[list[str]] = None,
) -> list[dict]:
    """
    Ask a series of questions and collect answers.

    Args:
        console: Rich console for output
        questions: List of dicts with 'question' and 'hint' keys
        prefill_answers: Optional list of pre-filled answers (non-interactive mode)

    Returns:
        List of dicts with 'q' and 'a' keys (Q/A transcript)
    """
    # Non-interactive mode with prefilled answers
    if prefill_answers is not None:
        return _prefill_questions(console, questions, prefill_answers)

    # Interactive mode
    return _interactive_questions(console, questions)


def _prefill_questions(
    console: Console,
    questions: list[dict],
    prefill_answers: list[str],
) -> list[dict]:
    """Build transcript from prefilled answers (non-interactive)."""
    qa_transcript = []

    # Warn if count mismatch
    if len(prefill_answers) != len(questions):
        console.print(
            f"[yellow]Warning: {len(prefill_answers)} answers provided for "
            f"{len(questions)} questions[/yellow]"
        )

    console.print()
    console.print(
        Panel(
            "[bold]Using prefilled answers[/bold]",
            title="Questionnaire",
            border_style="cyan",
        )
    )
    console.print()

    for i, q in enumerate(questions):
        question_text = q["question"]
        # Use prefill if available, otherwise empty string
        answer = prefill_answers[i] if i < len(prefill_answers) else ""

        console.print(f"[bold cyan]Q{i + 1}:[/bold cyan] {question_text}")
        console.print(f"[green]A:[/green] {answer or '[dim](skipped)[/dim]'}")
        console.print()

        qa_transcript.append({"q": question_text, "a": answer})

    return qa_transcript


def _interactive_questions(console: Console, questions: list[dict]) -> list[dict]:
    """Collect answers interactively."""
    qa_transcript = []

    console.print()
    console.print(
        Panel(
            "[bold]Answer a few questions to help generate your playa name.[/bold]\n"
            "[dim]Press Enter to skip any question.[/dim]",
            title="Questionnaire",
            border_style="cyan",
        )
    )
    console.print()

    for i, q in enumerate(questions, 1):
        question_text = q["question"]
        hint = q.get("hint", "")

        console.print(f"[bold cyan]Question {i}/{len(questions)}[/bold cyan]")
        console.print(f"[white]{question_text}[/white]")
        if hint:
            console.print(f"[dim italic]{hint}[/dim italic]")

        answer = pt_prompt("> ")

        qa_transcript.append({"q": question_text, "a": answer})
        console.print()

    return qa_transcript
