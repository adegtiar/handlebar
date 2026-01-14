# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Commands

```bash
# Install dependencies
pip install -e .

# Run the application
./src/main.py
```

## Architecture

Playa Nickname Booth is a terminal-based nickname generator for Burning Man participants. It collects user input, generates nicknames via LLM, validates results, and displays them.

### State Machine Flow

START → STYLE_SELECT → QUESTIONNAIRE → GENERATING → DISPLAY → BANNER → (loops back to START)

### Layers

- **UI Layer** (`src/ui/`): Terminal controller with Rich library styling. `terminal.py` manages state machine, `questionnaire.py` handles Q&A collection.
- **Data Layer** (`src/data/`): Question bank (8 questions) and style definitions (mixed, mythic, chaotic, cozy).
- **Core Logic** (planned in `src/core/`): Prompt builder, response parser, nickname validator.
- **LLM Client** (planned in `src/llm/`): OpenAI API integration.

### Key Data Structures

Q/A transcript: `[{"q": "question text", "a": "user answer"}, ...]`

Validation rules: 1-2 words, 3-28 chars, letters/apostrophes/hyphens only, no duplicates.