A2A (application-to-application) exposure for the movie tool agent

This folder contains a minimal `agent.json` card to expose the `movie-tool-agent`
in A2A mode using the ADK CLI.

Quick steps (based on ADK docs):

1. Set your service account credentials (don't commit the JSON to the repo):

```bash
export GOOGLE_APPLICATION_CREDENTIALS="/path/to/service-account.json"
```

2. From the `movie-agent-server` directory, run the ADK API server in A2A mode
   and point it at this folder:

```bash
cd movie-agent-server
adk api_server --a2a --port 9000 --allow_origins="*" ./google-adk-a2a
```

3. The server will expose agent endpoints for programmatic consumption. See the
   ADK docs for next steps and API details:

- Expose (quickstart): https://google.github.io/adk-docs/a2a/quickstart-exposing/#next-steps
- Consume (quickstart): https://google.github.io/adk-docs/a2a/quickstart-consuming/

Notes
- The `entrypoint` in `agent.json` refers to a Python module path that must be
  importable from the `movie-agent-server` package layout. The default in this
  repo is `movie-tool-agent.agent:root_agent`.
- If the ADK CLI cannot find the agent, verify `PYTHONPATH` or run the server
  from the repo root so the package modules are importable.
