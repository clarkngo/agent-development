"""ADK helper for the MCP (server-backed) example.

Shows the preferred server-side pattern: prefer `get_fast_api_app` from ADK
when available, otherwise expose minimal helpers.
"""
from typing import Any
import os

try:
    from google.adk.cli.fast_api import get_fast_api_app
    from google.adk.runners import InMemoryRunner
    from google.adk.agents.run_config import RunConfig
    HAS_ADK = True
except Exception:  # pragma: no cover
    get_fast_api_app = None  # type: ignore
    InMemoryRunner = None  # type: ignore
    RunConfig = None  # type: ignore
    HAS_ADK = False


def adk_available() -> bool:
    return HAS_ADK


def build_adk_app(agents_dir: str | None = None, allow_origins: str | None = None) -> Any:
    """Return an ADK-provided FastAPI app if possible, otherwise None."""
    if not HAS_ADK or not get_fast_api_app:
        return None
    return get_fast_api_app(agents_dir=agents_dir or "./agents", web=True, allow_origins=allow_origins)
