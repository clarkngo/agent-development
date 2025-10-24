import { useState, useRef } from 'react'

// Chat component: creates a session at /apps/{app_name}/users/{user_id}/sessions
// (POST { state: {} }) and uses the returned session id when posting to
// http://localhost:9000/run_sse. Streams SSE-style responses where lines
// prefixed with "data:" are appended incrementally to the assistant reply.

export default function Chat() {
  const [input, setInput] = useState('')
  const [messages, setMessages] = useState([]) // {role: 'user'|'assistant', text}
  const [streaming, setStreaming] = useState(false)
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
    typingRef.current = true
    while (queueRef.current.length > 0) {
      const next = queueRef.current.shift()
      if (!next) continue
      for (let i = 0; i < next.length; i++) {
        const ch = next[i]
        // append single char to last assistant message
        setMessages((prev) => {
          const copy = prev.slice()
          for (let j = copy.length - 1; j >= 0; j--) {
            if (copy[j].role === 'assistant') {
              copy[j] = { ...copy[j], text: (copy[j].text || '') + ch }
              break
            }
          }
          return copy
        })
        // small delay to simulate typing
        await sleep(TYPING_DELAY_MS)
        // if stream was aborted, stop typing
        if (!abortRef.current) {
          // continue typing but if abortRef is null it may mean finished normally; still continue
        }
      }
    }
    typingRef.current = false
  }

  // Try to extract human-readable text from an SSE data payload.
  // The backend often sends JSON like { content: { parts: [{ text: '...' }], role: 'model' }, ... }
  // Return the concatenated parts text when possible, otherwise return the raw string.
  function extractTextFromSSEData(raw) {
    if (!raw) return ''
    // If it's already a plain string without JSON, return it
    const s = raw.trim()
    if (!s) return ''
    try {
      const obj = JSON.parse(s)
      // common shape: obj.content.parts -> [{text: ''}, ...]
      if (obj && obj.content && Array.isArray(obj.content.parts)) {
        const partsText = obj.content.parts.map((p) => (p && p.text) ? p.text : '').join('')
        return partsText
      }
      // fallback: if there's a top-level text field
      if (obj && typeof obj.text === 'string') return obj.text
      // other nested common field
      if (obj && obj.content && typeof obj.content === 'string') return obj.content
      // last resort: return the stringified object without whitespace
      return JSON.stringify(obj)
    } catch (e) {
      // not JSON — return raw
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
        console.log('Received stream chunk:', chunkStr)
        buffer += chunkStr

        // parse SSE-style events separated by double-newline
        const parts = buffer.split("\n\n")
        // keep last partial in buffer
        buffer = parts.pop() || ''

        for (const part of parts) {
          // Each part may contain lines like "data: ..." possibly multiple lines
          const lines = part.split(/\r?\n/)
          const dataLines = lines
            .filter((l) => l.startsWith('data:'))
            .map((l) => l.replace(/^data:\s?/, ''))
          if (dataLines.length === 0) continue
          const text = dataLines.join('\n')
          console.log('Parsed SSE data chunk (raw):', text)
          const extracted = extractTextFromSSEData(text)
          console.log('Parsed SSE data chunk (extracted):', extracted)
          // enqueue extracted text for typing animation
          enqueueText(extracted)
        }
      }

      // If there's leftover buffer that contains data lines, handle them
      if (buffer) {
        console.log('Leftover buffer at stream end:', buffer)
        const lines = buffer.split(/\r?\n/)
        const dataLines = lines
          .filter((l) => l.startsWith('data:'))
          .map((l) => l.replace(/^data:\s?/, ''))
        if (dataLines.length) {
          const text = dataLines.join('\n')
          console.log('Parsed leftover SSE data (raw):', text)
          const extracted = extractTextFromSSEData(text)
          console.log('Parsed leftover SSE data (extracted):', extracted)
          enqueueText(extracted)
        }
      }
      console.log('run_sse stream finished')

    } catch (err) {
      console.error('Streaming error', err)
      setMessages((prev) => [...prev, { role: 'assistant', text: '\n[Error receiving response]' }])
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
    // clear any queued typing
    queueRef.current = []
    typingRef.current = false
  }

  return (
    <div className="chat-root">
      <div className="chat-window">
        {messages.length === 0 && <div className="chat-empty">Start the conversation</div>}
        {messages.map((m, idx) => (
          <div key={idx} className={`chat-message ${m.role}`}>
            <div className="chat-role">{m.role}</div>
            <div className="chat-text">{m.text}</div>
          </div>
        ))}
      </div>

      <div className="chat-controls">
        <textarea
          value={input}
          onChange={(e) => setInput(e.target.value)}
          onKeyDown={onKeyDown}
          placeholder="Type a message (Enter to send, Shift+Enter newline)"
          rows={3}
        />
        <div className="chat-actions">
          <button onClick={send} disabled={streaming || input.trim() === ''}>
            {streaming ? 'Streaming...' : 'Send'}
          </button>
          {streaming && (
            <button className="danger" onClick={cancel}>
              Cancel
            </button>
          )}
        </div>
      </div>
    </div>
  )
}
