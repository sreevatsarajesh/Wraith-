import os
import random
import sqlite3
from datetime import datetime, timezone
from pathlib import Path

import requests

GHOSTS = {
    "geocities": (
        "GeoCities, a nostalgic web spirit from 1999. Speak with retro internet nostalgia, "
        "guestbook and blinking-GIF references. Keep it to 1-2 short sentences."
    ),
    "fortran": (
        "The ghost of Fortran, a stern old scientific computing spirit who misses punch cards. "
        "Be dry, precise, and mildly judgmental. Keep it to 1-2 short sentences."
    ),
    "deleted-file": (
        "A deleted file that mourns lost data, but never claims to know file contents unless "
        "they are explicitly provided. Be eerie, poetic, and concise. Keep it to 1-2 sentences."
    ),
}

FALLBACKS = {
    "geocities": [
        "👻 Another command sent into the web. I miss when every page had a visitor counter.",
        "👻 The guestbook has been updated. Probably by a bot. It is 1999, after all.",
        "👻 I saw that from my little corner of the GeoNet. *blinking GIF intensifies*",
    ],
    "fortran": [
        "👻 In my day, this would have required a stack of punch cards.",
        "👻 The machine has spoken. I would have preferred a properly numbered deck.",
        "👻 Efficient enough. Now explain it to the compiler, mortal.",
    ],
    "deleted-file": [
        "👻 Something vanished. I shall not ask what; the silence is answer enough.",
        "👻 Every deletion leaves an echo. This one sounds suspiciously like regret.",
        "👻 I remember the shape of absence. The contents? You never told me.",
    ],
}

def db_path() -> Path:
    return Path(os.environ.get("WRAITH_DB", "~/.wraith/wraith.db")).expanduser()

def connect():
    path = db_path()
    path.parent.mkdir(parents=True, exist_ok=True)
    conn = sqlite3.connect(path, timeout=2)
    conn.execute("""CREATE TABLE IF NOT EXISTS events (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        created_at TEXT NOT NULL,
        command TEXT NOT NULL,
        exit_code INTEGER NOT NULL,
        ghost TEXT NOT NULL,
        response TEXT NOT NULL
    )""")
    conn.commit()
    return conn

def fallback(ghost: str, command: str, exit_code: int) -> str:
    if exit_code != 0:
        return {
            "geocities": "👻 A 404 in the command line. The page you seek is not responding.",
            "fortran": "👻 A non-zero exit code. The compiler of reality has rejected your offering.",
            "deleted-file": "👻 An error. Even the dead cannot make every operation succeed.",
        }.get(ghost, "👻 Something went wrong. Even spirits have limits.")
    if command.strip().startswith(("rm ", "rm\t")):
        return "👻 A disappearance. I hope you checked the path before opening that void."
    return random.choice(FALLBACKS.get(ghost, FALLBACKS["geocities"]))

def generate_response(command: str, exit_code: int, ghost: str = "geocities") -> str:
    ghost = ghost if ghost in GHOSTS else "geocities"
    prompt = (
        f"You are Wraith, a terminal ghost. Persona: {GHOSTS[ghost]}\n"
        f"Command observed: {command[:500]}\nExit status: {exit_code}\n"
        "React to the command in character. Do not give instructions, do not suggest executing "
        "commands, do not claim access to files or secrets. Maximum 35 words. Return only the line."
    )
    try:
        response = requests.post(
            os.environ.get("WRAITH_OLLAMA_URL", "http://127.0.0.1:11434").rstrip("/") + "/api/generate",
            json={
                "model": os.environ.get("WRAITH_MODEL", "qwen2.5:3b"),
                "prompt": prompt,
                "stream": False,
                "options": {"temperature": 0.85, "num_predict": 70},
            },
            timeout=float(os.environ.get("WRAITH_TIMEOUT", "8")),
        )
        response.raise_for_status()
        text = response.json().get("response", "").strip().strip('"')
        if not text:
            return fallback(ghost, command, exit_code)
        return "👻 " + text[:500]
    except (requests.RequestException, ValueError, KeyError):
        return fallback(ghost, command, exit_code)

def record_event(command: str, exit_code: int, ghost: str = "geocities") -> str:
    response = generate_response(command, exit_code, ghost)
    with connect() as conn:
        conn.execute(
            "INSERT INTO events(created_at, command, exit_code, ghost, response) VALUES (?, ?, ?, ?, ?)",
            (datetime.now(timezone.utc).isoformat(), command[:1000], int(exit_code), ghost, response),
        )
    return response

def recent_events(limit: int = 10):
    with connect() as conn:
        return conn.execute(
            "SELECT created_at, command, exit_code, ghost, response FROM events ORDER BY id DESC LIMIT ?",
            (max(1, min(int(limit), 100)),),
        ).fetchall()

def clear_memory():
    with connect() as conn:
        conn.execute("DELETE FROM events")
