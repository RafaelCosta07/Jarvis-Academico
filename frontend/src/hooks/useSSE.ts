import type { SSEEvent } from '@/types/api'
import { postChat } from '@/lib/api'

interface UseSSECallbacks {
  onToken: (content: string) => void
  onDone: () => void
  onError: (message: string) => void
}

function parseBuffer(buffer: string, callbacks: UseSSECallbacks): string {
  let buf = buffer
  while (buf.includes('\n\n')) {
    const idx = buf.indexOf('\n\n')
    const raw = buf.slice(0, idx).trim()
    buf = buf.slice(idx + 2)
    if (!raw.startsWith('data: ')) continue
    try {
      const event: SSEEvent = JSON.parse(raw.slice(6))
      if (event.type === 'token') callbacks.onToken(event.content)
      else if (event.type === 'done') callbacks.onDone()
      else if (event.type === 'error') callbacks.onError(event.content)
    } catch { /* ignora JSON malformado */ }
  }
  return buf
}

async function readStream(
  reader: ReadableStreamDefaultReader<Uint8Array>,
  callbacks: UseSSECallbacks,
): Promise<void> {
  const decoder = new TextDecoder()
  let buffer = ''
  while (true) {
    const { value, done } = await reader.read()
    if (done) break
    buffer += decoder.decode(value, { stream: true })
    buffer = parseBuffer(buffer, callbacks)
  }
}

export function connectSSE(
  messages: Array<{ role: string; content: string }>,
  callbacks: UseSSECallbacks,
): () => void {
  const controller = new AbortController()
  void (async () => {
    try {
      const res = await postChat(messages, controller.signal)
      if (!res.ok || !res.body) { callbacks.onError(`Erro HTTP ${res.status}`); return }
      await readStream(res.body.getReader(), callbacks)
    } catch (err) {
      if (!controller.signal.aborted) callbacks.onError('Erro ao conectar. Tente novamente.')
    }
  })()
  return () => controller.abort()
}
