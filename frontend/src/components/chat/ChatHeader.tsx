import type { ChatStatus } from '@/types/chat'
import { Loader2, AlertTriangle, Sparkles } from 'lucide-react'

interface ChatHeaderProps {
  title: string
  status: ChatStatus
}

function StatusBadge({ status }: { status: ChatStatus }) {
  if (status === 'idle') return null
  if (status === 'error') {
    return (
      <span className="flex items-center gap-1 text-xs text-academic-red">
        <AlertTriangle className="w-3 h-3" aria-hidden="true" />Erro
      </span>
    )
  }
  if (status === 'loading') {
    return (
      <span className="flex items-center gap-1 text-xs text-muted-foreground">
        <Loader2 className="w-3 h-3 animate-spin" aria-hidden="true" />Processando...
      </span>
    )
  }
  return (
    <span className="flex items-center gap-1 text-xs text-muted-foreground">
      <Sparkles className="w-3 h-3" aria-hidden="true" />Gerando…
    </span>
  )
}

export default function ChatHeader({ title, status }: ChatHeaderProps) {
  const isActive = status === 'loading' || status === 'streaming'
  return (
    <div className={`shrink-0 flex items-center justify-between px-6 py-4 border-b border-border ${isActive ? 'chat-header-pulse' : ''}`}>
      <h2 className="text-sm font-semibold text-foreground truncate">{title}</h2>
      <StatusBadge status={status} />
    </div>
  )
}
