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
        className="px-4 py-3 text-sm text-white"
        style={{
          background: 'linear-gradient(135deg, var(--color-primary-start), var(--color-primary-end))',
          borderRadius: 'var(--radius-lg)',
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
