"""
Compatibility shim for ADK loader: expose `root_agent` so `adk` can discover
the runtime entrypoint in the `hos01` folder.

The real executor logic lives in `agent_executor.MovieAgentExecutor`. ADK's
CLI looks for `root_agent` in `agent.py` (or a `root_agent.yaml`). To avoid
import-time failures when the full ADK runtime isn't installed, this module
provides a lightweight wrapper that delegates to `MovieAgentExecutor`.
"""
from typing import Any, Dict
import asyncio
import importlib.util
import os
import sys


def _load_local_module(module_name: str):
    """Attempt to import `module_name` normally; if that fails, load the
    module from a local .py file in the same directory as this file.

    This makes the agent folder robust to the ADK CLI running from a
    different working directory (the loader often imports by package name
    and the local module may not be on sys.path).
    """
    try:
        return __import__(module_name, fromlist=["*"])
    except ModuleNotFoundError:
        base = os.path.dirname(__file__)
        path = os.path.join(base, f"{module_name}.py")
        if not os.path.exists(path):
            raise
        spec = importlib.util.spec_from_file_location(f"{os.path.basename(base)}_{module_name}", path)
        mod = importlib.util.module_from_spec(spec)
        # Insert the module under a deterministic name so imports inside the
        # loaded module behave normally.
        module_key = spec.name
        sys.modules[module_key] = mod
        spec.loader.exec_module(mod)
        return mod


_agent_exec_mod = _load_local_module("agent_executor")
MovieAgentExecutor = getattr(_agent_exec_mod, "MovieAgentExecutor")


class _LocalRootAgent:
    """A minimal compatibility wrapper exposing a `handle` coroutine.

    The ADK CLI's loader only requires a `root_agent` symbol to exist. This
    wrapper implements a small `handle` method that accepts a plain input
    dict and optional `skill_id`, delegates to our executor, and returns the
    structured result. It is intentionally small and useful for local dev.
    """

    def __init__(self) -> None:
        self._executor = MovieAgentExecutor()

    async def handle(self, input: Dict[str, Any] | None = None, *, skill_id: str | None = None) -> Dict[str, Any]:
        # Build the minimal RequestContext/EventQueue expected by the executor.
        # Import here to avoid top-level dependency issues in environments
        # where the full ADK SDK isn't available.
        from agent_executor import RequestContext, EventQueue

        rc = RequestContext(input or {}, skill_id=skill_id)
        q = EventQueue()
        result = await self._executor.execute(rc, q)
        # Attempt to drain events if supported
        events = []
        if hasattr(q, "drain"):
            events = await q.drain()
        return {"result": result, "events": events}


# Expose the symbol the ADK CLI searches for
root_agent = _LocalRootAgent()
