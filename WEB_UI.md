# Wraith Terminal Web UI

The terminal-themed React UI is optional. Wraith's CLI and shell hooks work independently.

## Run the API

From the repository root, activate your Python environment and install the API dependencies:

```bash
python -m pip install -r web_ui/backend/requirements.txt
uvicorn web_ui.backend.main:app --reload --host 127.0.0.1 --port 8765
```

## Run the frontend

In another terminal:

```bash
cd web_ui/frontend
npm install
npm run dev
```

Open the local URL Vite prints. Keep the API running in the first terminal. The UI communicates with the local API; it does not execute arbitrary shell commands.
