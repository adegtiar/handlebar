"""Terminal UI controller for the Playa Nickname Booth."""

from enum import Enum, auto
from typing import Optional

from prompt_toolkit import prompt as pt_prompt
from rich.console import Console
from rich.panel import Panel

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
                "[dim]LLM client not yet implemented.[/dim]\n"
                "[dim]Q/A transcript collected:[/dim]",
                border_style="yellow",
            )
        )
        self.console.print()

        for qa in self.qa_transcript:
            if qa["a"]:
                self.console.print(f"[cyan]Q:[/cyan] {qa['q']}")
                self.console.print(f"[green]A:[/green] {qa['a']}")
                self.console.print()

        self.console.print(f"\n[dim]Style: {STYLES[self.style]['name']}[/dim]")
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
