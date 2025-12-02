# HOS01 — A2A Movie Tool Agent (minimal)

This folder contains a minimal A2A provider example suitable for local testing.

Files added:

- `.well-known/agent.json` — the AgentCard (discovery metadata).
- `agent_executor.py` — the runtime executor implementing the agent skills.
- `main.py` — server runner; prefers a real A2A runtime if installed, falls back to a FastAPI compatibility app.
- `client_example.py` — small `httpx` client that discovers the AgentCard and calls the agent.
- `requirements.txt` — minimal dependencies for the fallback server and client.

Quick start (local, no a2a SDK):

1. Create a virtualenv and install requirements:

```bash
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```

2. Run the server:

```bash
python main.py
```

3. In another terminal run the client example:

```bash
python client_example.py
```

If you have a real `a2a` SDK installed that supplies `A2AServer`, `AgentExecutor`,
and related runtime classes, `main.py` will prefer the real runtime. The
fallback exists to let you develop and debug the agent executor logic without
installing the full SDK.

Security note: this example is intentionally minimal. Always validate and
sanitize inputs in production and never accept untrusted binary payloads.
