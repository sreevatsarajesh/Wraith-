import os
from pathlib import Path
import typer
from rich.console import Console
from rich.table import Table
from .core import GHOSTS, clear_memory, db_path, recent_events, record_event, should_ignore
app=typer.Typer(no_args_is_help=True,help='A haunted terminal companion powered by local AI.')
console=Console(); PACKAGE_DIR=Path(__file__).resolve().parent
@app.command()
def init(shell:str=typer.Option('zsh'),ghost:str=typer.Option('geocities')):
    if shell not in ('zsh','bash'): raise typer.BadParameter('Choose zsh or bash')
    if ghost not in GHOSTS: raise typer.BadParameter('Unknown ghost personality')
    rc='~/.zshrc' if shell=='zsh' else '~/.bashrc'
    console.print(f'[bold magenta]👻 Wraith awakens as {ghost}.[/bold magenta]')
    console.print(f'Add this line to {rc}:')
    console.print(f'[green]source "$(wraith hook-path {shell})"[/green]')
    console.print('Disable at any time with: export WRAITH_ENABLED=0')
@app.command('hook-path')
def hook_path(shell:str):
    if shell not in ('zsh','bash'): raise typer.BadParameter('Choose zsh or bash')
    print(PACKAGE_DIR/'hooks'/f'{shell}.sh')
@app.command()
def haunt(command:str=typer.Argument(...),status:int=typer.Option(0,'--status'),ghost:str=typer.Option(None,'--ghost')):
    if should_ignore(command): return
    chosen=ghost or os.environ.get('WRAITH_GHOST','geocities')
    if chosen not in GHOSTS: raise typer.BadParameter(f'Choose one of: {", ".join(GHOSTS)}')
    try: console.print(record_event(command,status,chosen))
    except Exception:
        if os.environ.get('WRAITH_DEBUG')=='1': raise
@app.command()
def status():
    model=os.environ.get('WRAITH_MODEL','qwen2.5:3b')
    console.print(f'[bold magenta]👻 Wraith[/bold magenta] {"enabled" if os.environ.get("WRAITH_ENABLED","1")!="0" else "disabled"}')
    console.print(f"Ghost: {os.environ.get('WRAITH_GHOST', 'geocities')}\nModel: {model}\nMemory: {db_path()}")
    try:
        import requests
        r=requests.get(os.environ.get('WRAITH_OLLAMA_URL','http://127.0.0.1:11434').rstrip('/')+'/api/tags',timeout=1.5); r.raise_for_status()
        names=[m.get('name','') for m in r.json().get('models',[])]
        console.print(f'Ollama: online ({"configured model available" if any(n==model or n.startswith(model+":") for n in names) else "configured model not found"})')
    except Exception: console.print('Ollama: offline (fallback responses will be used)')
    console.print('Privacy: common token patterns redacted; local SQLite only.')
@app.command()
def ghosts():
    table=Table(title='Available ghosts'); table.add_column('Name',style='cyan'); table.add_column('Lore')
    for name,lore in {'geocities':'Lost web spirit from 1999','fortran':'Stern ghost of scientific computing','deleted-file':'Poetic spirit of vanished files','unix-daemon':'Ancient watcher of system processes'}.items(): table.add_row(name,lore)
    console.print(table)
@app.command()
def memory(limit:int=typer.Option(10,min=1,max=100)):
    table=Table(title="Wraith's local memory")
    for col in ('Time','Command','Exit','Ghost','Whisper'): table.add_column(col,max_width=55 if col=='Whisper' else 35)
    for created,command,code,ghost,response in recent_events(limit): table.add_row(created[:19],command,str(code),ghost,response)
    console.print(table)
@app.command()
def forget():
    if typer.confirm("Erase Wraith's local event memory?"): clear_memory(); console.print('[green]The echoes have faded.[/green]')
    else: console.print('The memories remain.')
if __name__=='__main__': app()
