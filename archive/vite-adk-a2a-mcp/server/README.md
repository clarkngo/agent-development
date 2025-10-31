# vite-adk-a2a-mcp server

This scaffold demonstrates both A2A and MCP server-side patterns using `google.adk`.

Quickstart

1. Copy `.env.example` to `.env` and provide credentials.
2. Create virtualenv and install dependencies:

```bash
python -m venv .venv
source .venv/bin/activate
pip install -r server/requirements.txt
```

3. Run server locally:

```bash
uvicorn server.main:app --reload --port 8002
```

Notes
- `main.py` will use the ADK `get_fast_api_app` if present, otherwise a helpful fallback is provided.
