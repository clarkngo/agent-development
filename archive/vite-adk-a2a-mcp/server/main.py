"""Combined A2A + MCP FastAPI server scaffold.

This scaffold demonstrates how to prefer the ADK helper `get_fast_api_app` when
present, and also exposes simple endpoints for quick testing in development.
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
    prompt: str


def build_app() -> FastAPI:
    allow_origins = os.getenv("ALLOW_ORIGINS")
    agents_dir = os.getenv("AGENTS_DIR") or "./agents"
    if HAS_ADK and get_fast_api_app:
        app = get_fast_api_app(agents_dir=agents_dir, web=True, allow_origins=allow_origins)
        app.title = os.getenv("APP_NAME", "vite-adk-a2a-mcp-server")
        return app

    app = FastAPI(title=os.getenv("APP_NAME", "vite-adk-a2a-mcp-server"))

    @app.get("/health")
    def _health():
        return {"status": "ok", "adk": HAS_ADK}

    @app.post("/run")
    async def _run(req: RunRequest):
        if not HAS_ADK:
            raise HTTPException(status_code=501, detail="ADK not installed; install google-adk to enable agent routes")
        # Placeholder: in production wire a runner/agent here
        return {"status": "ok", "prompt": req.prompt[:200]}

    return app


app = build_app()


if __name__ == "__main__":
    import uvicorn

    uvicorn.run(app, host="0.0.0.0", port=int(os.getenv("PORT", 8002)))
