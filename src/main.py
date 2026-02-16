#!/usr/bin/env python3
"""Entry point for the Playa Nickname Booth."""

import argparse
import json
import logging
import os
import sys
from pathlib import Path

from dotenv import load_dotenv

from session_logging import SessionLogger
from ui.terminal import Terminal


def load_answers(filepath: str) -> dict[str, str]:
    """Load prefill answers from a JSON file mapping question_id to answer."""
    path = Path(filepath)
    if not path.exists():
        raise FileNotFoundError(f"Answers file not found: {filepath}")
    return json.loads(path.read_text())


def setup_logging():
    """Configure file-based logging for error visibility in Replit console."""
    log_dir = Path(__file__).resolve().parent.parent / "logs"
    log_dir.mkdir(exist_ok=True)
    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
        handlers=[logging.FileHandler(log_dir / "app.log")],
    )


def main():
    """Run the Playa Nickname Booth application."""
    setup_logging()
    log = logging.getLogger(__name__)

    load_dotenv()

    provider = os.getenv("LLM_PROVIDER", "openai").lower()
    if provider != "ollama":
        api_key = os.getenv("OPENAI_API_KEY")
        if not api_key:
            print("Error: OPENAI_API_KEY not found. Please set it in .env file.")
            sys.exit(1)

    parser = argparse.ArgumentParser(description="Playa Nickname Booth")
    parser.add_argument(
        "-a", "--answers",
        help="Path to text file with prefilled answers (one per line)",
    )
    args = parser.parse_args()

    prefill_answers = None
    if args.answers:
        prefill_answers = load_answers(args.answers)

    session_logger = SessionLogger()
    terminal = Terminal(prefill_answers=prefill_answers, logger=session_logger)
    try:
        terminal.run()
    except Exception:
        log.exception("Terminal crashed")
        sys.exit(1)


if __name__ == "__main__":
    main()
