import ReactMarkdown from 'react-markdown'
import remarkGfm from 'remark-gfm'
import { format } from 'date-fns'
import GlassCard from '@/components/ui/GlassCard'

interface ChatMessageAssistantProps {
  content: string
  timestamp: Date
  isStreaming?: boolean
  isError?: boolean
  onRetry?: () => void
}

export default function ChatMessageAssistant({ content, timestamp, isStreaming, isError, onRetry }: ChatMessageAssistantProps) {
  return (
    <div
      className="flex flex-col gap-1 max-w-[85%]"
      style={{ animation: 'fade-slide-up 0.3s ease-out forwards' }}
    >
      <GlassCard error={isError}>
        {isError && (
          <p className="flex items-center gap-1 text-xs text-academic-red mb-2">⚠ Erro na resposta</p>
        )}
        <div className="prose-jarvis text-sm text-foreground">
          <ReactMarkdown remarkPlugins={[remarkGfm]}>{content}</ReactMarkdown>
        </div>
        {isStreaming && <span style={{ animation: 'blink 1s step-end infinite' }}>▌</span>}
        {isError && onRetry && (
          <button
            onClick={onRetry}
            className="mt-2 text-xs text-primary-start hover:underline transition-colors cursor-pointer"
          >
            ↺ Tentar novamente
          </button>
        )}
      </GlassCard>
      <span className="text-xs font-mono text-muted-foreground">{format(timestamp, 'HH:mm')}</span>
    </div>
  )
}
