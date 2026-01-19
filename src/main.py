#!/usr/bin/env python3
"""Entry point for the Playa Nickname Booth."""

import argparse
import os
import sys
from pathlib import Path

from dotenv import load_dotenv

from ui.terminal import Terminal


def load_answers(filepath: str) -> list[str]:
    """Load prefill answers from a text file (one per line)."""
    path = Path(filepath)
    if not path.exists():
        raise FileNotFoundError(f"Answers file not found: {filepath}")
    return path.read_text().splitlines()


def main():
    """Run the Playa Nickname Booth application."""
    load_dotenv()

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

    terminal = Terminal(prefill_answers=prefill_answers)
    terminal.run()


if __name__ == "__main__":
    main()
