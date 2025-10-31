"""FastAPI server scaffold for the MCP-backed starter.

This file prefers the ADK-provided `get_fast_api_app` when available. If not,
it falls back to a minimal set of endpoints and returns clear guidance.
"""
import os
from dotenv import load_dotenv
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel

load_dotenv()

try:
    from google.adk.cli.fast_api import get_fast_api_app
    HAS_ADK = True
except Exception:
    get_fast_api_app = None  # type: ignore
    HAS_ADK = False


class RunRequest(BaseModel):
    input: str


def build_app() -> FastAPI:
    allow_origins = os.getenv("ALLOW_ORIGINS")
    agents_dir = os.getenv("AGENTS_DIR") or "./agents"
    if HAS_ADK and get_fast_api_app:
        app = get_fast_api_app(agents_dir=agents_dir, web=True, allow_origins=allow_origins)
        app.title = os.getenv("APP_NAME", "vite-adk-mcp-server")
        return app

    app = FastAPI(title=os.getenv("APP_NAME", "vite-adk-mcp-server"))

    @app.get("/health")
    def _health():
        return {"status": "ok", "adk": HAS_ADK}

    @app.post("/run")
    def _run(req: RunRequest):
        if not HAS_ADK:
            raise HTTPException(status_code=501, detail="ADK not installed on server. Install google-adk to enable agent endpoints.")
        # In real use the ADK get_fast_api_app will provide routes like /run, /run_sse, /list-apps.
        return {"status": "ok", "note": "ADK is present; prefer get_fast_api_app routes"}

    return app


app = build_app()


if __name__ == "__main__":
    import uvicorn

    uvicorn.run(app, host="0.0.0.0", port=int(os.getenv("PORT", 8001)))
