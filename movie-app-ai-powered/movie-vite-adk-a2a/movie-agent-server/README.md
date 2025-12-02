# movie-agent-server

Run the API server
```
cd movie-agent-server
# For standard local development (uses ADK dev server)
adk api_server --port 9000 --allow_origins="*"
```

Run the API server in A2A mode (application-to-application)
```
cd movie-agent-server
# Use the ADK CLI with the --a2a flag to serve agents in A2A mode.
# Ensure you set `GOOGLE_APPLICATION_CREDENTIALS` to a service account JSON
# that has appropriate permissions before running.
export GOOGLE_APPLICATION_CREDENTIALS="/path/to/service-account.json"
adk api_server --a2a --port 9000 --allow_origins="*"
```

Notes for A2A
- A2A mode exposes agents for programmatic access using application credentials.
- You may need to create an `agent.json` card for each agent you want to expose when using `--a2a` (see repo references).
- Do not commit service account JSON files or secrets into the repository. Use `.env` or environment variables instead.