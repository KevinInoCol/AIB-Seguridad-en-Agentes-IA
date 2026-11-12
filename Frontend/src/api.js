// Cliente del backend. Las rutas /api/* las reenvía el proxy de Vite.

export async function getHealth() {
  const res = await fetch('/api/health')
  if (!res.ok) throw new Error(`Backend no disponible (${res.status})`)
  return res.json()
}

export async function sendMessage(message, threadId) {
  const res = await fetch('/api/chat', {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ message, thread_id: threadId }),
  })
  if (!res.ok) {
    const data = await res.json().catch(() => ({}))
    throw new Error(data.detail || `Error del backend (${res.status})`)
  }
  const data = await res.json()
  return data.reply
}
