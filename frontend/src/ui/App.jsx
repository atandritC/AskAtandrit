import { useEffect, useRef, useState } from 'react'
import ReactMarkdown from 'react-markdown'
import remarkGfm from 'remark-gfm'
import {
  ArrowDownToLine, ArrowUp, FileText, Menu, Moon, Plus,
  Sun, X, Paperclip, Sparkles,
} from 'lucide-react'

const suggestions = [
  { eyebrow: '01 · PROFILE', title: 'Candidate overview', question: 'Could you give me a concise overview of Atandrit’s background and strengths?' },
  { eyebrow: '02 · JOURNEY', title: 'Experience', question: 'Tell me about Atandrit’s professional experience and the impact of his work.' },
  { eyebrow: '03 · SELECTED WORK', title: 'Projects & skills', question: 'What projects has Atandrit worked on, and what skills did he use?' },
]

function Brand({ compact = false }) {
  return <div className={`brand ${compact ? 'brand-compact' : ''}`} aria-label="Ask.Atandrit">
    <span className="brand-copy"><strong>Ask.Atandrit</strong>{!compact && <small>YOUR CANDIDATE ASSISTANT</small>}</span>
  </div>
}

function formatBytes(size) {
  if (size < 1024) return `${size} B`
  if (size < 1024 * 1024) return `${(size / 1024).toFixed(0)} KB`
  return `${(size / (1024 * 1024)).toFixed(1)} MB`
}

function MessageText({ text }) {
  return <div className="message-text"><ReactMarkdown remarkPlugins={[remarkGfm]} components={{
    a: ({ node, ...props }) => <a {...props} target="_blank" rel="noreferrer" />,
  }}>{text}</ReactMarkdown></div>
}

