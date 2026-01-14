"""Terminal UI controller for the Playa Nickname Booth."""

import json
from enum import Enum, auto
from typing import Optional

from prompt_toolkit import prompt as pt_prompt
from rich.console import Console
from rich.panel import Panel
from rich.syntax import Syntax

from core.prompt import build_prompt
from data.questions import QUESTIONS
from data.styles import DEFAULT_STYLE, STYLES
from ui.questionnaire import ask_questions


class State(Enum):
    """Application states."""

    START = auto()
    STYLE_SELECT = auto()
    QUESTIONNAIRE = auto()
    GENERATING = auto()
    DISPLAY = auto()
    BANNER = auto()


class Terminal:
    """Terminal UI controller managing the application flow."""

    def __init__(self, prefill_answers: Optional[list[str]] = None):
        self.console = Console()
        self.state = State.START
        self.style = DEFAULT_STYLE
        self.qa_transcript: list[dict] = []
        self.avoid_list: list[str] = []
        self.candidates: list[str] = []
        self.prefill_answers = prefill_answers

    def clear(self):
        """Clear the terminal screen."""
        self.console.clear()

    def show_start_screen(self):
        """Display the start screen."""
        self.clear()
        self.console.print()
        self.console.print(
            Panel(
                "[bold magenta]PLAYA NICKNAME BOOTH[/bold magenta]\n\n"
                "[white]Get your playa name![/white]",
                border_style="magenta",
                padding=(1, 4),
            )
        )
        self.console.print()
        pt_prompt("Press Enter to begin: ")
        self.state = State.STYLE_SELECT

    def show_style_selector(self):
        """Display style selection options."""
        self.clear()
        self.console.print()
        self.console.print("[bold]Choose your vibe:[/bold]\n")

        for key, style in STYLES.items():
            self.console.print(
                f"  [bold cyan]\\[{key}][/bold cyan] {style['name'].title()} - [dim]{style['description']}[/dim]"
            )

        self.console.print()
        while True:
            choice = pt_prompt(f"Style [{DEFAULT_STYLE}]: ") or DEFAULT_STYLE
            if choice in STYLES:
                break
            self.console.print(f"[red]Invalid choice. Use: {', '.join(STYLES.keys())}[/red]")
        self.style = choice
        self.state = State.QUESTIONNAIRE

    def run_questionnaire(self):
        """Run the questionnaire flow."""
        self.clear()
        self.qa_transcript = ask_questions(
            self.console, QUESTIONS, prefill_answers=self.prefill_answers
        )
        self.state = State.GENERATING

    def show_generating(self):
        """Show generating state (placeholder for LLM integration)."""
        self.clear()
        self.console.print()
        self.console.print(
            Panel(
                "[bold yellow]Generating your playa names...[/bold yellow]\n\n"
                "[dim]LLM client not yet implemented.[/dim]",
                border_style="yellow",
            )
        )
        self.console.print()

        # Build and display the prompt
        prompt_messages = build_prompt(
            self.qa_transcript, self.style, self.avoid_list or None
        )

        self.console.print("[bold]Prompt that would be sent to LLM:[/bold]\n")

        # Pretty print each message
        for msg in prompt_messages:
            self.console.print(f"[bold cyan]{msg['role'].upper()}:[/bold cyan]")

            # Try to parse content as JSON for prettier display
            try:
                content_obj = json.loads(msg["content"])
                content_json = json.dumps(content_obj, indent=2)
                self.console.print(Syntax(content_json, "json", theme="monokai", word_wrap=True))
            except (json.JSONDecodeError, TypeError):
                # Plain text content - display as-is with word wrap
                self.console.print(msg["content"])

            self.console.print()

        self.console.print()
        pt_prompt("Press Enter to return to start: ")
        self.state = State.START

    def run(self):
        """Main application loop."""
        # Skip to questionnaire if prefill answers provided
        if self.prefill_answers:
            self.state = State.QUESTIONNAIRE

        try:
            while True:
                if self.state == State.START:
                    self.show_start_screen()
                elif self.state == State.STYLE_SELECT:
                    self.show_style_selector()
                elif self.state == State.QUESTIONNAIRE:
                    self.run_questionnaire()
                elif self.state == State.GENERATING:
                    self.show_generating()
                else:
                    self.state = State.START
        except KeyboardInterrupt:
            self.console.print("\n[dim]Goodbye![/dim]")
