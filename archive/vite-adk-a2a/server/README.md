# vite-adk-a2a server

This is a minimal FastAPI server scaffold for the `vite-adk-a2a` starter.

What is included
- `requirements.txt` — python deps (FastAPI, Uvicorn, python-dotenv, google-adk)
- `.env.example` — example environment variables
- `main.py` — FastAPI app demonstrating ADK imports and endpoints
- `adk_client.py` — small helper showing ADK import patterns

Quickstart (macOS / zsh)

1. Copy `.env.example` to `.env` and fill real credentials (do NOT commit `.env`).

2. Create a virtualenv and install dependencies:

```bash
python -m venv .venv
source .venv/bin/activate
pip install -r server/requirements.txt
```

3. Run the server:

```bash
uvicorn server.main:app --reload --port 8000
```

Notes
- `main.py` will attempt to use `get_fast_api_app` from `google.adk.cli.fast_api` if available.
- Endpoints return a clear message if the ADK package is not installed.
