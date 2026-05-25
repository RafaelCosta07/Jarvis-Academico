'use client'
import { useRef, useState, useCallback } from 'react'
import { Textarea } from '@/components/ui/textarea'
import GradientButton from '@/components/ui/GradientButton'
import { Send } from 'lucide-react'

interface ChatInputProps {
  onSend: (content: string) => void
  disabled?: boolean
}

export default function ChatInput({ onSend, disabled = false }: ChatInputProps) {
  const [value, setValue] = useState('')
  const [focused, setFocused] = useState(false)
  const [flashing, setFlashing] = useState(false)
  const ref = useRef<HTMLTextAreaElement>(null)

  const resize = useCallback(() => {
    const el = ref.current
    if (!el) return
    el.style.height = 'auto'
    el.style.height = `${Math.min(el.scrollHeight, 144)}px`
  }, [])

  const send = useCallback(() => {
    const trimmed = value.trim()
    if (!trimmed || disabled) return
    onSend(trimmed)
    setValue('')
    if (ref.current) ref.current.style.height = 'auto'
    setFlashing(true)
    setTimeout(() => setFlashing(false), 700)
  }, [value, disabled, onSend])

  const onKeyDown = useCallback((e: React.KeyboardEvent<HTMLTextAreaElement>) => {
    if (e.key === 'Enter' && !e.shiftKey) { e.preventDefault(); send() }
  }, [send])

  return (
    <div className="shrink-0 relative flex items-end gap-2 p-4 border-t border-border">
      {flashing && <div className="send-flash-bar" />}
      <Textarea
        ref={ref}
        value={value}
        onChange={(e) => { setValue(e.target.value); resize() }}
        onKeyDown={onKeyDown}
        onFocus={() => setFocused(true)}
        onBlur={() => setFocused(false)}
        disabled={disabled}
        placeholder="Digite sua mensagem..."
        rows={1}
        className={`resize-none min-h-[40px] max-h-36 flex-1 bg-surface border-border
          focus-visible:ring-0 focus-visible:ring-offset-0
          ${focused ? 'chat-input-focused' : ''}`}
      />
      <GradientButton onClick={send} disabled={disabled || !value.trim()} aria-label="Enviar">
        <Send className="w-4 h-4" />
      </GradientButton>
    </div>
  )
}
