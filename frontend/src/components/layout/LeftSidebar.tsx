'use client'
import { isToday, isYesterday, formatDistanceToNow } from 'date-fns'
import { ptBR } from 'date-fns/locale'
import { X } from 'lucide-react'
import { ScrollArea } from '@/components/ui/scroll-area'
import { Separator } from '@/components/ui/separator'
import { Avatar, AvatarFallback } from '@/components/ui/avatar'
import GradientButton from '@/components/ui/GradientButton'
import type { Conversation } from '@/types/conversation'

const MATERIALS = [
  'introducao-ia.pdf',
  'redes-neurais.pdf',
  'processamento-linguagem.pdf',
]

function formatDate(date: Date): string {
  if (isToday(date)) return 'Hoje'
  if (isYesterday(date)) return 'Ontem'
  return formatDistanceToNow(date, { locale: ptBR, addSuffix: true })
}

interface ConversationItemProps {
  conversation: Conversation
  isActive: boolean
  onSelect: (id: string) => void
  onDelete: (id: string) => void
}

function ConversationItem({ conversation, isActive, onSelect, onDelete }: ConversationItemProps) {
  return (
    <div className={`relative flex items-center group rounded-md transition-colors ${isActive ? 'bg-glass-bg' : 'hover:bg-surface/80'}`}>
      {isActive && (
        <div className="absolute left-0 top-1 bottom-1 w-0.5 rounded-full bg-gradient-to-b from-[var(--color-primary-start)] to-[var(--color-primary-end)]" />
      )}
      <button onClick={() => onSelect(conversation.id)} className="flex-1 text-left px-3 py-2 pl-3 min-w-0">
        <p className="text-sm truncate text-foreground">{conversation.title}</p>
        <p className="text-xs text-muted-foreground">{formatDate(conversation.updatedAt)}</p>
      </button>
      <button
        onClick={e => { e.stopPropagation(); onDelete(conversation.id) }}
        className="mr-1.5 p-1 rounded opacity-0 group-hover:opacity-60 hover:!opacity-100 hover:text-academic-red transition-opacity"
      >
        <X className="w-3 h-3" />
      </button>
    </div>
  )
}

export interface LeftSidebarProps {
  conversations: Conversation[]
  activeId: string | null
  onNew: () => void
  onSelect: (id: string) => void
  onDelete: (id: string) => void
}

export default function LeftSidebar({ conversations, activeId, onNew, onSelect, onDelete }: LeftSidebarProps) {
  return (
    <aside className="h-full bg-surface border-r border-border flex flex-col">
      <div className="p-4 border-b border-border flex flex-col gap-3 shrink-0">
        <div>
          <span className="text-xl font-bold bg-gradient-to-r from-[var(--color-primary-start)] to-[var(--color-primary-end)] bg-clip-text text-transparent">JARVIS</span>
          <span className="text-xs text-muted-foreground ml-2">Academic</span>
        </div>
        <GradientButton onClick={onNew} className="w-full text-sm py-1.5">+ Nova Conversa</GradientButton>
      </div>
      <ScrollArea className="flex-1">
        <div className="px-2 py-2">
          <p className="text-[10px] uppercase tracking-widest text-muted-foreground px-2 pb-1">Conversas</p>
          {conversations.length === 0 && (
            <p className="text-xs text-muted-foreground px-2 py-1">Nenhuma conversa ainda.</p>
          )}
          {conversations.map(c => (
            <ConversationItem key={c.id} conversation={c} isActive={c.id === activeId} onSelect={onSelect} onDelete={onDelete} />
          ))}
        </div>
        <Separator className="mx-2" />
        <div className="px-2 py-2">
          <p className="text-[10px] uppercase tracking-widest text-muted-foreground px-2 pb-1">Materiais</p>
          {MATERIALS.map(name => (
            <div key={name} className="flex items-center gap-2 px-2 py-1.5 text-xs text-muted-foreground">
              <span>📄</span>
              <span className="truncate">{name}</span>
            </div>
          ))}
        </div>
      </ScrollArea>
      <Separator />
      <div className="p-3 flex items-center gap-2 shrink-0">
        <Avatar className="w-6 h-6"><AvatarFallback className="text-[10px]">E</AvatarFallback></Avatar>
        <span className="text-xs text-muted-foreground">Estudante</span>
      </div>
    </aside>
  )
}
