import { useState, useRef, useEffect } from 'react'
import ReactMarkdown from 'react-markdown'
import { chatStream } from '../services/api'

export default function ChatModal() {
  const [open, setOpen] = useState(false)
  const [messages, setMessages] = useState([])
  const [input, setInput] = useState('')
  const [streaming, setStreaming] = useState(false)
  const endRef = useRef(null)

  useEffect(() => {
    endRef.current?.scrollIntoView({ behavior: 'smooth' })
  }, [messages])

  const handleSend = async () => {
    const text = input.trim()
    if (!text || streaming) return
    setInput('')
    const userMsg = { role: 'user', text }
    setMessages((prev) => [...prev, userMsg])
    setStreaming(true)
    setMessages((prev) => [...prev, { role: 'assistant', text: '', loading: true }])
    try {
      const history = [...messages, userMsg].map((m) => ({ role: m.role, text: m.text }))
      let full = ''
      await chatStream(text, history, (token) => {
        full += token
        setMessages((prev) => {
          const next = [...prev]
          next[next.length - 1] = { role: 'assistant', text: full, loading: false }
          return next
        })
      })
    } catch (e) {
      setMessages((prev) => {
        const next = [...prev]
        next[next.length - 1] = { role: 'assistant', text: `Error: ${e.message}`, loading: false }
        return next
      })
    }
    setStreaming(false)
  }

  return (
    <>
      {!open && (
        <button className="chat-fab" onClick={() => setOpen(true)} title="AI Chat">
          <svg width="22" height="22" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
            <path d="M21 15a2 2 0 0 1-2 2H7l-4 4V5a2 2 0 0 1 2-2h14a2 2 0 0 1 2 2z"/>
          </svg>
        </button>
      )}
      {open && (
        <div className="chat-panel">
          <div className="chat-header">
            <span>CineMatch AI</span>
            <button className="chat-close" onClick={() => setOpen(false)}>✕</button>
          </div>
          <div className="chat-body">
            {messages.length === 0 && (
              <div className="chat-welcome">
                Ask me for movie recommendations!<br />
                <em>e.g. "I want a funny sci-fi movie from the 90s"</em>
              </div>
            )}
            {messages.map((m, i) => (
              <div key={i} className={`chat-msg chat-msg-${m.role}`}>
                {m.text || m.loading ? (
                  m.loading && !m.text ? (
                    <span className="chat-dots"><span>.</span><span>.</span><span>.</span></span>
                  ) : (
                    <div className="chat-markdown">
                      <ReactMarkdown>{m.text}</ReactMarkdown>
                    </div>
                  )
                ) : null}
              </div>
            ))}
            <div ref={endRef} />
          </div>
          <div className="chat-footer">
            <input
              className="chat-input"
              placeholder="Ask for recommendations..."
              value={input}
              onChange={(e) => setInput(e.target.value)}
              onKeyDown={(e) => e.key === 'Enter' && handleSend()}
              disabled={streaming}
            />
            <button className="chat-send" onClick={handleSend} disabled={streaming || !input.trim()}>
              <svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2"><line x1="22" y1="2" x2="11" y2="13"/><polygon points="22 2 15 22 11 13 2 9 22 2"/></svg>
            </button>
          </div>
        </div>
      )}
    </>
  )
}
