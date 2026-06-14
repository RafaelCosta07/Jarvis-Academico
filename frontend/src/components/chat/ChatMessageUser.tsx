import { format } from 'date-fns'

interface ChatMessageUserProps {
  content: string
  timestamp: Date
}

export default function ChatMessageUser({ content, timestamp }: ChatMessageUserProps) {
  return (
    <div
      className="flex flex-col items-end gap-1 max-w-[75%] ml-auto"
      style={{ animation: 'fade-slide-up 0.3s ease-out forwards' }}
    >
      <div
        className="px-4 py-3 text-sm leading-relaxed text-white"
        style={{
          background: 'var(--color-primary)',
          borderRadius: 'var(--radius-lg) var(--radius-lg) var(--radius-sm) var(--radius-lg)',
        }}
      >
        {content}
      </div>
      <span className="text-xs font-mono text-muted-foreground">
        {format(timestamp, 'HH:mm')}
      </span>
    </div>
  )
}
