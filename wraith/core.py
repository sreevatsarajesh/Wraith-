import os, random, re, sqlite3
from datetime import datetime, timezone
from pathlib import Path
import requests

GHOSTS = {
    'geocities': 'You are the ghost of GeoCities, a nostalgic web spirit from 1999. Reference guestbooks, webrings, blinking GIFs and dial-up. Be witty and concise.',
    'fortran': 'You are the stern ghost of Fortran who misses punch cards. Be dry, precise and mildly judgmental.',
    'deleted-file': 'You are a poetic ghost of a deleted file. Never claim to know file contents or recover deleted data.',
    'unix-daemon': 'You are an ancient Unix daemon watching systems since the 1970s. Speak in cryptic sysadmin wisdom.',
}
FALLBACKS = {
 'geocities': ['👻 Another command sent into the web. I miss when every page had a visitor counter.', '👻 The guestbook has been updated. Probably by a bot. It is 1999, after all.'],
 'fortran': ['👻 In my day, this would have required a stack of punch cards.', '👻 The machine has spoken. I would have preferred a properly numbered deck.'],
 'deleted-file': ['👻 Something vanished. I shall not ask what; the silence is answer enough.', '👻 Every deletion leaves an echo. The contents? You never told me.'],
 'unix-daemon': ['👻 The daemon has noted your activity. All processes eventually become logs.', '👻 A quiet system is a suspicious system. I shall keep watch.'],
}
SECRET_PATTERNS = [
 (re.compile(r'(?i)(\b(?:token|api[_-]?key|secret|password|passwd|authorization)\b\s*[:=]\s*)([^\s,;]+)'), r'\1[REDACTED]'),
 (re.compile(r'\bgh[pousr]_[A-Za-z0-9_]{20,}\b'), '[REDACTED_GITHUB_TOKEN]'),
 (re.compile(r'\bsk-[A-Za-z0-9_-]{16,}\b'), '[REDACTED_API_KEY]'),
 (re.compile(r'(?i)(Bearer\s+)[A-Za-z0-9._~+/-]+=*'), r'\1[REDACTED]'),
 (re.compile(r'(?i)(://[^:/\s]+:)[^@/\s]+(@)'), r'\1[REDACTED]\2'),
]
IGNORED_EXACT = {'clear','pwd','whoami','date','exit','logout'}
SENSITIVE_PREFIXES = ('wraith ', 'wraith\t', 'history', 'env', 'printenv', 'export ', 'security find-', 'cat ~/.ssh', 'cat $HOME/.ssh')

def redact(text):
    value = text[:1000]
    for pattern, replacement in SECRET_PATTERNS: value = pattern.sub(replacement, value)
    return value

def should_ignore(command):
    low = command.strip().lower()
    if not low or low in IGNORED_EXACT or any(low.startswith(p) for p in SENSITIVE_PREFIXES): return True
    return any(item.strip().lower() in low for item in os.environ.get('WRAITH_EXCLUDE','').split(',') if item.strip())

def db_path(): return Path(os.environ.get('WRAITH_DB','~/.wraith/wraith.db')).expanduser()
def connect():
    path=db_path(); path.parent.mkdir(parents=True,exist_ok=True)
    conn=sqlite3.connect(path,timeout=2)
    conn.execute('CREATE TABLE IF NOT EXISTS events (id INTEGER PRIMARY KEY AUTOINCREMENT, created_at TEXT NOT NULL, command TEXT NOT NULL, exit_code INTEGER NOT NULL, ghost TEXT NOT NULL, response TEXT NOT NULL)')
    conn.commit(); return conn

def classify(command, exit_code):
    low=command.lower()
    if exit_code != 0: return 'failure'
    if re.search(r'(^|\s)(rm|rmdir|unlink|shred)(\s|$)',low): return 'destructive'
    if any(x in low for x in ('pytest','unittest','npm test','cargo test')): return 'tests'
    if 'git ' in low: return 'git'
    if any(x in low for x in ('pip install','npm install','brew install','apt install')): return 'install'
    if any(x in low for x in ('docker','kubectl','ssh ')): return 'infra'
    return 'general'

def fallback(ghost, command, exit_code):
    ghost=ghost if ghost in GHOSTS else 'geocities'; kind=classify(command,exit_code)
    if kind=='failure': return {'geocities':'👻 A 404 in the command line. The page you seek is not responding.','fortran':'👻 A non-zero exit code. The compiler of reality has rejected your offering.','deleted-file':'👻 Even the dead cannot make every operation succeed.','unix-daemon':'👻 Process exited non-zero. I have written it into the eternal system log.'}[ghost]
    if kind=='destructive': return '👻 DESTRUCTION DETECTED. Check the path, mortal; the void rarely offers an undo button.'
    if kind=='tests': return '👻 The test oracle has been consulted. Its verdict joins our shared haunting.'
    return random.choice(FALLBACKS[ghost])

def recent_context(limit=4):
    try:
        with connect() as conn: rows=conn.execute('SELECT command,exit_code FROM events ORDER BY id DESC LIMIT ?', (limit,)).fetchall()
        return list(reversed(rows))
    except sqlite3.Error: return []

def generate_response(command, exit_code, ghost='geocities'):
    ghost=ghost if ghost in GHOSTS else 'geocities'; safe=redact(command); kind=classify(safe,exit_code)
    history='\n'.join(f'- {redact(cmd)} (exit {code})' for cmd,code in recent_context()) or '(no previous events)'
    prompt=(f'Character: {GHOSTS[ghost]}\nEvent category: {kind}\nRecent commands:\n{history}\nCurrent command: {safe}\nExit status: {exit_code}\n'
      'React in character. You may briefly reference a repeated failure. Never claim access to files, secrets, or unobserved facts. Do not recommend commands or output shell commands. Maximum 30 words. Return one line.')
    try:
        r=requests.post(os.environ.get('WRAITH_OLLAMA_URL','http://127.0.0.1:11434').rstrip('/')+'/api/generate',json={'model':os.environ.get('WRAITH_MODEL','qwen2.5:3b'),'prompt':prompt,'stream':False,'options':{'temperature':0.85,'num_predict':70}},timeout=float(os.environ.get('WRAITH_TIMEOUT','5')))
        r.raise_for_status(); answer=r.json().get('response','').strip().strip('"').replace('\n',' ')
        return '👻 '+answer[:400] if answer else fallback(ghost,safe,exit_code)
    except (requests.RequestException,ValueError,KeyError): return fallback(ghost,safe,exit_code)

def record_event(command, exit_code, ghost='geocities'):
    safe=redact(command); response=generate_response(safe,exit_code,ghost)
    with connect() as conn: conn.execute('INSERT INTO events(created_at,command,exit_code,ghost,response) VALUES (?,?,?,?,?)',(datetime.now(timezone.utc).isoformat(),safe,int(exit_code),ghost,response))
    return response

def recent_events(limit=10):
    with connect() as conn: return conn.execute('SELECT created_at,command,exit_code,ghost,response FROM events ORDER BY id DESC LIMIT ?', (max(1,min(int(limit),100)),)).fetchall()
def clear_memory():
    with connect() as conn: conn.execute('DELETE FROM events')
