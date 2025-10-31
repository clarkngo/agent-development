# Vite + React + Google ADK (A2A)

This starter shows a minimal Vite + React project and where to wire Google ADK in an A2A (application-to-application) flow.

Quick start

1. cd projects/vite-adk-a2a
2. npm install
3. copy `.env.example` -> `.env` and fill in A2A credentials
4. npm run dev

Notes
- The repository includes sample code only. Use the `reference/` folder and `movie-app-react-adk` for complete examples of ADK usage and secure backends.
- A2A flows require careful secret handling; never embed client secrets in browser code. Consider proxying ADK calls through a secure backend.

Links and references
- Reference samples: `reference/gemini-fullstack`, `reference/realtime-conversational-agent`
