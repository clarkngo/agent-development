"""Minimal FastAPI server scaffold that demonstrates ADK imports and endpoints.

This template follows patterns from the repo's reference examples (get_fast_api_app
when available) and exposes /health and /run endpoints. If ADK isn't installed the
endpoints will return a helpful message.
"""
import os
from dotenv import load_dotenv
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from typing import Any

load_dotenv()

try:
    # Import ADK utilities used throughout the reference projects
    from google.adk.cli.fast_api import get_fast_api_app
    from google.adk.runners import InMemoryRunner
    from google.adk.agents.run_config import RunConfig
    HAS_ADK = True
except Exception:
    get_fast_api_app = None  # type: ignore
    InMemoryRunner = None  # type: ignore
    RunConfig = None  # type: ignore
    HAS_ADK = False


class RunRequest(BaseModel):
    prompt: str
    metadata: dict[str, Any] | None = None


def build_app() -> FastAPI:
    allow_origins = os.getenv("ALLOW_ORIGINS")
    if HAS_ADK and get_fast_api_app:
        # If the ADK-provided helper exists, prefer it — matches repo examples
        agents_dir = os.getenv("AGENTS_DIR") or "./agents"
        app = get_fast_api_app(agents_dir=agents_dir, web=True, allow_origins=allow_origins)
        app.title = os.getenv("APP_NAME", "vite-adk-a2a-server")
        return app

    # Fallback simple FastAPI app for environments without the ADK package.
    app = FastAPI(title=os.getenv("APP_NAME", "vite-adk-a2a-server"))

    @app.get("/health")
    def _health():
        return {"status": "ok", "adk": HAS_ADK}

    @app.post("/run")
    async def _run(req: RunRequest):
        if not HAS_ADK:
            raise HTTPException(status_code=501, detail="ADK not installed in server environment")
        # In real usage: create a Runner, start a session, and invoke the agent.
        try:
            # Example placeholder — adapt to your agent wiring
            runner = InMemoryRunner(app_name=os.getenv("APP_NAME", "vite-adk-a2a"), agent=None)  # type: ignore[arg-type]
            return {"status": "ok", "note": "ADK runner created (example)"}
        except Exception as e:
            raise HTTPException(status_code=500, detail=str(e))

    return app


app = build_app()


if __name__ == "__main__":
    import uvicorn

    uvicorn.run(app, host="0.0.0.0", port=int(os.getenv("PORT", "8000")))
