"""
A minimal AgentExecutor implementation for the HOS01 Movie Tool Agent.

This module attempts to import the real `a2a` SDK classes. If the SDK is not
installed, lightweight shims are provided so the module can run for local
development and testing. The shim behavior is intentionally simple — it lets
you run the server and exercise the executor logic locally.

Separation of concerns: agent metadata lives in `.well-known/agent.json` and
the runtime behavior lives here in `MovieAgentExecutor`.
"""
from typing import Any, Dict
import asyncio
import json
import os

try:
    # Preferred real imports from the a2a SDK
    from a2a.server import AgentExecutor, RequestContext, EventQueue
except Exception:
    # Lightweight runtime shims to allow local testing without the SDK.
    class RequestContext:
        def __init__(self, input: Dict[str, Any], skill_id: str | None = None, metadata: Dict[str, Any] | None = None):
            self.input = input
            self.skill_id = skill_id
            self.metadata = metadata or {}

    class EventQueue:
        def __init__(self):
            self._events = []

        async def publish(self, event: Dict[str, Any]):
            # simple append — in a real runtime this would stream to listeners
            self._events.append(event)

        async def drain(self):
            # return events and clear
            events = list(self._events)
            self._events.clear()
            return events

    class AgentExecutor:
        async def execute(self, request_context: RequestContext, event_queue: EventQueue) -> Any:  # pragma: no cover - shim
            raise NotImplementedError()


class MovieAgentExecutor(AgentExecutor):
    """Executor implementing two simple skills:
    - `movie_lookup`: returns a minimal metadata object for a given title
    - `summarize_description`: returns a short textual summary for input text

    The executor validates inputs and emits simple events to the provided
    `EventQueue`. In a production A2A runtime the event_queue will stream
    events to connected clients; here we append them and return the final
    result.
    """

    async def execute(self, request_context: RequestContext, event_queue: EventQueue) -> Dict[str, Any]:
        payload = request_context.input or {}
        skill_id = request_context.skill_id or payload.get("skill")

        if not skill_id:
            raise ValueError("skill id is required in RequestContext.skill_id or payload['skill']")

        # Basic input validation
        if skill_id == "movie_lookup":
            title = payload.get("title")
            if not isinstance(title, str) or not title.strip():
                raise ValueError("'title' must be a non-empty string for movie_lookup")

            # In a real agent this would call a DB or external API. Keep minimal here.
            result = {
                "title": title.strip(),
                "year": "1999",
                "summary": f"A concise, programmatic lookup for '{title.strip()}'."
            }

            # Emit a friendly text event
            try:
                await event_queue.publish({"type": "new_agent_text_message", "text": f"Found: {result['title']} ({result['year']})"})
            except Exception:
                # Some EventQueue shims use different method names — ignore failures of optional streaming
                pass

            # Return structured response
            return {"status": "ok", "skill": skill_id, "result": result}

        if skill_id == "summarize_description":
            text = payload.get("text")
            if not isinstance(text, str) or not text.strip():
                raise ValueError("'text' must be a non-empty string for summarize_description")

            # Very small summarizer: return first 120 chars followed by ellipsis if long.
            summary = (text.strip()[:120] + ("..." if len(text.strip()) > 120 else ""))

            await event_queue.publish({"type": "new_agent_text_message", "text": f"Summary produced ({len(summary)} chars)"})

            return {"status": "ok", "skill": skill_id, "result": {"summary": summary}}

        raise ValueError(f"Unsupported skill_id: {skill_id}")


def load_card(path: str) -> Dict[str, Any]:
    p = os.path.abspath(path)
    with open(p, "r", encoding="utf-8") as fh:
        return json.load(fh)


if __name__ == "__main__":
    # quick local smoke test for the executor
    import asyncio

    async def _test():
        ex = MovieAgentExecutor()
        rc = RequestContext({"title": "The Matrix"}, skill_id="movie_lookup")
        q = EventQueue()
        res = await ex.execute(rc, q)
        events = await q.drain() if hasattr(q, "drain") else []
        print("RESULT:", res)
        print("EVENTS:", events)

    asyncio.run(_test())
