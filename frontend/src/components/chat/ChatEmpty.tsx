import GlassCard from '@/components/ui/GlassCard'
import { BookOpen, CalendarDays, CheckSquare, type LucideIcon } from 'lucide-react'

interface ChatEmptyProps {
  onSuggestionClick: (text: string) => void
}

const SUGGESTIONS: { icon: LucideIcon; text: string }[] = [
  { icon: BookOpen, text: 'Explicar um conceito' },
  { icon: CalendarDays, text: 'O que tenho hoje?' },
  { icon: CheckSquare, text: 'Ver tarefas' },
]

export default function ChatEmpty({ onSuggestionClick }: ChatEmptyProps) {
  return (
    <div className="flex flex-col items-center justify-center flex-1 gap-10 p-8">
      <div className="text-center space-y-3">
        <h1 className="font-display text-5xl font-medium tracking-tight bg-gradient-to-r from-[var(--color-primary-start)] to-[var(--color-primary-end)] bg-clip-text text-transparent">
          JARVIS
        </h1>
        <p className="text-sm text-muted-foreground">Seu assistente acadêmico está pronto para ajudar.</p>
      </div>
      <div className="flex gap-3">
        {SUGGESTIONS.map(({ icon: Icon, text }) => (
          <button
            key={text}
            onClick={() => onSuggestionClick(text)}
            className="group text-left transition-transform duration-200 hover:-translate-y-1"
          >
            <GlassCard className="w-40 cursor-pointer transition-colors group-hover:border-primary/40 group-hover:shadow-2">
              <Icon className="w-5 h-5 mb-3 text-primary" strokeWidth={1.75} aria-hidden="true" />
              <span className="text-sm text-foreground">{text}</span>
            </GlassCard>
          </button>
        ))}
      </div>
    </div>
  )
}
