# Playa Nickname Booth (Terminal) — Architecture & Flow

This document describes the end-to-end flow for a terminal-based “playa name” generator:
**ask questions → compile prompt → call GPT via SDK → validate/filter → display → choose / reroll**.

---

## Goals

- Collect freeform user input (typed or transcribed) quickly in a terminal.
- Generate a list of candidate nicknames using a GPT model.
- **Validate results by filtering invalid items. Accept the response if at least 1 valid nickname remains.**
- Provide a simple selection and reroll loop.

---

## Core Components

1. **Terminal UI (Questionnaire + Picker)**
   - Collects Q/A pairs
   - Displays candidate nicknames
   - Accepts commands (pick, reroll, edit answers, quit)

2. **Prompt Builder**
   - Converts Q/A pairs into a single model request
   - Includes strict output rules (e.g., “Adjective Noun”, Title Case)

3. **LLM Client**
   - Makes a single SDK call (OpenAI Responses API)
   - Returns raw model output

4. **Parser**
   - Extracts nicknames from the model output (ideally JSON; fallback: parse lines)

5. **Validator (Filter)**
   - Filters out invalid nicknames (format/banned words/duplicates)
   - Accepts if **≥ 1** remain

---

## Data Structures

### Q/A Transcript
Represent as a list of items in order:

```json
[
  {"q": "What's your vibe right now? Describe it like a movie scene.", "a": "Foggy neon boardwalk..."},
  {"q": "If you had a side-quest tonight, what would it be?", "a": "Repair someone's bike light"},
  ...
]
```

### Generation Request Context
A simple object passed between modules:

```json
{
  "style_mode": "mixed",
  "qa": [...],
  "avoid_list": ["Neon Moth", "Dusty Lantern"]
}
```

### Generation Result
```json
{
  "raw_text": "...",
  "candidates": ["Neon Moth", "Static Wrench", ...],
  "valid": ["Neon Moth", "Static Wrench"],
  "invalid": ["Cool Dude", "Neon-Moth!!"]
}
```

---

## Terminal Flow (User Experience)

### 1) Start Screen
- Prompt:
  - “Press Enter to get named”
  - Optional style shortcut in a single line (still simple): `Style [m]ixed / [y]mythic / [c]chaotic / [z]cozy`
- User presses Enter or chooses style key.

### 2) Questionnaire Loop
- Ask **5–8** questions.
- For each question:
  - Display question + example answer hint.
  - Read freeform answer.
  - Allow blank answer (Enter) to skip.

**Store as ordered list of Q/A pairs.**

### 3) Generate
- Show “Generating…” spinner/status line.
- Build prompt from:
  - Instruction block (strict output requirements)
  - Style mode (if you use it)
  - Q/A transcript
  - Avoid list (if rerolling)

### 4) Display Candidates
- Show list (numbered):
  - `1) Neon Moth`
  - `2) Static Wrench`
  - …

### 5) Command Loop
Accept single-key or simple commands:

- `1-10` → pick a nickname
- `r` → reroll (same answers; add previous outputs to avoid list)
- `e` → edit answers (jump back to questionnaire)
- `q` → quit / restart

On pick:
- Display chosen name prominently (ASCII banner / large text).
- Return to start screen for next participant.

---

## Prompt Builder

### Input
- `qa`: list of question/answer objects
- `style_mode`: string (e.g., `mixed`, `mythic`, `chaotic`, `cozy`)
- `avoid_list`: names to avoid on reroll

### Output (Conceptual)
A single string (or structured `input` payload) that includes:

1. Role/behavior instruction (what the model is)
2. Strict output format requirements:
   - **Return exactly 10** candidates (the validator will filter later)
   - Each candidate is **two words**: `Adjective Noun`
   - Title Case
   - No real name, no insults, no protected traits, no diagnostics
3. Style direction (if any)
4. “Avoid these previous results: …” (on reroll)
5. The Q/A transcript

**Recommendation for reliability:** ask for **JSON output** (array of strings).

Example requirement block:

- Output must be JSON:
  - `{"nicknames": ["Neon Moth", "Static Wrench", ...]}`
- If you cannot comply, output your best effort JSON anyway.

---

## LLM Client (SDK Call)

### Request
- `model`: your chosen GPT model
- `input`: compiled prompt (or structured fields if you prefer)
- `temperature`: moderate (e.g., 0.8) for creativity
- `max_output_tokens`: enough for JSON + 10 names (small)

### Response
- Capture:
  - `raw_text` (or parsed JSON if supported by your SDK wrapper)

---

## Parser

### Preferred: JSON Parsing
If model output is JSON:
- Parse and read `nicknames` as list of strings.

### Fallback: Line Parsing
If JSON parse fails:
- Split on newlines.
- Strip numbering like `1)` / `1.`
- Keep non-empty lines as candidates.

---

## Validation (Filter-Only, Accept If ≥ 1)

**Goal:** filter invalid entries, do not fail the entire generation unless *everything* is invalid.

### Candidate Validation Rules (suggested defaults)
- **Two words only** (split on whitespace → exactly 2 tokens)
- Title-ish casing (not strictly required, but recommended)
- Allowed characters: letters, apostrophe, hyphen (optional)
- Length bounds: e.g., 3–28 characters
- Deduplicate case-insensitively
- Filter banned words (camp-defined list)

### Behavior
1. Start with parsed `candidates` list.
2. For each candidate:
   - Normalize whitespace.
   - Validate format.
   - If invalid → discard into `invalid` list.
   - If valid → add to `valid` list if not a duplicate.
3. **If `valid` has at least 1 item, accept.**
4. If `valid` is empty:
   - Return a friendly error state to UI and automatically trigger reroll **or**
   - Show “No valid names produced—press `r` to try again.”
   - (Choose whichever feels best for booth flow.)

---

## Reroll Flow

When the user presses `r`:
1. Append previously shown valid candidates (or the chosen subset) to `avoid_list`.
2. Rebuild prompt with the same Q/A + avoid list.
3. Call LLM again.
4. Parse → validate → display.

**Tip:** keep avoid list bounded (e.g., last 30 names) to avoid giant prompts.

---

## End-to-End Sequence (Happy Path)

1. **UI**: Start → choose style (optional) → begin
2. **UI**: Ask questions → collect `qa[]`
3. **Prompt Builder**: `qa[]` (+ style, avoid_list) → `prompt`
4. **LLM Client**: `prompt` → `raw_output`
5. **Parser**: `raw_output` → `candidates[]`
6. **Validator**: `candidates[]` → `valid[]` (filter invalid)
7. **UI**: Display `valid[]` (if ≥ 1)
8. **UI**: User picks or rerolls
9. **UI**: On pick → confirm → restart for next participant

---

## Minimal Function Interfaces

```text
ask_questions(questions) -> qa_list

build_prompt(qa_list, style_mode, avoid_list) -> prompt_string

call_llm(prompt_string) -> raw_text

parse_candidates(raw_text) -> candidates_list

filter_valid(candidates_list, banned_words) -> valid_list, invalid_list

display_and_choose(valid_list) -> action
  where action ∈ {("pick", name), ("reroll", None), ("edit", None), ("quit", None)}
```

---

## Notes for Robust Booth Operation

- Keep questions short; encourage 1–2 sentence answers.
- Always allow “skip” (blank answer).
- Never block the booth on strict formatting; rely on **filtering**.
- Prefer “fast loop” over perfect results:
  - If only 1–3 valid nicknames remain, still show them.
  - Provide reroll as the escape hatch.
