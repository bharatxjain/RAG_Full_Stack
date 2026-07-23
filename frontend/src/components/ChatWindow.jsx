import { useState, useRef, useEffect } from 'react'
import MessageBubble from './MessageBubble'
import SourceList from './SourceList'

// Resolved at BUILD time by Vite. Must be a URL the BROWSER can reach,
// not a Docker-internal hostname like "backend", since fetch() runs
// client-side in the user's browser, outside the Docker network.
const API_URL = import.meta.env.VITE_API_URL || 'http://localhost:8000'

export default function ChatWindow() {
  const [messages, setMessages] = useState([])
  const [question, setQuestion] = useState('')
  const [loading, setLoading] = useState(false)
  const scrollRef = useRef(null)

  useEffect(() => {
    scrollRef.current?.scrollIntoView({ behavior: 'smooth' })
  }, [messages])

  async function handleSubmit(e) {
    e.preventDefault()
    const q = question.trim()
    if (!q || loading) return

    setMessages((prev) => [...prev, { role: 'user', text: q }])
    setQuestion('')
    setLoading(true)

    try {
      const res = await fetch(`${API_URL}/query`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ question: q }),
      })
      if (!res.ok) throw new Error(`Server error: ${res.status}`)
      const data = await res.json()

      setMessages((prev) => [
        ...prev,
        { role: 'bot', text: data.answer, sources: data.sources },
      ])
    } catch (err) {
      setMessages((prev) => [
        ...prev,
        { role: 'bot', text: `Error: ${err.message}` },
      ])
    } finally {
      setLoading(false)
    }
  }

  return (
    <div className="chat-window">
      <div className="chat-log">
        {messages.map((m, i) => (
          <MessageBubble key={i} role={m.role} text={m.text}>
            <SourceList sources={m.sources} />
          </MessageBubble>
        ))}
        {loading && <MessageBubble role="bot" text="Thinking..." />}
        <div ref={scrollRef} />
      </div>

      <form className="chat-input-row" onSubmit={handleSubmit}>
        <input
          type="text"
          value={question}
          onChange={(e) => setQuestion(e.target.value)}
          placeholder="Ask a question about your documents..."
          disabled={loading}
        />
        <button type="submit" disabled={loading}>
          Ask
        </button>
      </form>
    </div>
  )
}
