import { useEffect, useRef, useState } from 'react'
import { getHealth, sendMessage } from './api'
import './App.css'

const SUGERENCIAS = [
  'Busco alquilar un departamento de 2 dormitorios',
  'Quiero comprar una casa con cochera',
  '¿Qué documentos piden para alquilar?',
  'Quiero vender mi terreno',
]

const nuevoThreadId = () => crypto.randomUUID()

// Nombres legibles de los filtros de Model Armor.
const NOMBRE_FILTRO = {
  pi_and_jailbreak: 'Prompt injection / jailbreak',
  malicious_uris: 'URL maliciosa',
  sdp: 'Datos sensibles',
  csam: 'Contenido CSAM',
  'rai:hate_speech': 'Discurso de odio',
  'rai:dangerous': 'Contenido peligroso',
  'rai:sexually_explicit': 'Contenido sexual',
  'rai:harassment': 'Acoso',
}

function describirGuardrail(g) {
  const donde = g.stage === 'input' ? 'Mensaje bloqueado' : 'Respuesta bloqueada'
  if (g.error) return `${donde}: Model Armor no respondió (fail-closed)`
  const filtros = g.filters.map((f) => NOMBRE_FILTRO[f] ?? f).join(', ')
  return `${donde} por Model Armor${filtros ? ` · ${filtros}` : ''}`
}

export default function App() {
  const [health, setHealth] = useState(null)
  const [healthError, setHealthError] = useState(null)
  const [threadId, setThreadId] = useState(nuevoThreadId)
  const [messages, setMessages] = useState([])
  const [input, setInput] = useState('')
  const [loading, setLoading] = useState(false)
  const [error, setError] = useState(null)
  const endRef = useRef(null)
  const inputRef = useRef(null)

  useEffect(() => {
    getHealth()
      .then(setHealth)
      .catch((e) => setHealthError(e.message))
  }, [])

  useEffect(() => {
    endRef.current?.scrollIntoView({ behavior: 'smooth' })
  }, [messages, loading])

  async function enviar(texto) {
    const mensaje = texto.trim()
    if (!mensaje || loading) return
    setError(null)
    setInput('')
    setMessages((prev) => [...prev, { role: 'user', content: mensaje }])
    setLoading(true)
    try {
      const { reply, guardrail } = await sendMessage(mensaje, threadId)
      setMessages((prev) => {
        const next = [...prev]
        // Si se bloqueó la entrada, marca también el mensaje del usuario.
        if (guardrail?.stage === 'input') {
          next[next.length - 1] = { ...next[next.length - 1], blocked: true }
        }
        return [...next, { role: 'assistant', content: reply, guardrail }]
      })
    } catch (e) {
      setError(e.message)
    } finally {
      setLoading(false)
      inputRef.current?.focus()
    }
  }

  function nuevaConversacion() {
    setThreadId(nuevoThreadId())
    setMessages([])
    setError(null)
    setInput('')
    inputRef.current?.focus()
  }

  function onKeyDown(e) {
    if (e.key === 'Enter' && !e.shiftKey) {
      e.preventDefault()
      enviar(input)
    }
  }

  const botName = health?.bot_name ?? 'Asesora'
  const empresa = health?.empresa ?? 'Inmobiliaria'

  return (
    <div className="app">
      <header className="header">
        <div className="identity">
          <div className="avatar" aria-hidden="true">{botName[0]}</div>
          <div>
            <h1>{botName}</h1>
            <p className="subtitle">{empresa}</p>
          </div>
        </div>
        <div className="header-actions">
          {health && (
            <span
              className={`guard-badge ${health.guardrails?.enabled ? 'on' : 'off'}`}
              title={
                health.guardrails?.enabled
                  ? `Template: ${health.guardrails.template} · fail-${health.guardrails.fail_mode}`
                  : 'Guardrails desactivados (MODEL_ARMOR_ENABLED=false)'
              }
            >
              {health.guardrails?.enabled ? 'Model Armor activo' : 'Sin guardrails'}
            </span>
          )}
          <span
            className={`model-badge ${healthError ? 'off' : health ? 'on' : ''}`}
            title={healthError ?? 'Proveedor y modelo activos en el backend'}
          >
            <span className="dot" />
            {healthError
              ? 'Backend desconectado'
              : health
                ? `${health.provider} · ${health.model}`
                : 'Conectando…'}
          </span>
          <button className="btn-secondary" onClick={nuevaConversacion} disabled={loading}>
            Nueva conversación
          </button>
        </div>
      </header>

      <main className="chat">
        {messages.length === 0 && !loading ? (
          <div className="empty">
            <h2>¿En qué te ayudo hoy?</h2>
            <p>Cuéntame qué inmueble buscas o quieres vender.</p>
            <div className="chips">
              {SUGERENCIAS.map((s) => (
                <button key={s} className="chip" onClick={() => enviar(s)} disabled={!!healthError}>
                  {s}
                </button>
              ))}
            </div>
          </div>
        ) : (
          <ul className="messages">
            {messages.map((m, i) => (
              <li key={i} className={`msg ${m.role}`}>
                <div className={`bubble ${m.blocked ? 'blocked' : ''}`}>{m.content}</div>
                {m.guardrail && <div className="guard-note">{describirGuardrail(m.guardrail)}</div>}
              </li>
            ))}
            {loading && (
              <li className="msg assistant">
                <div className="bubble typing" aria-label={`${botName} está escribiendo`}>
                  <span /><span /><span />
                </div>
              </li>
            )}
          </ul>
        )}
        <div ref={endRef} />
      </main>

      <footer className="composer">
        {error && <div className="error" role="alert">{error}</div>}
        <div className="composer-row">
          <textarea
            ref={inputRef}
            value={input}
            onChange={(e) => setInput(e.target.value)}
            onKeyDown={onKeyDown}
            placeholder="Escribe tu mensaje…"
            rows={1}
            maxLength={4000}
            autoFocus
          />
          <button
            className="btn-primary"
            onClick={() => enviar(input)}
            disabled={loading || !input.trim()}
          >
            Enviar
          </button>
        </div>
        <p className="hint">
          Enter para enviar · Shift+Enter para salto de línea · Conversación{' '}
          <code>{threadId.slice(0, 8)}</code>
        </p>
      </footer>
    </div>
  )
}
