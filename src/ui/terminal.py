"""Terminal UI controller for the Playa Nickname Booth."""

import json
import logging
from enum import Enum, auto
from typing import Optional

log = logging.getLogger(__name__)

from session_logging import SessionLogger

from prompt_toolkit import prompt as pt_prompt
from rich.console import Console
from rich.panel import Panel
from rich.syntax import Syntax

from core.prompt import build_prompt
from data.questions import QUESTIONS
from data.styles import DEFAULT_STYLE, STYLES
from llm import get_client, LLMError
from ui.feedback import ask_feedback
from ui.questionnaire import ask_questions


class State(Enum):
    """Application states."""

    START = auto()
    STYLE_SELECT = auto()
    QUESTIONNAIRE = auto()
    GENERATING = auto()
    FEEDBACK = auto()
    DISPLAY = auto()
    BANNER = auto()


class Terminal:
    """Terminal UI controller managing the application flow."""

    def __init__(
        self,
        prefill_answers: Optional[dict[str, str]] = None,
        logger: Optional[SessionLogger] = None,
    ):
        self.console = Console()
        self.state = State.START
        self.style = DEFAULT_STYLE
        self.qa_transcript: list[dict] = []
        self.avoid_list: list[str] = []
        self.candidates: list[str] = []
        self.current_session_id: Optional[int] = None
        self.prefill_answers = prefill_answers
        self.logger = logger

    def show_start_screen(self):
        """Display the start screen."""
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
        self.qa_transcript = ask_questions(
            self.console, QUESTIONS, prefill_answers=self.prefill_answers
        )
        self.state = State.GENERATING

    def show_generating(self):
        """Show generating state and call LLM."""
        self.console.print()

        # Build prompt
        prompt_messages = build_prompt(
            self.qa_transcript, self.style, self.avoid_list or None
        )

        # Try to call LLM
        try:
            client = get_client()
            self.console.print(
                Panel(
                    "[bold yellow]Generating your playa names...[/bold yellow]",
                    border_style="yellow",
                )
            )
            self.console.print()

            response = client.generate(prompt_messages)

            self.console.print("[bold green]LLM Response:[/bold green]\n")
            # Try to pretty-print JSON response
            try:
                response_obj = json.loads(response)
                response_json = json.dumps(response_obj, indent=2)
                self.console.print(Syntax(response_json, "json", theme="monokai", word_wrap=True))

                nicknames = response_obj.get("nicknames", [])
                self.candidates = nicknames

                if self.logger:
                    logged_transcript = [
                        {"question_id": qa["question_id"], "answer": qa["answer"]}
                        for qa in self.qa_transcript
                    ]
                    self.current_session_id = self.logger.log_session(
                        style=self.style,
                        qa_transcript=logged_transcript,
                        nicknames=nicknames,
                        llm_response_raw=response,
                    )
            except json.JSONDecodeError:
                self.console.print(response)

        except LLMError as e:
            # No API key or API error - show prompt instead
            self.console.print(
                Panel(
                    "[bold yellow]Generating your playa names...[/bold yellow]\n\n"
                    f"[dim]{e}[/dim]",
                    border_style="yellow",
                )
            )
            self.console.print()
            self.console.print("[bold]Prompt that would be sent to LLM:[/bold]\n")

            for msg in prompt_messages:
                self.console.print(f"[bold cyan]{msg['role'].upper()}:[/bold cyan]")
                try:
                    content_obj = json.loads(msg["content"])
                    content_json = json.dumps(content_obj, indent=2)
                    self.console.print(Syntax(content_json, "json", theme="monokai", word_wrap=True))
                except (json.JSONDecodeError, TypeError):
                    self.console.print(msg["content"])
                self.console.print()

        if self.candidates:
            self.state = State.FEEDBACK
        else:
            self.console.print()
            pt_prompt("Press Enter to continue: ")
            self.state = State.START

    def show_feedback(self):
        """Show optional feedback form after nickname generation."""
        feedback_data = ask_feedback(
            self.console,
            nicknames=self.candidates,
        )

        if feedback_data is not None and self.logger and self.current_session_id:
            self.logger.log_feedback(
                session_id=self.current_session_id,
                **feedback_data,
            )

        self.state = State.START

    def run(self):
        """Main application loop."""
        # Skip to questionnaire if prefill answers provided
        if self.prefill_answers:
            self.state = State.QUESTIONNAIRE

        try:
            while True:
                log.info("[%s] State starting: %s", self.current_session_id or "N/A", self.state.name)
                if self.state == State.START:
                    self.show_start_screen()
                elif self.state == State.STYLE_SELECT:
                    self.show_style_selector()
                elif self.state == State.QUESTIONNAIRE:
                    self.run_questionnaire()
                elif self.state == State.GENERATING:
                    self.show_generating()
                elif self.state == State.FEEDBACK:
                    self.show_feedback()
                else:
                    self.state = State.START
                log.info("[%s] State finished: %s", self.current_session_id or "N/A", self.state.name)
        except KeyboardInterrupt:
            log.info("Interrupted by user")
            self.console.print("\n[dim]Goodbye![/dim]")
