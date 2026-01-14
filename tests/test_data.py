"""Tests for data modules."""

from data.questions import QUESTIONS
from data.styles import DEFAULT_STYLE, STYLES


def test_questions_have_required_keys():
    """Each question should have 'question' and 'hint' keys."""
    for q in QUESTIONS:
        assert "question" in q
        assert "hint" in q


def test_questions_not_empty():
    """Should have at least one question."""
    assert len(QUESTIONS) > 0


def test_styles_have_required_keys():
    """Each style should have name, description, and prompt_modifier."""
    for key, style in STYLES.items():
        assert "name" in style
        assert "description" in style
        assert "prompt_modifier" in style


def test_default_style_exists():
    """DEFAULT_STYLE should be a valid style key."""
    assert DEFAULT_STYLE in STYLES
