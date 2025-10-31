import React from 'react'

export default function App(){
  return (
    <div className="app-root">
      <h1>Vite + React + Google ADK (A2A)</h1>
      <p className="muted">A minimal starter that shows where to wire A2A credentials and client code.</p>

      <section>
        <h2>Next steps</h2>
        <ol>
          <li>Install the Google ADK library (see README).</li>
          <li>Populate <code>.env</code> with A2A credentials and endpoints.</li>
          <li>Use a client helper (example in README) to call ADK from the browser or a secure backend.</li>
        </ol>
      </section>
    </div>
  )
}
