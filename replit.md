# Playa Nickname Booth

## Overview

Playa Nickname Booth is a terminal-based nickname generator for Burning Man participants. Users go through an interactive questionnaire, select a style, and receive AI-generated playa names via OpenAI's API. The application uses a state machine to manage the flow: START → STYLE_SELECT → QUESTIONNAIRE → GENERATING → DISPLAY → BANNER, then loops back.

The project is a Python CLI application installed as a package (entry point: `handlebar`). It uses Rich for terminal styling, prompt_toolkit for input handling, and OpenAI for nickname generation.

## User Preferences

Preferred communication style: Simple, everyday language.

## System Architecture

### State Machine Pattern
The application is built around a finite state machine defined in `src/ui/terminal.py`. States are: START, STYLE_SELECT, QUESTIONNAIRE, GENERATING, FEEDBACK, DISPLAY, BANNER. Each state maps to a handler method on the `Terminal` class that processes user interaction and transitions to thte.

### Layer Organization

- **UI Layer (`src/ui/`)**: Terminal controller (`terminal.py`) manages the state machine and overall flow. `questionnaire.py` handles Q&A collection. `feedback.py` collects optional post-generation feedback. Uses Rich library for styled terminal output and prompt_toolkit for user input.
- **Data Layer (`src/data/`)**: Static data definitions. `questions.py` contains the question bank (7 questions, each with `question_id`, `question`, and `hint`). `styles.py` defines 5 style modes (mixed, mythic, chaotic, cozy, whimsical) with prompt modifiers. Default style is "w" (whimsical).
- **Core Logic (`src/core/`)**: `prompt.py` contains the system prompt and prompt builder for constructing LLM requests. Includes detailed rules for nickname generation (1-2 words, 3-28 chars, Title Case, letters/apostrophes/hyphens only).
- **LLM Client (`src/llm/`)**: Protocol-based design with `LLMClient` protocol in `base.py` and `OpenAIClient` implementation in `openai_client.py`. Factory function `get_client()` returns the configured client. Uses OpenAI's chat completions API with model `gpt-5.2`.
- **Session Logging (`src/session_logging/`)**: SQLAlchemy-based session logger using SQLite. Tracks sessions (style, Q&A transcript, nicknames, raw LLM response) and feedback in separate tables.

### Key Data Structures
- **Q/A Transcript**: `[{"q": "question text", "a": "user answer"}, ...]`
- **Questions**: Each has `question_id`, `question`, and `hint` fields
- **Styles**: Keyed by single letter (m/y/c/z/w), each with `name`, `description`, `prompt_modifier`

### Package Structure
The project is installable via `pip install -e .` and provides a `handlebar` CLI entry point. The `src/` directory is the package root — imports use module names directly (e.g., `from data.questions import QUESTIONS`, not `from src.data`).

### Known Issues
- `src/main.py` has unresolved git merge conflict markers (between HEAD and commit 3b26816) — these need to be resolved. The conflict is around imports of `logging`, `osnd `sys`.
- Some files appear truncated in the repository snapshot (e.g., `session_logger.py`, `feedback.py`, `terminal.py`, `questionnaire.py`, `prompt.py`).

### Testing
Tests are in `tests/` and use pytest. They test data structure validity, questionnaire behavior (mocking prompt_toolkit input), and terminal state transitions. Run with `pytest`.

### Configuration
- Uses `python-dotenv` to load `.env` file for environment variables
- Supports `--answers`/`-a` CLI flag to pass a JSON file with prefilled answers for non-interactive mode
- Logging goes to `logs/app.log` (file-based)
- Pyright is configured via `pyrightconfig.json` with `src` in `extraPaths`

## External Dependencies

### OpenAI API
- **Purpose**: Nickname generation via chat completions
- **Model**: `gpt-5.2`
- **Auth**: `OPENAI_API_KEY` environment variable (required)
- **SDK**: `openai` Python package

### Python Libraries
- **Rich**: Terminal UI styling (panels, syntax highlighting, formatted output)
- **prompt_toolkit**: Interactive user input with better UX than built-in `input()`
- **SQLAlchemy**: ORM for session logging to SQLite database
- **python-dotenv**: Loading environment variables from `.env` file
- **pytest**: Test framework

### Data Storage
- **SQLite** (via SQLAlchemy): Local session logging with `sessions` and `feedback` tables. No external database required.
- **JSON files**: Example answer files in `answers/` directory for testing/demo purposes
