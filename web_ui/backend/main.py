from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field

try:
    from wraith.core import GHOSTS, db_path, recent_events, record_event
except ImportError as exc:
    raise RuntimeError(
        "Run this API from your Wraith project root so Python can import wraith.core."
    ) from exc

app = FastAPI(title="Wraith Local API", version="0.2.0")
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://127.0.0.1:5173", "http://localhost:5173"],
    allow_credentials=False,
    allow_methods=["GET", "POST"],
    allow_headers=["Content-Type"],
)

class HauntRequest(BaseModel):
    command: str = Field(min_length=1, max_length=1000)
    ghost: str = "geocities"

@app.get("/api/status")
def status():
    import os
    return {
        "api": True,
        "model": os.environ.get("WRAITH_MODEL", "qwen2.5:3b"),
        "ghosts": list(GHOSTS.keys()),
        "memory_path": str(db_path()),
        "execution": False,
    }

@app.post("/api/haunt")
def haunt(payload: HauntRequest):
    command = payload.command.strip()
    if not command:
        raise HTTPException(status_code=400, detail="Command text is required.")
    if payload.ghost not in GHOSTS:
        raise HTTPException(status_code=400, detail="Unknown ghost personality.")
    try:
        response = record_event(command, 0, payload.ghost)
        return {"response": response, "ghost": payload.ghost, "executed": False}
    except Exception as exc:
        raise HTTPException(status_code=503, detail=f"Wraith reaction failed: {type(exc).__name__}") from exc

@app.get("/api/memory")
def memory(limit: int = 8):
    try:
        rows = recent_events(max(1, min(limit, 30)))
        return {"events": [
            {"created_at": row[0], "command": row[1], "exit_code": row[2], "ghost": row[3], "response": row[4]}
            for row in rows
        ]}
    except Exception as exc:
        raise HTTPException(status_code=503, detail="Local memory is unavailable.") from exc
