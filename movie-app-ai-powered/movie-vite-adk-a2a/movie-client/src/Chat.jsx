import { useState, useRef, useEffect } from 'react'

// Chat component: creates a session at /apps/{app_name}/users/{user_id}/sessions
// (POST { state: {} }) and uses the returned session id when posting to
// http://localhost:9000/run_sse. Streams SSE-style responses where lines
// prefixed with "data:" are appended incrementally to the assistant reply.

export default function Chat() {
  const [input, setInput] = useState('')
  const [messages, setMessages] = useState([]) // {role: 'user'|'assistant', text}
  const [streaming, setStreaming] = useState(false)
  const [typingEnabled, setTypingEnabled] = useState(true)
  
  const abortRef = useRef(null)
  const sessionRef = useRef(null)
  const SESSION_KEY = 'movie_tool_agent_session_id'
  const queueRef = useRef([]) // queued text chunks to type
  const typingRef = useRef(false)
  const TYPING_DELAY_MS = 25 // per-character typing delay (ms)

  // Ensure a session exists. Caches in sessionRef for the lifetime of the component.
  async function ensureSession() {
    if (sessionRef.current) return sessionRef.current
    // try to reuse session id from localStorage
    try {
      const saved = localStorage.getItem(SESSION_KEY)
      if (saved) {
        console.log('Loaded session id from localStorage:', saved)
        sessionRef.current = saved
        return saved
      }
    } catch (e) {
      // ignore localStorage errors
      console.warn('localStorage access failed', e)
    }
    try {
      console.log('Creating session for app/movie-tool-agent user/movie_guest...')
      const res = await fetch('http://localhost:9000/apps/movie-tool-agent/users/movie_guest/sessions', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ state: {} }),
      })
      console.log('Session creation response status:', res.status)
      if (!res.ok) throw new Error(`create session failed: ${res.status}`)
      const data = await res.json()
      console.log('Session creation response body:', data)
      // Expect top-level `id` field per spec
      const id = data && (data.id || data.session_id || (data.session && data.session.id))
      if (!id) throw new Error('no session id returned')
      console.log('Using session id:', id)
      sessionRef.current = id
      try {
        localStorage.setItem(SESSION_KEY, id)
        console.log('Saved session id to localStorage')
      } catch (e) {
        console.warn('Failed to save session id to localStorage', e)
      }
      return id
    } catch (err) {
      console.error('Session creation error', err)
      throw err
    }
  }

  function resetSession() {
    console.log('Resetting session...')
    try {
      localStorage.removeItem(SESSION_KEY)
    } catch (e) {
      console.warn('Failed to clear localStorage', e)
    }
    sessionRef.current = null
    setMessages([])
    setInput('')
    // Cancel any ongoing stream
    if (abortRef.current) {
      abortRef.current.abort()
      abortRef.current = null
    }
    setStreaming(false)
    queueRef.current = []
    typingRef.current = false
  }

  function sleep(ms) {
    return new Promise((res) => setTimeout(res, ms))
  }

  // Enqueue text to be typed; starts the processor if idle
  function enqueueText(txt) {
    if (!txt) return
    queueRef.current.push(txt)
    if (!typingRef.current) {
      processQueue()
    }
  }

  // Process queued text chunks sequentially and type them character-by-character
  async function processQueue() {
    if (typingRef.current) return
    typingRef.current = true
    
    while (queueRef.current.length > 0) {
      const next = queueRef.current.shift()
      if (!next) continue
      
      if (!typingEnabled) {
        // Instant append
        setMessages((prev) => {
          const copy = [...prev]
          const lastIdx = copy.length - 1
          if (lastIdx >= 0 && copy[lastIdx].role === 'assistant') {
            copy[lastIdx] = { ...copy[lastIdx], text: (copy[lastIdx].text || '') + next }
          }
          return copy
        })
        // minimal delay to yield UI
        await sleep(5)
      } else {
        // Typing effect
        for (let i = 0; i < next.length; i++) {
          const ch = next[i]
          // append single char to last assistant message
          setMessages((prev) => {
            const copy = [...prev]
            const lastIdx = copy.length - 1
            if (lastIdx >= 0 && copy[lastIdx].role === 'assistant') {
              copy[lastIdx] = { ...copy[lastIdx], text: (copy[lastIdx].text || '') + ch }
            }
            return copy
          })
          // small delay to simulate typing
          await sleep(TYPING_DELAY_MS)
          // if stream was aborted, stop typing? 
          // Actually we usually want to finish typing what we have, but if reset happened:
          if (!sessionRef.current && messages.length === 0) {
             // Session was reset mid-typing
             typingRef.current = false
             return 
          }
        }
      }
    }
    typingRef.current = false
  }

  // Try to extract human-readable text from an SSE data payload.
  function extractTextFromSSEData(raw) {
    if (!raw) return ''
    const s = raw.trim()
    if (!s) return ''
    try {
      const obj = JSON.parse(s)
      if (obj && obj.content && Array.isArray(obj.content.parts)) {
        const partsText = obj.content.parts.map((p) => (p && p.text) ? p.text : '').join('')
        return partsText
      }
      if (obj && typeof obj.text === 'string') return obj.text
      if (obj && obj.content && typeof obj.content === 'string') return obj.content
      return JSON.stringify(obj)
    } catch (e) {
      return raw
    }
  }

  function appendMessage(role, text) {
    setMessages((m) => [...m, { role, text }])
  }

  async function send() {
    const trimmed = input.trim()
    if (!trimmed || streaming) return

    appendMessage('user', trimmed)
    setInput('')

    // prepare assistant placeholder
    appendMessage('assistant', '')
    setStreaming(true)

    const controller = new AbortController()
    abortRef.current = controller

    try {
      // create or fetch session id first
      const sessionId = await ensureSession()
      console.log('Sending message to run_sse, session id:', sessionId)
      const payload = {
        app_name: 'movie-tool-agent',
        user_id: 'movie_guest',
        session_id: sessionId,
        new_message: {
          role: 'user',
          parts: [{ text: trimmed }],
        },
        streaming: true,
      }
      console.log('Posting to /run_sse payload:', payload)

      const res = await fetch('http://localhost:9000/run_sse', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(payload),
        signal: controller.signal,
      })
      console.log('/run_sse response status:', res.status)

      if (!res.body) throw new Error('No response body')

      const reader = res.body.getReader()
      const decoder = new TextDecoder()
      let buffer = ''

      while (true) {
        const { value, done } = await reader.read()
        if (done) break
        const chunkStr = decoder.decode(value, { stream: true })
        buffer += chunkStr

        const parts = buffer.split("\n\n")
        buffer = parts.pop() || ''

        for (const part of parts) {
          const lines = part.split(/\r?\n/)
          const dataLines = lines
            .filter((l) => l.startsWith('data:'))
            .map((l) => l.replace(/^data:\s?/, ''))
          if (dataLines.length === 0) continue
          const text = dataLines.join('\n')
          const extracted = extractTextFromSSEData(text)
          enqueueText(extracted)
        }
      }

      if (buffer) {
        const lines = buffer.split(/\r?\n/)
        const dataLines = lines
          .filter((l) => l.startsWith('data:'))
          .map((l) => l.replace(/^data:\s?/, ''))
        if (dataLines.length) {
          const text = dataLines.join('\n')
          const extracted = extractTextFromSSEData(text)
          enqueueText(extracted)
        }
      }
      console.log('run_sse stream finished')

    } catch (err) {
      if (err.name === 'AbortError') {
          console.log('Stream aborted')
      } else {
          console.error('Streaming error', err)
          setMessages((prev) => [...prev, { role: 'assistant', text: '\n[Error receiving response]' }])
      }
    } finally {
      setStreaming(false)
      abortRef.current = null
    }
  }

  function onKeyDown(e) {
    if (e.key === 'Enter' && !e.shiftKey) {
      e.preventDefault()
      send()
    }
  }

  function cancel() {
    if (abortRef.current) {
      abortRef.current.abort()
      abortRef.current = null
      setStreaming(false)
    }
    queueRef.current = []
    typingRef.current = false
  }

  return (
    <div className="chat-root">
      <div className="chat-header">
        <div className="chat-title">Movie Agent</div>
        <div className="header-controls">
            <label className="toggle-label">
                <input 
                    type="checkbox" 
                    className="toggle-checkbox"
                    checked={typingEnabled} 
                    onChange={e => setTypingEnabled(e.target.checked)} 
                />
                Typing Effect
            </label>
            <button className="reset-btn" onClick={resetSession}>
                Reset Session
            </button>
        </div>
      </div>

      <div className="chat-window">
        {messages.length === 0 && <div className="chat-empty">Start the conversation</div>}
        {messages.map((m, idx) => (
          <div key={idx} className={`chat-message ${m.role}`}>
            <div className="chat-role">{m.role === 'assistant' ? 'Agent' : 'You'}</div>
            <div className="chat-text">{m.text}</div>
          </div>
        ))}
      </div>

      <div className="chat-controls">
        <textarea
          value={input}
          onChange={(e) => setInput(e.target.value)}
          onKeyDown={onKeyDown}
          placeholder="Type a message..."
          rows={1}
        />
        <div className="chat-actions">
          <button onClick={send} disabled={streaming || input.trim() === ''}>
            {streaming ? '...' : 'Send'}
          </button>
          {streaming && (
            <button className="danger" onClick={cancel}>
              Stop
            </button>
          )}
        </div>
      </div>
    </div>
  )
}
