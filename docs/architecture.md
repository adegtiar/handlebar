# Playa Nickname Booth — Architecture Diagram

## System Overview

```mermaid
flowchart TB
    subgraph UI["Terminal UI Layer"]
        START[Start Screen]
        STYLE[Style Selector]
        QA[Questionnaire Loop]
        SPINNER[Loading Spinner]
        DISPLAY[Candidate Display]
        CMD[Command Handler]
        BANNER[Name Banner]
    end

    subgraph CORE["Core Logic Layer"]
        PB[Prompt Builder]
        PARSER[Response Parser]
        VALIDATOR[Nickname Validator]
    end

    subgraph EXTERNAL["External Services"]
        LLM[LLM Client]
        OPENAI[(OpenAI API)]
    end

    subgraph DATA["Data Stores"]
        QA_DATA[("Q/A Transcript")]
        AVOID[("Avoid List")]
    end

    %% UI Flow
    START --> STYLE
    STYLE --> QA
    QA --> SPINNER
    SPINNER --> DISPLAY
    DISPLAY --> CMD
    CMD -->|pick| BANNER
    CMD -->|reroll| SPINNER
    CMD -->|edit| QA
    CMD -->|quit| START
    BANNER --> START

    %% Core Logic Connections
    QA -->|answers| QA_DATA
    QA_DATA --> PB
    AVOID --> PB
    PB --> LLM
    LLM --> OPENAI
    OPENAI --> LLM
    LLM --> PARSER
    PARSER --> VALIDATOR
    VALIDATOR --> DISPLAY
    VALIDATOR -->|valid names| AVOID
```

## Component Detail

```mermaid
flowchart LR
    subgraph PromptBuilder["Prompt Builder"]
        direction TB
        INST[Instructions Block]
        STYLE_DIR[Style Direction]
        AVOID_BLOCK[Avoid List Block]
        QA_BLOCK[Q/A Transcript]

        INST --> PROMPT
        STYLE_DIR --> PROMPT
        AVOID_BLOCK --> PROMPT
        QA_BLOCK --> PROMPT
        PROMPT[Final Prompt]
    end

    subgraph Parser["Response Parser"]
        direction TB
        RAW[Raw Response]
        JSON_PARSE{JSON Parse OK?}
        JSON_EXTRACT[Extract nicknames array]
        LINE_PARSE[Line-by-line fallback]
        CANDIDATES[Candidates List]

        RAW --> JSON_PARSE
        JSON_PARSE -->|yes| JSON_EXTRACT
        JSON_PARSE -->|no| LINE_PARSE
        JSON_EXTRACT --> CANDIDATES
        LINE_PARSE --> CANDIDATES
    end

    subgraph Validator["Nickname Validator"]
        direction TB
        INPUT[Candidates]
        CHECK_WORDS{1-2 words?}
        CHECK_LEN{3-28 chars?}
        CHECK_CHARS{Valid chars?}
        CHECK_DUP{Not duplicate?}
        VALID[Valid List]
        INVALID[Invalid List]

        INPUT --> CHECK_WORDS
        CHECK_WORDS -->|no| INVALID
        CHECK_WORDS -->|yes| CHECK_LEN
        CHECK_LEN -->|no| INVALID
        CHECK_LEN -->|yes| CHECK_CHARS
        CHECK_CHARS -->|no| INVALID
        CHECK_CHARS -->|yes| CHECK_DUP
        CHECK_DUP -->|no| INVALID
        CHECK_DUP -->|yes| VALID
    end
```

## Data Flow Sequence

```mermaid
sequenceDiagram
    participant U as User
    participant UI as Terminal UI
    participant PB as Prompt Builder
    participant LLM as LLM Client
    participant API as OpenAI API
    participant P as Parser
    participant V as Validator

    U->>UI: Press Enter to start
    U->>UI: Select style (optional)

    loop 5-8 Questions
        UI->>U: Display question
        U->>UI: Type answer (or skip)
    end

    UI->>PB: Q/A list + style + avoid_list
    PB->>LLM: Compiled prompt
    LLM->>API: API request
    API-->>LLM: Raw response
    LLM->>P: Raw text
    P->>V: Candidates list
    V->>UI: Valid + Invalid lists

    UI->>U: Display valid nicknames

    alt User picks a name
        U->>UI: Select number (1-10)
        UI->>U: Display name banner
    else User rerolls
        U->>UI: Press 'r'
        Note over UI,V: Add shown names to avoid_list
        UI->>PB: Same Q/A + updated avoid_list
    else User edits
        U->>UI: Press 'e'
        Note over UI: Return to questionnaire
    end
```

## Module Structure

```
handlebar/
├── src/
│   ├── main.py              # Entry point
│   ├── ui/
│   │   ├── __init__.py
│   │   ├── terminal.py      # Terminal UI controller
│   │   ├── questionnaire.py # Question asking logic
│   │   ├── picker.py        # Candidate display & selection
│   │   └── banner.py        # ASCII name display
│   ├── core/
│   │   ├── __init__.py
│   │   ├── prompt.py        # Prompt builder
│   │   ├── parser.py        # Response parser
│   │   └── validator.py     # Nickname validation
│   ├── llm/
│   │   ├── __init__.py
│   │   └── client.py        # OpenAI SDK wrapper
│   └── data/
│       ├── __init__.py
│       ├── questions.py     # Question bank
│       └── styles.py        # Style mode definitions
├── config/
│   └── settings.py          # API keys, model config
├── docs/
│   └── ...
└── tests/
    └── ...
```

## State Machine

```mermaid
stateDiagram-v2
    [*] --> Start
    Start --> StyleSelect: Enter pressed
    StyleSelect --> Questionnaire: Style chosen

    Questionnaire --> Generating: All questions answered
    Generating --> DisplayCandidates: Valid results (≥1)
    Generating --> Error: No valid results
    Error --> Generating: Auto-retry

    DisplayCandidates --> NameChosen: Pick (1-10)
    DisplayCandidates --> Generating: Reroll (r)
    DisplayCandidates --> Questionnaire: Edit (e)
    DisplayCandidates --> Start: Quit (q)

    NameChosen --> ShowBanner: Display name
    ShowBanner --> Start: Continue to next participant
```