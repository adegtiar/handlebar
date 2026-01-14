"""Questionnaire logic for collecting user answers."""

from rich.console import Console
from rich.panel import Panel
from rich.prompt import Prompt


def ask_questions(console: Console, questions: list[dict]) -> list[dict]:
    """
    Ask a series of questions and collect answers.

    Args:
        console: Rich console for output
        questions: List of dicts with 'question' and 'hint' keys

    Returns:
        List of dicts with 'q' and 'a' keys (Q/A transcript)
    """
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

        answer = Prompt.ask("[green]>[/green]", default="", show_default=False)

        qa_transcript.append({"q": question_text, "a": answer})
        console.print()

    return qa_transcript
