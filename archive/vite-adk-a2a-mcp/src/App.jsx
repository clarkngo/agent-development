import React from 'react'

export default function App(){
  return (
    <div className="app-root">
      <h1>Vite + React + Google ADK (A2A + MCP)</h1>
      <p className="muted">Starter combining A2A credentials and MCP-backed server patterns.</p>

      <section>
        <h2>How to use</h2>
        <ol>
          <li>Fill `.env` with the A2A variables and MCP server configuration.</li>
          <li>Run `npm install` and `npm run dev` to start the frontend.</li>
          <li>Implement secure backend endpoints (MCP) and proxy A2A calls as needed.</li>
        </ol>
      </section>
    </div>
  )
}
