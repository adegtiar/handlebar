"""Tests for questionnaire module."""

from unittest.mock import patch

from rich.console import Console

from ui.questionnaire import ask_questions


def test_ask_questions_returns_qa_format():
    """Should return list of dicts with 'q' and 'a' keys."""
    console = Console(record=True)
    questions = [
        {"question": "Test question?", "hint": "hint"},
    ]

    with patch("ui.questionnaire.pt_prompt", return_value="test answer"):
        result = ask_questions(console, questions)

    assert len(result) == 1
    assert result[0]["q"] == "Test question?"
    assert result[0]["a"] == "test answer"


def test_ask_questions_handles_blank_answers():
    """Should store blank answers when user skips."""
    console = Console(record=True)
    questions = [
        {"question": "Question 1?", "hint": "hint"},
        {"question": "Question 2?", "hint": "hint"},
    ]

    with patch("ui.questionnaire.pt_prompt", return_value=""):
        result = ask_questions(console, questions)

    assert result[0]["a"] == ""
    assert result[1]["a"] == ""


def test_ask_questions_processes_all_questions():
    """Should process every question in the list."""
    console = Console(record=True)
    questions = [
        {"question": f"Question {i}?", "hint": "hint"}
        for i in range(5)
    ]

    with patch("ui.questionnaire.pt_prompt", return_value="answer"):
        result = ask_questions(console, questions)

    assert len(result) == 5


def test_ask_questions_displays_question_text():
    """Should display question text in console output."""
    console = Console(record=True)
    questions = [
        {"question": "What is your vibe?", "hint": "e.g., chill"},
    ]

    with patch("ui.questionnaire.pt_prompt", return_value="cool"):
        ask_questions(console, questions)

    output = console.export_text()
    assert "What is your vibe?" in output
