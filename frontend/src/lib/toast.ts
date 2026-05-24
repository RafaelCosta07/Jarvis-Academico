export type ToastType = 'success' | 'error' | 'info'

export interface ToastItem {
  id: string
  message: string
  type: ToastType
  duration: number
}

type Listener = (toast: ToastItem) => void
const listeners: Listener[] = []

export function toast(message: string, type: ToastType = 'info', duration?: number): void {
  const item: ToastItem = {
    id: crypto.randomUUID(),
    message,
    type,
    duration: duration ?? (type === 'error' ? 4000 : 2000),
  }
  listeners.forEach(l => l(item))
}

export function subscribeToasts(listener: Listener): () => void {
  listeners.push(listener)
  return () => {
    const idx = listeners.indexOf(listener)
    if (idx > -1) listeners.splice(idx, 1)
  }
}
