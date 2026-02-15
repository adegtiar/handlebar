"""Questionnaire logic for collecting user answers."""

from typing import Optional

from prompt_toolkit import prompt as pt_prompt
from rich.console import Console
from rich.text import Text

from ui.theme import (
    GRADIENT_NEON,
    STYLE_DIM,
    STYLE_HINT,
    STYLE_QUESTION,
    STYLE_SUCCESS,
    make_gradient_text,
    styled_rule,
)


def ask_questions(
    console: Console,
    questions: list[dict],
    prefill_answers: Optional[dict[str, str]] = None,
) -> list[dict]:
    """
    Ask a series of questions and collect answers.

    Args:
        console: Rich console for output
        questions: List of dicts with 'question_id', 'question', and 'hint' keys
        prefill_answers: Optional dict mapping question_id to answer (non-interactive mode)

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
    prefill_answers: dict[str, str],
) -> list[dict]:
    """Build transcript from prefilled answers (non-interactive)."""
    qa_transcript = []

    console.print()
    console.print(styled_rule("prefilled answers"))
    console.print()
    console.print(Text("Using prefilled answers", style="bold white"))
    console.print()

    for i, q in enumerate(questions):
        question_id = q["question_id"]
        question_text = q["question"]
        # Look up answer by question_id
        answer = prefill_answers.get(question_id, "")

        label = Text()
        label.append(f"Q{i + 1}: ", style=STYLE_SUCCESS)
        label.append(question_text, style=STYLE_QUESTION)
        console.print(label)

        if answer:
            console.print(Text(f"A: {answer}", style=STYLE_SUCCESS))
        else:
            console.print(Text("A: (skipped)", style=STYLE_DIM))
        console.print()

        qa_transcript.append({"question_id": question_id, "question": question_text, "answer": answer})

    console.print(styled_rule())
    return qa_transcript


def _interactive_questions(console: Console, questions: list[dict]) -> list[dict]:
    """Collect answers interactively."""
    qa_transcript = []

    console.print()
    console.print(styled_rule("questionnaire"))
    console.print()
    console.print(Text("Answer a few questions to help generate your playa name.", style="bold white"))
    console.print(Text("Press Enter to skip any question.", style=STYLE_DIM))
    console.print()

    for i, q in enumerate(questions, 1):
        question_id = q["question_id"]
        question_text = q["question"]
        hint = q.get("hint", "")

        progress = make_gradient_text(f"[{i}/{len(questions)}]", GRADIENT_NEON, bold=True)
        console.print(progress)
        console.print(Text(question_text, style=STYLE_QUESTION))
        if hint:
            console.print(Text(hint, style=STYLE_HINT))

        answer = pt_prompt("> ")

        qa_transcript.append({"question_id": question_id, "question": question_text, "answer": answer})
        console.print()

    console.print(styled_rule())
    return qa_transcript
