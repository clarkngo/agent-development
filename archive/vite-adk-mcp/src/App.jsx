import React from 'react'

export default function App(){
  return (
    <div className="app-root">
      <h1>Vite + React + Google ADK (MCP)</h1>
      <p className="muted">A starter that demonstrates where to configure MCP (Model Context Protocol) integration.</p>

      <section>
        <h2>Notes</h2>
        <ul>
          <li>Use a secure backend to host MCP components and credentials.</li>
          <li>See `reference/gemini-fullstack` and `movie-app-react-adk` for sample MCP wiring patterns.</li>
        </ul>
      </section>
    </div>
  )
}
