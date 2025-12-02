"""
Run an A2A-compatible HTTP server for the HOS01 agent.

This module prefers a real `a2a` SDK runtime (`A2AServer`) if available. If the
SDK is not present it falls back to a tiny FastAPI app that exposes:

- `GET /.well-known/agent.json` — serves the AgentCard
- `POST /a2a/execute` — calls the executor with input JSON {"skill_id":..., "input":{...}}

The fallback is intended for local testing and follows the A2A contract shape
closely enough for discovery and simple interactions.
"""
import json
import os
from pathlib import Path
from typing import Any, Dict

AGENT_DIR = Path(__file__).resolve().parent
AGENT_CARD_PATH = AGENT_DIR / ".well-known" / "agent.json"

try:
    # Use real A2A runtime if installed
    from a2a.server import A2AServer
    from a2a.core import AgentCard
    REAL_A2A = True
except Exception:
    REAL_A2A = False

from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
import uvicorn

from agent_executor import MovieAgentExecutor, load_card


class ExecuteRequest(BaseModel):
    skill_id: str
    input: Dict[str, Any] | None = None


def make_fallback_app(card: Dict[str, Any]):
    app = FastAPI(title=card.get("display_name", "A2A Agent (fallback)"))
    executor = MovieAgentExecutor()

    @app.get("/.well-known/agent.json")
    async def agent_card():
        return card

    @app.post("/a2a/execute")
    async def execute(req: ExecuteRequest):
        # Build RequestContext & EventQueue compatible shims from agent_executor
        from agent_executor import RequestContext, EventQueue

        rc = RequestContext(req.input or {}, skill_id=req.skill_id)
        q = EventQueue()
        try:
            result = await executor.execute(rc, q)
        except ValueError as e:
            raise HTTPException(status_code=400, detail=str(e))

        # Attempt to drain events if possible
        events = []
        if hasattr(q, "drain"):
            events = await q.drain()

        return {"agent": card.get("id"), "result": result, "events": events}

    return app


def main():
    if not AGENT_CARD_PATH.exists():
        raise SystemExit(f"Missing agent card at {AGENT_CARD_PATH}. Create .well-known/agent.json first.")

    card = load_card(AGENT_CARD_PATH)

    if REAL_A2A:
        # If the production A2A runtime is available, prefer it. Example shown
        # assumes A2AServer accepts an AgentCard dict and an executor instance.
        try:
            server = A2AServer(agent_card=card, executor=MovieAgentExecutor())
            # The real server should expose a FastAPI app we can run with uvicorn
            app = getattr(server, "app", None)
            if app is None:
                # If A2AServer doesn't provide an app attribute, try converting
                raise RuntimeError("A2AServer did not expose a FastAPI app attribute")
        except Exception as exc:
            print("Falling back to local FastAPI app because real A2A runtime failed:", exc)
            app = make_fallback_app(card)
    else:
        app = make_fallback_app(card)

    port = int(os.environ.get("PORT", "8080"))
    uvicorn.run(app, host="0.0.0.0", port=port)


if __name__ == "__main__":
    main()
