# vite-adk-mcp server

Minimal FastAPI scaffold for the `vite-adk-mcp` starter (server-backed ADK).

Quickstart

1. Copy `.env.example` to `.env` and fill credentials.
2. Create virtualenv and install:

```bash
python -m venv .venv
source .venv/bin/activate
pip install -r server/requirements.txt
```

3. Run the server:

```bash
uvicorn server.main:app --reload --port 8001
```

Notes
- If `google-adk` is installed the server will use `get_fast_api_app` to expose the full agent API (see reference projects).
