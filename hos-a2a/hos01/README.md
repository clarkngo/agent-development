# HOS01 — A2A Movie Tool Agent (minimal)

This folder contains a minimal A2A provider example suitable for local testing.

Files included:

- `.well-known/agent.json` — the AgentCard (discovery metadata).
- `agent_executor.py` — the runtime executor implementing the agent skills.
- `main.py` — server runner; prefers a real A2A runtime if installed, falls back to a FastAPI compatibility app.
- `client_example.py` — small `httpx` client that discovers the AgentCard and calls the agent.
- `requirements.txt` — minimal dependencies for the fallback server and client.
- `.env.example` and `.env` — environment variables for running the agent locally.


Quick start (start inside the `hos-a2a/hos01` folder)

These commands assume you begin with your shell's working directory set to `hos-a2a/hos01`.

1. Create a virtualenv and install requirements:

```bash
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```

2. Copy `.env.example` to `.env` and set your credentials (edit the file inline):

```bash
cp .env.example .env
# edit .env and set GOOGLE_API_KEY=... or GOOGLE_APPLICATION_CREDENTIALS=...
```

3a. Run the fallback FastAPI server (no ADK CLI required):

```bash
python main.py
```

3b. (Optional) Expose the agent using the ADK API server so it appears in `adk web`.
Run this from inside the agent folder so the ADK loader resolves the local `entrypoint` paths:

```bash
# load env (in the current shell)
set -a; source .env; set +a

# start the ADK API server in A2A mode and point it at the current directory
adk api_server --a2a .
```

4. In another terminal (or after starting `adk api_server`), open the ADK web UI:

```bash
adk web
```

5. Quick client test (from the same `hos-a2a/hos01` folder):

```bash
python client_example.py
```

Authentication and model access
--------------------------------

There are two common ways to authenticate and call Gemini model(s):

- Service account (recommended for server agents):
  - Set `GOOGLE_APPLICATION_CREDENTIALS` to the path of a Google service account JSON file.
  - Example (in `.env`):

```dotenv
GOOGLE_APPLICATION_CREDENTIALS=/path/to/service-account.json
ADK_AUTH_METHOD=service_account
```

  - This is the preferred production method: it provides strong identity and IAM controls and is suitable for exposing an agent to others.

- API key (simple, for quick local testing):
  - Set `GOOGLE_API_KEY` in your environment if you prefer to call model endpoints with a key.
  - Example (in `.env`):

```dotenv
GOOGLE_API_KEY=ya29.your_api_key_here
```

  - Note: `GOOGLE_API_KEY` is convenient but less secure than a service account. Avoid embedding keys in front-end/browser code.

Which should you use with ADK/web + `gemini-2.0-flash`?
- If you run `adk web` and the ADK runtime expects a service account, prefer `GOOGLE_APPLICATION_CREDENTIALS` for server-side credentials.
- If you want a minimal local test of model calls, `GOOGLE_API_KEY` is acceptable; set it in your `.env` or exported shell.

A2A (agent-to-agent) credentials
--------------------------------

- `A2A_CLIENT_ID` / `A2A_CLIENT_SECRET` are OAuth-style client credentials used only if you intend to expose the agent via A2A with an OAuth2 client-credentials flow.
- For most local development where the provider uses a service account, you can leave `A2A_CLIENT_ID`/`A2A_CLIENT_SECRET` empty and use `A2A_ENABLE=true` to let the ADK runtime configure exposure using service account tokens.

Security & git
--------------

- Keep `.env` local. `.env.example` is safe to commit. The repository contains a `.gitignore` entry for `hos-a2a/hos01/.env`.
- Never commit `GOOGLE_APPLICATION_CREDENTIALS` JSON files or `A2A_CLIENT_SECRET` values to source control.

Troubleshooting
---------------

- If client discovery fails (404 on `/.well-known/agent.json`): make sure the server is running on the port you expect (default `8080`) and that `main.py` started without errors.
- If model calls fail with `401`/`403`: verify your `GOOGLE_API_KEY` or `GOOGLE_APPLICATION_CREDENTIALS` and ensure the service account has appropriate permissions to call the requested model.

Common ADK loader error: "No root_agent found for '<agent>'"
----------------------------------------------------------

If you see an error like:

```
ValueError: No root_agent found for 'hos01'. Searched in 'hos01.agent.root_agent', 'hos01.root_agent' and 'hos01/root_agent.yaml'.
```

The ADK CLI expects each agent folder to expose a `root_agent` symbol (or a
`root_agent.yaml`) that the runtime can import. To fix this we provide a
lightweight `agent.py` in this folder that exposes a compatible `root_agent`.

What to check:

- Ensure `hos-a2a/hos01/agent.py` exists and defines `root_agent` (this repo
  includes a small wrapper that delegates to `agent_executor.MovieAgentExecutor`).
- Run `adk api_server` from the agent folder so entrypoints resolve relative to
  the folder (recommended):

```bash
cd hos-a2a/hos01
set -a; source .env; set +a
adk api_server --a2a .
```

- Alternatively, if you prefer to run `adk api_server` from the repository
  root, ensure the `entrypoint` paths in `.well-known/agent.json` are
  fully-qualified module paths that Python can import from the repo root.

If you'd like I can attempt to start `adk api_server --a2a .` (and report
any import/entrypoint errors). I cannot start it here unless the `adk` CLI is
installed in this environment, but I can show exact commands and help
interpret any stack traces you paste back.


Commands for loading env and running `adk web` (example):

```bash
# load env from the folder
set -a
source hos-a2a/hos01/.env
set +a

# run adk web (example command — adjust to your adk CLI)
adk web
```

If you'd like I can commit a focused change (commit only `hos-a2a/hos01/.well-known/agent.json`, `agent_executor.py`, `main.py`, `client_example.py`, `requirements.txt`, `README.md`, `.env.example`, `.gitignore`) and leave `.env` untracked. Say "commit & push" to proceed.
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
