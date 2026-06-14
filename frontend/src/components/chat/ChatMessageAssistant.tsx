import ReactMarkdown from 'react-markdown'
import remarkGfm from 'remark-gfm'
import { format } from 'date-fns'
import { AlertTriangle, RotateCcw } from 'lucide-react'
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
          <p className="flex items-center gap-1.5 text-xs text-academic-red mb-2">
            <AlertTriangle className="w-3.5 h-3.5 shrink-0" aria-hidden="true" />Erro na resposta
          </p>
        )}
        <div className="prose-jarvis max-w-[66ch] text-sm text-foreground">
          <ReactMarkdown remarkPlugins={[remarkGfm]}>{content}</ReactMarkdown>
        </div>
        {isStreaming && <span style={{ animation: 'blink 1s step-end infinite' }}>▌</span>}
        {isError && onRetry && (
          <button
            onClick={onRetry}
            className="mt-2 flex items-center gap-1.5 text-xs text-primary hover:underline transition-colors cursor-pointer"
          >
            <RotateCcw className="w-3.5 h-3.5 shrink-0" aria-hidden="true" />Tentar novamente
          </button>
        )}
      </GlassCard>
      <span className="text-xs font-mono text-muted-foreground">{format(timestamp, 'HH:mm')}</span>
    </div>
  )
}
