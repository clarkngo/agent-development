"""
Simple A2A client example using `httpx` to discover the AgentCard and call the
fallback `POST /a2a/execute` endpoint. If the `a2a` SDK is available, prefer
using `A2AClient` from the SDK in production.
"""
import httpx
import asyncio
import json
from typing import Any, Dict

AGENT_BASE = "http://localhost:8080"


async def discover_agent(base_url: str = AGENT_BASE) -> Dict[str, Any]:
    async with httpx.AsyncClient() as client:
        r = await client.get(f"{base_url}/.well-known/agent.json")
        r.raise_for_status()
        return r.json()


async def call_skill(skill_id: str, payload: Dict[str, Any], base_url: str = AGENT_BASE) -> Any:
    async with httpx.AsyncClient() as client:
        r = await client.post(f"{base_url}/a2a/execute", json={"skill_id": skill_id, "input": payload})
        r.raise_for_status()
        return r.json()


def pretty(obj: Any) -> str:
    try:
        return json.dumps(obj, indent=2, ensure_ascii=False)
    except Exception:
        return str(obj)


async def main():
    card = await discover_agent()

    # Nicely print card header
    header = f"Discovered agent: {card.get('display_name', '<unknown>')} (id={card.get('id', '<no-id>')})"
    print("=" * len(header))
    print(header)
    print("=" * len(header))

    # Print skills with short summary
    skills = card.get("skills", [])
    if skills:
        print("Skills:")
        for s in skills:
            sid = s.get("id")
            name = s.get("name")
            desc = s.get("description", "")
            print(f" - {sid}: {name} — {desc}")
    else:
        print("(no skills listed on agent card)")

    print()

    # call the movie_lookup skill
    res = await call_skill("movie_lookup", {"title": "Inception"})
    print("Movie lookup result:")
    print(pretty(res))

    print()
    # call the summarizer
    res2 = await call_skill("summarize_description", {"text": "This is a long description that should be summarized by the agent."})
    print("Summarize result:")
    print(pretty(res2))


if __name__ == "__main__":
    asyncio.run(main())
