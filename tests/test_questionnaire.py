"""Tests for questionnaire module."""

from unittest.mock import patch

from rich.console import Console

from ui.questionnaire import ask_questions


def test_ask_questions_returns_qa_format():
    """Should return list of dicts with question_id, question, and answer keys."""
    console = Console(record=True)
    questions = [
        {"question_id": "q1", "question": "Test question?", "hint": "hint"},
    ]

    with patch("ui.questionnaire.pt_prompt", return_value="test answer"):
        result = ask_questions(console, questions)

    assert len(result) == 1
    assert result[0]["question"] == "Test question?"
    assert result[0]["answer"] == "test answer"
    assert result[0]["question_id"] == "q1"


def test_ask_questions_handles_blank_answers():
    """Should store blank answers when user skips."""
    console = Console(record=True)
    questions = [
        {"question_id": "q1", "question": "Question 1?", "hint": "hint"},
        {"question_id": "q2", "question": "Question 2?", "hint": "hint"},
    ]

    with patch("ui.questionnaire.pt_prompt", return_value=""):
        result = ask_questions(console, questions)

    assert result[0]["answer"] == ""
    assert result[1]["answer"] == ""


def test_ask_questions_processes_all_questions():
    """Should process every question in the list."""
    console = Console(record=True)
    questions = [
        {"question_id": f"q{i}", "question": f"Question {i}?", "hint": "hint"}
        for i in range(5)
    ]

    with patch("ui.questionnaire.pt_prompt", return_value="answer"):
        result = ask_questions(console, questions)

    assert len(result) == 5


def test_ask_questions_displays_question_text():
    """Should display question text in console output."""
    console = Console(record=True)
    questions = [
        {"question_id": "vibe", "question": "What is your vibe?", "hint": "e.g., chill"},
    ]

    with patch("ui.questionnaire.pt_prompt", return_value="cool"):
        ask_questions(console, questions)

    output = console.export_text()
    assert "What is your vibe?" in output


def test_prefill_answers_returns_correct_transcript():
    """Should build transcript from prefilled answers without prompting."""
    console = Console(record=True)
    questions = [
        {"question_id": "q1", "question": "Question 1?", "hint": "hint"},
        {"question_id": "q2", "question": "Question 2?", "hint": "hint"},
    ]
    prefill = {"q1": "Answer 1", "q2": "Answer 2"}

    result = ask_questions(console, questions, prefill_answers=prefill)

    assert len(result) == 2
    assert result[0]["question"] == "Question 1?"
    assert result[0]["answer"] == "Answer 1"
    assert result[1]["question"] == "Question 2?"
    assert result[1]["answer"] == "Answer 2"


def test_prefill_with_blank_lines():
    """Should treat missing prefill entries as skipped questions."""
    console = Console(record=True)
    questions = [
        {"question_id": "q1", "question": "Question 1?", "hint": "hint"},
        {"question_id": "q2", "question": "Question 2?", "hint": "hint"},
        {"question_id": "q3", "question": "Question 3?", "hint": "hint"},
    ]
    prefill = {"q1": "Answer 1", "q2": "", "q3": "Answer 3"}

    result = ask_questions(console, questions, prefill_answers=prefill)

    assert result[0]["answer"] == "Answer 1"
    assert result[1]["answer"] == ""
    assert result[2]["answer"] == "Answer 3"


def test_prefill_with_fewer_answers():
    """Should use empty string for missing answers."""
    console = Console(record=True)
    questions = [
        {"question_id": "q1", "question": "Question 1?", "hint": "hint"},
        {"question_id": "q2", "question": "Question 2?", "hint": "hint"},
        {"question_id": "q3", "question": "Question 3?", "hint": "hint"},
    ]
    prefill = {"q1": "Answer 1"}

    result = ask_questions(console, questions, prefill_answers=prefill)

    assert len(result) == 3
    assert result[0]["answer"] == "Answer 1"
    assert result[1]["answer"] == ""
    assert result[2]["answer"] == ""
