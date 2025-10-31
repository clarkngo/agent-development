"""Small helper showing ADK imports and a safe wrapper to call an agent.

This module intentionally imports the ADK objects used in the repo examples.
Wraps imports in a try/except so the server can fail gracefully if ADK isn't
installed in the environment.
"""
from typing import Any
import os

try:
    # Real ADK imports used in reference examples
    from google.adk.cli.fast_api import get_fast_api_app
    from google.adk.runners import InMemoryRunner
    from google.adk.agents.run_config import RunConfig
    from google.genai import types

    HAS_ADK = True
except Exception:  # pragma: no cover - ADK optional at import time
    get_fast_api_app = None  # type: ignore
    InMemoryRunner = None  # type: ignore
    RunConfig = None  # type: ignore
    types = None  # type: ignore
    HAS_ADK = False


def adk_available() -> bool:
    return HAS_ADK


async def run_example_inmemory(prompt: str) -> dict[str, Any]:
    """Example wrapper that would create an InMemoryRunner and start a run.

    This function shows how to reference the ADK classes. It is left intentionally
    minimal: real agent wiring requires an `agent` object or agents_dir which is
    project-specific.
    """
    if not HAS_ADK:
        raise RuntimeError("ADK package not installed in this environment")

    # Example: create runner (note: this requires a real `agent` or agents_dir)
    app_name = os.getenv("APP_NAME", "vite-adk-a2a")

    # The caller should provide a real agent instance or import one here.
    # This example shows the intended pattern from repo references.
    runner = InMemoryRunner(app_name=app_name, agent=None)  # type: ignore[arg-type]

    # In real use you'd create a session and call runner.run or runner.run_live
    # See reference/short-movie-agents and realtime-conversational-agent for examples.
    return {"status": "ok", "note": "runner created (example)"}
