'use client'
import { useState, useEffect, useCallback } from 'react'
import { subscribeToasts } from '@/lib/toast'
import type { ToastItem } from '@/lib/toast'

const BG: Record<ToastItem['type'], string> = {
  success: 'bg-academic-green/90 text-white',
  error:   'bg-academic-red/90 text-white',
  info:    'bg-surface border border-border text-foreground',
}

const PREFIX: Record<ToastItem['type'], string> = {
  success: '✓ ',
  error:   '✗ ',
  info:    '',
}

function ToastBubble({ item, onClose }: { item: ToastItem; onClose: () => void }) {
  useEffect(() => {
    const t = setTimeout(onClose, item.duration)
    return () => clearTimeout(t)
  }, [item.duration, onClose])

  return (
    <div
      className={`flex items-center gap-1 px-4 py-2.5 rounded-lg text-sm shadow-lg ${BG[item.type]}`}
      style={{ animation: 'fade-slide-up 0.3s ease-out forwards' }}
    >
      {PREFIX[item.type]}{item.message}
    </div>
  )
}

export default function ToastContainer() {
  const [toasts, setToasts] = useState<ToastItem[]>([])

  useEffect(() => subscribeToasts(item => setToasts(prev => [...prev, item])), [])

  const remove = useCallback((id: string) => setToasts(prev => prev.filter(t => t.id !== id)), [])

  if (toasts.length === 0) return null
  return (
    <div className="fixed bottom-6 right-6 z-50 flex flex-col gap-2 items-end pointer-events-none">
      {toasts.map(t => <ToastBubble key={t.id} item={t} onClose={() => remove(t.id)} />)}
    </div>
  )
}
