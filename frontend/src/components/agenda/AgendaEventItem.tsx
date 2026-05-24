import type { Evento } from '@/types/api'
import GradientBadge from '@/components/ui/GradientBadge'

const BORDER_COLOR: Record<Evento['tipo'], string> = {
  aula:  'border-l-academic-blue',
  prova: 'border-l-academic-red',
  prazo: 'border-l-academic-yellow',
  outro: 'border-l-muted-foreground',
}

function formatHora(hora: string | null): string {
  if (!hora) return ''
  return hora.slice(0, 5)
}

interface AgendaEventItemProps {
  evento: Evento
}

export default function AgendaEventItem({ evento }: AgendaEventItemProps) {
  const hora = formatHora(evento.hora_inicio)
  const horaFim = formatHora(evento.hora_fim)
  return (
    <div className={`border-l-2 pl-3 py-1 rounded-sm transition-all duration-200 cursor-default hover:-translate-y-1 hover:shadow-[var(--shadow-neural)] ${BORDER_COLOR[evento.tipo]}`}>
      <div className="flex items-center justify-between gap-2">
        <span className="text-sm text-foreground font-medium truncate">{evento.titulo}</span>
        <GradientBadge variant={evento.tipo} />
      </div>
      {(hora || evento.local) && (
        <p className="text-xs text-muted-foreground mt-0.5">
          {hora}{horaFim ? `–${horaFim}` : ''}{hora && evento.local ? ' · ' : ''}{evento.local ?? ''}
        </p>
      )}
    </div>
  )
}
