'use client'
import { useEffect, useRef, useCallback } from 'react'
import ChatMessage from './ChatMessage'
import NeuralPulse from '@/components/ui/NeuralPulse'
import { useScrollFade } from '@/hooks/useScrollFade'
import type { Message, ChatStatus } from '@/types/chat'

const MAX_VISIBLE = 100

interface ChatMessageListProps {
  messages: Message[]
  status: ChatStatus
  onRetry?: () => void
}

export default function ChatMessageList({ messages, status, onRetry }: ChatMessageListProps) {
  const containerRef = useRef<HTMLDivElement>(null)
  const bottomRef = useRef<HTMLDivElement>(null)
  const isAtBottomRef = useRef(true)
  const handleScrollFade = useScrollFade()

  const visible = messages.filter(m => !(m.role === 'assistant' && m.content === ''))
  const truncated = visible.length > MAX_VISIBLE
  const display = truncated ? visible.slice(-MAX_VISIBLE) : visible
  const lastIdx = display.length - 1

  const handleScroll = useCallback((e: React.UIEvent<HTMLDivElement>) => {
    const el = containerRef.current
    if (!el) return
    isAtBottomRef.current = el.scrollTop + el.clientHeight >= el.scrollHeight - 100
    handleScrollFade(e)
  }, [handleScrollFade])

  useEffect(() => {
    if (!isAtBottomRef.current) return
    bottomRef.current?.scrollIntoView({ behavior: 'smooth' })
  }, [messages.length, status])

  return (
    <div
      ref={containerRef}
      onScroll={handleScroll}
      className="flex-1 min-h-0 overflow-y-auto px-4 py-4 scroll-fade"
    >
      <div className="flex flex-col gap-4">
        {truncated && (
          <p className="text-xs text-muted-foreground text-center py-1">
            Mostrando últimas 100 mensagens
          </p>
        )}
        {display.map((msg, i) => (
          <ChatMessage
            key={msg.id}
            message={msg}
            isStreaming={status === 'streaming' && i === lastIdx && msg.role === 'assistant'}
            isError={status === 'error' && i === lastIdx && msg.role === 'assistant'}
            onRetry={onRetry}
          />
        ))}
        {status === 'loading' && <NeuralPulse />}
        <div ref={bottomRef} />
      </div>
    </div>
  )
}
