# Wraith 👻 — A Ghost in Your Terminal

Wraith is an open-source terminal companion that reacts to completed shell commands in the voice of forgotten technologies. It uses a local Ollama model when available, stores event history in SQLite, and falls back to scripted whispers when Ollama is unavailable.

## Features
- Four personalities: GeoCities, Fortran, Deleted File, Unix Daemon.
- Local-first inference through Ollama; no hosted AI API.
- Context-aware categories for failures, tests, Git, installs, infrastructure and destructive operations.
- Local memory with inspect and erase commands.
- Best-effort redaction of common token formats before storage/inference.
- Model output is displayed only, never executed.
- Deterministic fallback lines work without Ollama; generative responses require Ollama and a downloaded model.

## Install on macOS
Install Ollama from https://ollama.com or `brew install ollama`.

Terminal 1: `ollama serve`

Terminal 2:
```bash
ollama pull qwen2.5:3b
cd /path/to/Wraith
python3 -m venv .venv
source .venv/bin/activate
pip install -e .
wraith status
wraith haunt "git push origin main" --ghost geocities
wraith ghosts
```

Enable zsh integration:
```bash
echo 'source "$(wraith hook-path zsh)"' >> ~/.zshrc
source ~/.zshrc
```
Disable at any time: `export WRAITH_ENABLED=0`
Set personality: `export WRAITH_GHOST=fortran`

## Commands
- `wraith init --shell zsh --ghost geocities`
- `wraith haunt "pytest" --status 1`
- `wraith status`
- `wraith ghosts`
- `wraith memory --limit 10`
- `wraith forget`

## Configuration
`WRAITH_ENABLED` (default `1`), `WRAITH_MODEL` (default `qwen2.5:3b`), `WRAITH_OLLAMA_URL` (default `http://127.0.0.1:11434`), `WRAITH_GHOST` (default `geocities`), `WRAITH_DB` (default `~/.wraith/wraith.db`), `WRAITH_TIMEOUT` (default `5` seconds), `WRAITH_EXCLUDE` (comma-separated command substrings), `WRAITH_DEBUG` (default `0`).

## Privacy & safety
Wraith stores command text, exit codes, timestamps, ghost names and responses in a local SQLite database. Common credential patterns are redacted and sensitive prefixes such as `env`, `printenv`, and `export` are ignored. Redaction is best-effort, not a guarantee; review code and exclusions before enabling it in sensitive environments. The shell hook observes completed commands; it does not alter their execution. Wraith does not read or recover deleted files.

## Why open innovation?
After downloading a model, Wraith can generate reactions locally without sending command history to a hosted AI service or requiring a paid API. Its hooks, prompts, event engine and storage are inspectable and modifiable. The fallback mode remains available if Ollama is stopped.

## Tests
`pip install -e ".[dev]"` then `pytest -q`.

## License
MIT. Model weights and Ollama have their own licenses and terms; review them separately.
