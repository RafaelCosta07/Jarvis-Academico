import GlassCard from '@/components/ui/GlassCard'

interface ChatEmptyProps {
  onSuggestionClick: (text: string) => void
}

const SUGGESTIONS = [
  { icon: '📚', text: 'Explicar um conceito' },
  { icon: '📅', text: 'O que tenho hoje?' },
  { icon: '✅', text: 'Ver tarefas' },
]

export default function ChatEmpty({ onSuggestionClick }: ChatEmptyProps) {
  return (
    <div className="flex flex-col items-center justify-center flex-1 gap-8 p-8">
      <div className="text-center space-y-2">
        <h1 className="text-3xl font-bold bg-gradient-to-r from-[var(--color-primary-start)] to-[var(--color-primary-end)] bg-clip-text text-transparent">
          JARVIS
        </h1>
        <p className="text-sm text-muted-foreground">Seu assistente acadêmico está pronto para ajudar.</p>
      </div>
      <div className="flex gap-3">
        {SUGGESTIONS.map(({ icon, text }) => (
          <button
            key={text}
            onClick={() => onSuggestionClick(text)}
            className="transition-all duration-200 hover:-translate-y-1 hover:shadow-neural text-left"
          >
            <GlassCard className="w-36 text-center cursor-pointer">
              <span className="block text-2xl mb-2">{icon}</span>
              <span className="text-xs text-foreground">{text}</span>
            </GlassCard>
          </button>
        ))}
      </div>
    </div>
  )
}
