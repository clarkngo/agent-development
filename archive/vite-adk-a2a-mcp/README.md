# Vite + React + Google ADK (A2A + MCP)

This starter combines A2A and MCP integration patterns. Use it as a reference when you need both direct application credentials and server-side MCP workflows.

Quick start

1. cd projects/vite-adk-a2a-mcp
2. npm install
3. copy `.env.example` -> `.env` and fill in both A2A and MCP values
4. npm run dev

Notes
- Follow security best practices: A2A secrets should never be shipped in client-side bundles. Proxy or sign requests via your MCP server.
- Consult `reference/gemini-fullstack` and `movie-app-react-adk` to see practical server + frontend wiring.
