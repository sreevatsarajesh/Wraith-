# Wraith 👻

**A haunted terminal powered by a local open-weight model.** Wraith watches completed shell commands, reacts in character, and can keep a small local memory of your sessions.

- Works with `zsh` and `bash`
- Uses Ollama for local inference (no hosted AI API)
- Ghost personalities: `geocities`, `fortran`, `deleted-file`
- Local SQLite event history
- Safety-first: never executes model output; command text is not sent anywhere except your local Ollama server

> Prototype note: Wraith records command text and exit status locally when enabled. Review your shell history/privacy needs before enabling it on shared machines. Secrets can appear in command arguments, so use `WRAITH_ENABLED=0` to disable it at any time.

## Quick start (macOS / Linux)

### 1. Install Ollama and download a model
Install Ollama from https://ollama.com, then run:

```bash
ollama pull qwen2.5:3b
ollama serve
```

If Ollama is already running, you can skip `ollama serve`. You can override the model with `WRAITH_MODEL`.

### 2. Install Wraith

```bash
python3 -m venv .venv
source .venv/bin/activate
pip install -e .
wraith init --shell zsh --ghost geocities
```

For bash, use `--shell bash`.

### 3. Enable the shell hook
The init command prints the exact line to add to your `~/.zshrc` or `~/.bashrc`. Add it, then restart the terminal or source your rc file.

For zsh, the line is:

```bash
source "$(wraith hook-path zsh)"
```

For bash:

```bash
source "$(wraith hook-path bash)"
```

The hook only observes commands after they finish. To disable temporarily:

```bash
export WRAITH_ENABLED=0
```

### 4. Test without a shell hook

```bash
wraith haunt "git push origin main" --status 0 --ghost geocities
wraith status
wraith memory --limit 10
```

## Commands

```text
wraith init [--shell zsh|bash] [--ghost geocities|fortran|deleted-file]
wraith haunt "command text" [--status N] [--ghost NAME]
wraith status
wraith memory [--limit N]
wraith forget
wraith hook-path zsh|bash
```

## Configuration

| Variable | Default | Purpose |
|---|---|---|
| `WRAITH_ENABLED` | `1` | Set to `0` to disable shell observation |
| `WRAITH_MODEL` | `qwen2.5:3b` | Ollama model name |
| `WRAITH_OLLAMA_URL` | `http://127.0.0.1:11434` | Local Ollama endpoint |
| `WRAITH_GHOST` | `geocities` | Default personality |
| `WRAITH_DB` | `~/.wraith/wraith.db` | Local SQLite database |
| `WRAITH_TIMEOUT` | `8` | Maximum seconds to wait for Ollama |

## Design & privacy

Wraith stores timestamps, command text, exit codes, and short ghost responses in a local SQLite database. It does not upload telemetry. When Ollama is unavailable, Wraith falls back to deterministic local lines. Avoid running it where shell commands may contain credentials or private data. Wraith never reads deleted files and does not claim to recover their contents.

## Development

```bash
pip install -e ".[dev]"
pytest
```

## Roadmap

- [ ] Optional project-aware context
- [ ] Secret redaction before local inference
- [ ] Configurable quiet hours and response frequency
- [ ] More shells and custom ghost packs
- [ ] Model latency / offline benchmarks

## Why open innovation?

The ghost runs on an open-weight model through a local inference server. Once the model is downloaded, Wraith can respond without internet access, keep command history on the developer's machine, and remain useful without a paid hosted AI API. The shell integration and core event engine are open source and inspectable.
