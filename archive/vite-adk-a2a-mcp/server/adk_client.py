"""ADK helpers demonstrating both A2A and MCP patterns.

This module is a small reference for wiring A2A (app-to-app) and MCP
server-backed flows using the `google.adk` package.
"""
from typing import Any
import os

try:
    # Imports used in several reference projects in this repo
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


def example_note() -> dict[str, Any]:
    return {"adk": HAS_ADK, "info": "See README for wiring details."}
