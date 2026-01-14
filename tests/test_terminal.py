"""Tests for terminal module."""

from unittest.mock import patch, MagicMock

from rich.console import Console

from ui.terminal import State, Terminal
from data.styles import DEFAULT_STYLE


def test_state_enum_has_required_states():
    """State enum should have all required states."""
    assert State.START
    assert State.STYLE_SELECT
    assert State.QUESTIONNAIRE
    assert State.GENERATING
    assert State.DISPLAY
    assert State.BANNER


def test_terminal_initializes_with_defaults():
    """Terminal should initialize with correct default values."""
    terminal = Terminal()

    assert terminal.state == State.START
    assert terminal.style == DEFAULT_STYLE
    assert terminal.qa_transcript == []
    assert terminal.avoid_list == []
    assert terminal.candidates == []


def test_terminal_has_console():
    """Terminal should have a Console instance."""
    terminal = Terminal()
    assert isinstance(terminal.console, Console)


def test_show_start_screen_transitions_to_style_select():
    """show_start_screen should transition state to STYLE_SELECT."""
    terminal = Terminal()
    terminal.console = Console(record=True)

    with patch("ui.terminal.Prompt.ask", return_value=""):
        terminal.show_start_screen()

    assert terminal.state == State.STYLE_SELECT


def test_show_style_selector_transitions_to_questionnaire():
    """show_style_selector should transition state to QUESTIONNAIRE."""
    terminal = Terminal()
    terminal.console = Console(record=True)
    terminal.state = State.STYLE_SELECT

    with patch("ui.terminal.Prompt.ask", return_value="m"):
        terminal.show_style_selector()

    assert terminal.state == State.QUESTIONNAIRE
    assert terminal.style == "m"


def test_run_questionnaire_transitions_to_generating():
    """run_questionnaire should transition state to GENERATING."""
    terminal = Terminal()
    terminal.console = Console(record=True)
    terminal.state = State.QUESTIONNAIRE

    with patch("ui.terminal.ask_questions", return_value=[{"q": "Q?", "a": "A"}]):
        terminal.run_questionnaire()

    assert terminal.state == State.GENERATING
    assert terminal.qa_transcript == [{"q": "Q?", "a": "A"}]


def test_show_generating_transitions_to_start():
    """show_generating should transition state back to START."""
    terminal = Terminal()
    terminal.console = Console(record=True)
    terminal.state = State.GENERATING
    terminal.qa_transcript = [{"q": "Q?", "a": "A"}]

    with patch("ui.terminal.Prompt.ask", return_value=""):
        terminal.show_generating()

    assert terminal.state == State.START
