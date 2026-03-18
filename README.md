# Playa Nickname Booth

Terminal-based playa name generator.

## Install for MacOS

## Python version
This projects requires python >=3.11
You can use pyenv to manage python versions if you don't have it.
```bash
python --version
brew install pyenv
pyenv install 3.14
pyenv global 3.14
```
Make sure the pyenv python takes precedent in your .zshrc file.

```bash
echo 'export PYENV_ROOT="$HOME/.pyenv"' >> ~/.zshrc
echo '[[ -d $PYENV_ROOT/bin ]] && export PATH="$PYENV_ROOT/bin:$PATH"' >> ~/.zshrc
echo 'eval "$(pyenv init - zsh)"' >> ~/.zshrc
```

```bash
python3 -m venv .venv
source .venv/bin/activate
pip install -e .
```

## Configure
Need to include an API key from OpenAI and export it as an env variable. This is managed through the .env file.
cp .env.example .env
Edit the line for CLAUDE_API_KEY to add your key.


## Run

```bash
handlebar
```

If you have dependencies installed already and don't want to use venv, you can
also simply run:
```bash
./src/main.py
```

## Install ollama for local models
```bash
brew install ollama
brew services start ollama
ollama pull llama3.2
ollama list
```

Then in .env:
LLM_PROVIDER=ollama

## Test

```bash
pytest
```

## Usage

1. Press Enter to start
2. Select a style (mixed, mythic, chaotic, cozy)
3. Answer the questions (or press Enter to skip)
4. Get your playa name! [NOTE: not supported yet]