export default function App() {
  const [theme, setTheme] = useState(() => localStorage.getItem('ask-atandrit-theme') || (matchMedia('(prefers-color-scheme: dark)').matches ? 'dark' : 'light'))
  const [messages, setMessages] = useState([])
  const [draft, setDraft] = useState('')
  const [files, setFiles] = useState([])
  const [busy, setBusy] = useState(false)
  const [error, setError] = useState('')
  const [drawerOpen, setDrawerOpen] = useState(false)
  const [dragging, setDragging] = useState(false)
  const fileInput = useRef(null)
  const textarea = useRef(null)
  const endOfMessages = useRef(null)
  const menuButton = useRef(null)
  const closeButton = useRef(null)

  useEffect(() => {
    document.documentElement.dataset.theme = theme
    localStorage.setItem('ask-atandrit-theme', theme)
  }, [theme])

  useEffect(() => endOfMessages.current?.scrollIntoView({ behavior: 'smooth', block: 'end' }), [messages])

  useEffect(() => {
    if (!drawerOpen) return undefined
    closeButton.current?.focus()
    function keepFocusInDrawer(event) {
      if (event.key === 'Escape') {
        setDrawerOpen(false)
        return
      }
      if (event.key !== 'Tab') return
      const drawer = closeButton.current?.closest('[role="dialog"]')
      const focusable = drawer?.querySelectorAll('button:not([disabled]), a[href]')
      if (!focusable?.length) return
      const first = focusable[0]
      const last = focusable[focusable.length - 1]
      if (event.shiftKey && document.activeElement === first) {
        event.preventDefault()
        last.focus()
      } else if (!event.shiftKey && document.activeElement === last) {
        event.preventDefault()
        first.focus()
      }
    }
    document.addEventListener('keydown', keepFocusInDrawer)
    return () => {
      document.removeEventListener('keydown', keepFocusInDrawer)
      menuButton.current?.focus()
    }
  }, [drawerOpen])

  function addFiles(incoming) {
    const accepted = [...incoming].filter((file) => /\.(txt|pdf|docx)$/i.test(file.name))
    const rejected = [...incoming].filter((file) => !/\.(txt|pdf|docx)$/i.test(file.name))
    setFiles((current) => {
      const unique = [...current]
      for (const file of accepted) if (!unique.some((item) => item.name === file.name && item.size === file.size && item.lastModified === file.lastModified)) unique.push(file)
      return unique
    })
    setError(rejected.length ? 'Please choose a .txt, .pdf, or .docx file.' : '')
    if (fileInput.current) fileInput.current.value = ''
  }

  async function sendMessage(text = draft) {
    const content = text.trim()
    if ((!content && !files.length) || busy) return
    const userMessage = { role: 'user', content: content || 'Please take a look at the attached file.', fileNames: files.map((file) => file.name) }
    const nextMessages = [...messages, userMessage]
    setMessages([...nextMessages, { role: 'assistant', content: '', streaming: true }])
    setDraft('')
    setBusy(true)
    setError('')
    const form = new FormData()
    form.append('messages_json', JSON.stringify({
      messages: nextMessages.map(({ role, content: body }) => ({ role, content: body })),
    }))
    // Keep attachments for this browser session and include them on follow-up questions too.
    for (const file of files) form.append('attachments', file)
    try {
      const response = await fetch('/chat', { method: 'POST', body: form })
      if (!response.ok) {
        let detail = `The request failed (${response.status}).`
        try { detail = (await response.json()).detail || detail } catch { /* keep readable fallback */ }
        throw new Error(detail)
      }
      if (!response.body) throw new Error('The server did not return a response stream.')
      const reader = response.body.getReader()
      const decoder = new TextDecoder()
      let answer = ''
      while (true) {
        const { value, done } = await reader.read()
        if (done) break
        answer += decoder.decode(value, { stream: true })
        setMessages([...nextMessages, { role: 'assistant', content: answer, streaming: true }])
      }
      answer += decoder.decode()
      setMessages([...nextMessages, { role: 'assistant', content: answer, streaming: false }])
    } catch (err) {
      setMessages(nextMessages)
      setError(err.message === 'Failed to fetch' ? 'Could not reach the chat service. Make sure the backend is running, then try again.' : err.message)
    } finally {
      setBusy(false)
      requestAnimationFrame(() => textarea.current?.focus())
    }
  }

  function newConversation() {
    if (busy) return
    setMessages([])
    setDraft('')
    setFiles([])
    setError('')
    setDrawerOpen(false)
    textarea.current?.focus()
  }

  function handleSubmit(event) {
    event.preventDefault()
    sendMessage()
  }

  function handleKeyDown(event) {
    if (event.key === 'Enter' && !event.shiftKey) {
      event.preventDefault()
      sendMessage()
    }
  }

  const hasMessages = messages.length > 0
  const sidebar = <>
    <div className="sidebar-top"><Brand /><button ref={closeButton} className="icon-button drawer-close" aria-label="Close menu" onClick={() => setDrawerOpen(false)}><X size={19} /></button></div>
    <button className="new-chat-button" onClick={newConversation}><Plus size={17} strokeWidth={1.8} /> New conversation</button>
    <div className="side-section">
      <p className="section-label">QUICK LINKS</p>
      <a className="side-link resume-link" href="/resume" target="_blank" rel="noreferrer"><ArrowDownToLine size={16} /> Download resume</a>
      <button className="side-link" onClick={() => fileInput.current?.click()}><Paperclip size={16} /> Upload a file</button>
    </div>
    <div className="side-section about-section">
      <p className="section-label">ABOUT THIS CHAT</p>
      <p>Ask about Atandrit’s background, work, or fit for a role.</p>
    </div>
    <p className="sidebar-foot">Built to make introductions easier.</p>
  </>

  return <div className="app-shell" onDragOver={(event) => { event.preventDefault(); setDragging(true) }} onDragLeave={(event) => { if (!event.currentTarget.contains(event.relatedTarget)) setDragging(false) }} onDrop={(event) => { event.preventDefault(); setDragging(false); addFiles(event.dataTransfer.files) }}>
    <aside className="sidebar">{sidebar}</aside>
    {drawerOpen && <><button className="drawer-scrim" aria-label="Close menu" onClick={() => setDrawerOpen(false)} /><aside className="mobile-drawer" role="dialog" aria-modal="true" aria-label="Website menu">{sidebar}</aside></>}
    <main className="main-panel">
      <header className="topbar">
        <button ref={menuButton} className="icon-button mobile-menu" aria-label="Open menu" onClick={() => setDrawerOpen(true)}><Menu size={20} /></button>
        <span className="topbar-caption">A personal introduction</span>
        <button className="theme-button" onClick={() => setTheme(theme === 'dark' ? 'light' : 'dark')} aria-label={`Switch to ${theme === 'dark' ? 'light' : 'dark'} mode`} title={`Switch to ${theme === 'dark' ? 'light' : 'dark'} mode`}>
          {theme === 'dark' ? <Sun size={16} /> : <Moon size={16} />}<span>{theme === 'dark' ? 'Light' : 'Dark'}</span>
        </button>
      </header>

      <section className={`conversation ${hasMessages ? 'conversation-active' : 'conversation-welcome'}`} aria-label="Chat conversation">
        {!hasMessages ? <div className="welcome-content">
          <div className="welcome-heading"><h1>Ask.Atandrit</h1><h2>Hello, I’m Atandrit.</h2></div>
          <p className="welcome-description">Think of this as a more conversational resume. What would you like to know?</p>
          <div className="suggestions-heading">EXPLORE</div>
          <div className="suggestion-grid">{suggestions.map((item) => <button className="suggestion-card" key={item.title} onClick={() => sendMessage(item.question)} disabled={busy}>
            <span>{item.eyebrow}</span><strong>{item.title} <span className="suggestion-arrow" aria-hidden="true">↗</span></strong>
          </button>)}</div>
          <button className="starter-question" onClick={() => { textarea.current?.focus(); setDraft('What kind of role is Atandrit looking for?') }}><span aria-hidden="true">↗</span> What kind of role is Atandrit looking for?</button>
        </div> : <div className="message-list" aria-live="polite" aria-relevant="additions text">
          {messages.map((message, index) => <article className={`message-row ${message.role}`} key={`${index}-${message.role}`}>
            <div className="message-body">
              {message.role === 'user' && message.fileNames?.length > 0 && <div className="message-files">{message.fileNames.map((name, fileIndex) => <span className="message-file" key={`${name}-${fileIndex}`}><FileText size={14} />{name}</span>)}</div>}
              <MessageText text={message.content} />
              {message.streaming && !message.content && <span className="typing-indicator" aria-label="Atandrit is thinking"><i /><i /><i /></span>}
            </div>
          </article>)}
          <div ref={endOfMessages} />
        </div>}
      </section>

      <div className="composer-area">
        {files.length > 0 && <div className="attachment-list" aria-label="Attached files">{files.map((file) => <span className="attachment-chip" key={`${file.name}-${file.lastModified}`}><FileText size={15} /><span className="attachment-name">{file.name}<small>{formatBytes(file.size)}</small></span><button aria-label={`Remove ${file.name}`} onClick={() => setFiles((items) => items.filter((item) => item !== file))} disabled={busy}><X size={15} /></button></span>)}</div>}
        {error && <div className="error-message" role="alert">{error}</div>}
        <form className={`composer ${dragging ? 'composer-dragging' : ''}`} onSubmit={handleSubmit}>
          {dragging && <div className="drop-overlay"><Paperclip size={18} /> Drop files to attach</div>}
          <label className="sr-only" htmlFor="message-input">Ask anything about Atandrit</label>
          <textarea id="message-input" ref={textarea} value={draft} onChange={(event) => setDraft(event.target.value)} onKeyDown={handleKeyDown} placeholder="Ask anything about Atandrit…" rows={2} disabled={busy} />
          <div className="composer-tools">
            <div className="composer-actions"><button type="button" className="attach-button" onClick={() => fileInput.current?.click()} disabled={busy}><Paperclip size={15} /><span>Attach a file</span></button><span className="file-hint">TXT, PDF, DOCX</span></div>
            <button className="send-button" type="submit" disabled={busy || (!draft.trim() && !files.length)} aria-label={busy ? 'Response in progress' : 'Send message'}>{busy ? <Sparkles className="busy-icon" size={17} /> : <ArrowUp size={19} />}</button>
          </div>
        </form>
        <input ref={fileInput} className="sr-only" type="file" accept=".txt,.pdf,.docx,text/plain,application/pdf,application/vnd.openxmlformats-officedocument.wordprocessingml.document" multiple onChange={(event) => addFiles(event.target.files)} aria-label="Choose files to attach" />
        <p className="composer-note">AI responses are based on Atandrit’s shared profile and your materials.</p>
      </div>
    </main>
    {dragging && <div className="global-drop-hint" aria-hidden="true">Drop files to add them to your conversation</div>}
  </div>
}
