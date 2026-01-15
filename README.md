# Playa Nickname Booth

Terminal-based playa name generator.

## Install

```bash
python3 -m venv .venv
source .venv/bin/activate
pip install -e .
```

## Configure
Need to include an API key from OpenAI and export it as an env varaible:
export OPENAI_API_KEY="sk-..."

## Run

```bash
handlebar
```

If you have dependencies installed already and don't want to use venv, you can
also simply run:
```bash
./src/main.py
```

## Test

```bash
pytest
```

## Usage

1. Press Enter to start
2. Select a style (mixed, mythic, chaotic, cozy)
3. Answer the questions (or press Enter to skip)
4. Get your playa name! [NOTE: not supported yet]