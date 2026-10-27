import os
import shlex
import subprocess
import sys
from pathlib import Path

import typer
from rich.console import Console
from rich.table import Table

from .core import GHOSTS, clear_memory, db_path, recent_events, record_event

app = typer.Typer(no_args_is_help=True, help="A haunted terminal companion powered by local AI.")
console = Console()
PACKAGE_DIR = Path(__file__).resolve().parent

@app.command()
def init(
    shell: str = typer.Option("zsh", help="Shell to configure: zsh or bash."),
    ghost: str = typer.Option("geocities", help="Default ghost personality."),
):
    """Show setup instructions for your shell."""
    if shell not in ("zsh", "bash"):
        raise typer.BadParameter("Choose zsh or bash")
    if ghost not in GHOSTS:
        raise typer.BadParameter("Unknown ghost personality")
    rc = "~/.zshrc" if shell == "zsh" else "~/.bashrc"
    hook = f'source "$(wraith hook-path {shell})"'
    console.print(f"[bold purple]👻 Wraith awakens as {ghost}.[/bold purple]")
    console.print(f"Add this line to {rc}:")
    console.print(f"[green]{hook}[/green]")
    console.print("Restart your shell, or source your rc file. Disable with WRAITH_ENABLED=0.")

@app.command("hook-path")
def hook_path(shell: str):
    """Print the path to a supported shell hook."""
    if shell not in ("zsh", "bash"):
        raise typer.BadParameter("Choose zsh or bash")
    print(PACKAGE_DIR / "hooks" / f"{shell}.sh")

@app.command()
def haunt(
    command: str = typer.Argument(..., help="Command text to haunt (does not execute it)."),
    status: int = typer.Option(0, "--status", help="Exit status to describe."),
    ghost: str = typer.Option(None, "--ghost", help="Ghost personality."),
):
    """Generate a reaction to command text without executing the command."""
    chosen = ghost or os.environ.get("WRAITH_GHOST", "geocities")
    if chosen not in GHOSTS:
        raise typer.BadParameter(f"Choose one of: {', '.join(GHOSTS)}")
    console.print(record_event(command, status, chosen))

@app.command()
def status():
    """Show local model and memory status."""
    model = os.environ.get("WRAITH_MODEL", "qwen2.5:3b")
    enabled = os.environ.get("WRAITH_ENABLED", "1") != "0"
    console.print(f"[bold purple]👻 Wraith[/bold purple] {'enabled' if enabled else 'disabled'}")
    console.print(f"Ghost: {os.environ.get('WRAITH_GHOST', 'geocities')}")
    console.print(f"Model: {model}")
    console.print(f"Memory: {db_path()}")
    try:
        import requests
        r = requests.get(os.environ.get("WRAITH_OLLAMA_URL", "http://127.0.0.1:11434").rstrip("/") + "/api/tags", timeout=1.5)
        r.raise_for_status()
        models = [m.get("name", "") for m in r.json().get("models", [])]
        console.print(f"Ollama: online ({'model available' if any(m == model or m.startswith(model + ':') for m in models) else 'configured model not found'})")
    except Exception:
        console.print("Ollama: offline (fallback responses will be used)")

@app.command()
def memory(limit: int = typer.Option(10, min=1, max=100, help="Number of recent events.")):
    """Inspect recent local events."""
    rows = recent_events(limit)
    table = Table(title="Wraith's local memory")
    table.add_column("Time", style="dim", max_width=25)
    table.add_column("Command", max_width=35)
    table.add_column("Exit")
    table.add_column("Ghost")
    table.add_column("Whisper", max_width=55)
    for created, command, code, ghost, response in rows:
        table.add_row(created[:19], command, str(code), ghost, response)
    console.print(table)

@app.command()
def forget():
    """Delete all locally stored Wraith events."""
    if typer.confirm("Erase Wraith's local event memory?"):
        clear_memory()
        console.print("[green]The echoes have faded.[/green]")
    else:
        console.print("The memories remain.")

if __name__ == "__main__":
    app()
