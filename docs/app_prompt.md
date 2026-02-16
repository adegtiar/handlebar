  Build a terminal-based "Playa Name Booth" — a Burning Man nickname
  generator that runs as a single-user terminal kiosk in Python. It
  loops continuously for one participant after another and can be served
  in a web browser via ttyd.

  High-level flow

  The app is a looping state machine: START → STYLE_SELECT → QUESTIONNAIRE →
   GENERATING → DISPLAY → FEEDBACK → (back to START). It runs forever until
  Ctrl-C.

  Tech stack

  - Python 3.11+, installable via pip install -e .
  - Rich for styled terminal output (gradients, rules, colored text)
  - prompt_toolkit for user input (not input())
  - pyfiglet for ASCII art title screen
  - OpenAI Python SDK for LLM calls (chat completions)
  - SQLAlchemy (with SQLite locally, Postgres via DATABASE_URL env var) for
  session logging
  - python-dotenv for env config
  - Entry point: src/main.py, run directly as ./src/main.py

  Project structure

  src/
    main.py              # argparse entry point, loads .env, wires up
  Terminal + SessionLogger
    ui/
      terminal.py        # State machine controller (State enum, Terminal
  class with run() loop)
      questionnaire.py   # Interactive Q&A collection (also supports prefill
   mode via --answers JSON file)
      feedback.py        # Optional post-generation feedback form (favorite
  name, helpful/unhelpful questions, suggestions)
      theme.py           # Centralized color palette, gradient definitions,
  utility functions
    data/
      questions.py       # Question bank (list of dicts with question_id,
  question, hint)
      styles.py          # Style mode definitions (dict mapping key →
  name/description/prompt_modifier)
    llm/
      __init__.py        # Factory: get_client() returns OpenAI or Ollama
  based on LLM_PROVIDER env var
      base.py            # Protocol class LLMClient with generate(messages)
  -> str, plus LLMError empt.py          # SYSTEM_PROMPT constant + build_prompt() that
  assembles messages array
      openai_client.py   # OpenAI implementation
      ollama_client.py   # Ollama implementation (uses OpenAI SDK pointed at
   localhost:11434/v1)
    session_logging/
      __init__.py
      session_logger.py  # SQLAlchemy tables (sessions + feedback),
  SessionLogger class
      __main__.py        # CLI dump tool: python -m session_logging
  [session_id]

  Visual design

  Desert sunset + neon playa aesthetic:
  - Color palette: deep orange, gold, coral, hot pink, electric teal, playa
  purple, night blue, warm sand
  - Three gradient ramps (sunset, neon, fire) applied per-character across
  text including multi-line ASCII art
  - Rules use ~ characters in orange (like desert heat shimmer)
  - Title screen: "PLAYA NAME" and "BOOTH" rendered in pyfiglet slant font
  (or small_slant for narrow terminals), with sunset and fire gradients
  respectively
  - Generated nicknames displayed with neon gradient distributed across the
  list items

  Questions (7 total)

  1. "Optional: what's your real name or an alias, for inspiration?"
  2. "What's your vibe right now? Describe it like a movie scene."
  3. "What brings you joy?"
  4. "If you had a side-quest tonight, what would it be?"
  5. "What animal do you become at 2am?"
  6. "What's something you're inexplicably good at that has no practical
  use?"
  7. "Describe your most legendary night in 3 words"

  Each has a hint shown in italic sand color. User can skip any by pressing
  Enter.

  Style modes (5)

  - [m] Mixed — "Mix playful, mythical, and cozy elements. Be creative and
  unexpected."
  - [y] Mythic — "Use mythical, legendary, and epic language. Think ancient
  heroes and cosmic forces."
  - [c] Chaotic — "Be chaotic, absurd, and unexpected. Embrace weirdness and
   surprise."
  - [z] Cozy — "Use warm, gentle, and comforting language. Think soft
  blankets and warm drinks."
  - [w] Whimsical (default) — "Be whimsical, playful, and unexpected. Think
 es."

  LLM prompt

  System message instructs the LLM:

  ```
  You are a playa name generator for Burning Man participants. Your job is to
  distill a participant's essence into a memorable name they'll carry on the
  playa. Generate creative, memorable nicknames based on the participant's
  answers.

  ## Output Format
  Respond with valid JSON only:
  {"nicknames": ["Name One", "Nametwo", ...]}

  ## Rules
  - Generate exactly 7 nickname candidates
  - Each nickname: 1-2 words, Title Case
  - Length: 3-28 characters total
  - Allowed characters: letters, apostrophes, hyphens
  - Be creative, playful, and evocative
  - If a real name is given, use it as a base for some suggestions. You can use parts of it, especially the front, or something that rhymes with it
  - No more that 1/4 are alliterations

  ## What Makes a Great Playa Name
  - Captures a contradiction, tension, or unexpected quality
  - Sounds good shouted across a dusty dance floor at 4am
  - Evokes imagery, sensation, or story preferably in 1 word (or 2 words max)
  - Feels like it could only belong to THIS person
  - Has rhythm and mouth-feel (alliteration, consonance, unexpected pairings)
  - Short
  - Mostly stick with one word
  - Action
  - Thing
  - Trait
  - Ironic
  - Funny

  ## Examples
  Here are some examples and why there are good:
  Nurse Noise - Alliteration, reflects her DJ interest
  Flutter - Verb, reflects her active nature, and high energy
  Danimal - Takes his name, Dan, and combines it with animal
  Shimmer - Nice quality, gives a ethereal vibe
  Maculate - Uses last name but converts it from immaculate
  Badazzler - Takes a funny decor meme and adds bad. There's a story behind it.
  Yardsale - Went to burningmand and lost all his stuff (wallet, keys, phone)
  Sunshine - fun, positive, good vibes
  Chuckles - funny, ironic because his stoic and grumpy (sometimes)
  Sir Bear - Big furry guy with big presence
  Captain T-Bag - funny name, maybe there is a story
  ```

  User message is JSON with style (the modifier text), answers
  (question→answer map, only answered ones), and optionally avoid_names
  (accumulated from rerolls).

  Response handling

  - `json.loads(response)` → extract `nicknames` list → store as candidates
  - On JSON parse failure: print raw response, return to START
  - Empty nicknames list: show raw JSON as debug output
  - No runtime validation — names are displayed as-is, system prompt relied
    upon for quality

  Key behaviors

  - Reroll: From the display screen, user can press 'r' to regenerate.
  Previous nicknames get added to an avoid_list sent to the LLM.
  - Prefill mode: ./src/main.py --answers path/to/answers.json skips
  interactive input, loads answers by question_id, and shows them as
  prefilled.
  - LLM error fallback: If the API keys missing or the call fails, display
   the prompt that would have been sent, then return to START.
  - Feedback form (optional after display): asks for favorite name
  (single-select from list), which questions were most/least helpful
  (multi-select), free-text suggested questions, and self-suggested playa
  name.

  Session logging

  SQLAlchemy with two tables:
  - sessions: session_id (auto PK), process_id (UUID per app run), timestamp
   (UTC ISO), style, qa_transcript (JSON), nicknames (JSON),
  llm_response_raw (text)
  - feedback: feedback_id (auto PK), session_id (FK), timestamp,
  favorite_name, helpful_questions (JSON list of question_ids),
  unhelpful_questions (JSON), suggested_questions, self_suggested_name

  SQLite with WAL mode locally. Supports Postgres via DATABASE_URL env var.
  Includes a dump_sessions() method and python -m session_logging CLI for
  inspecting data.

  ttyd deployment

  The app can be served as a web-accessible terminal kiosk via ttyd.
  Launch script at `scripts/start_server.sh`. Key flags: `-W` (writable
  input from browser), `-t fontSize=32` (kiosk-sized text), `-p PORT`.
  On Replit, port 5000 is mapped to external port 80 for public access.

  Environment variables

  - OPENAI_API_KEY — required unless using Ollama
  - LLM_PROVIDER — "openai" (default) or "oll
  - OLLAMA_HOST — defaults to http://localhost:11434/v1
  - OLLAMA_MODEL — defaults to llama3.2
  - DATABASE_URL — optifor Postgres instead of local SQLite

  Edge cases

  - Avoid-list accumulates across rerolls within a session (never resets)
  - Session logging never crashes the app — all DB ops wrapped in try/except
  - `process_id` is a UUID generated once per app launch, shared across all
    sessions in that run
  - Logged `qa_transcript` is stripped to `{question_id, answer}` only (no
    question text)
  - No external assets — all visuals generated at runtime (pyfiglet, Rich
    styling)