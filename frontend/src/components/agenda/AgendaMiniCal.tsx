import { useMemo } from 'react'
import { format, startOfMonth, getDay, getDaysInMonth, isToday } from 'date-fns'
import { ptBR } from 'date-fns/locale'
import type { Evento } from '@/types/api'

const WEEK_DAYS = ['D', 'S', 'T', 'Q', 'Q', 'S', 'S']

interface AgendaMiniCalProps {
  eventos: Evento[]
}

export default function AgendaMiniCal({ eventos }: AgendaMiniCalProps) {
  const now = new Date()
  const daysInMonth = getDaysInMonth(now)
  const firstDay = getDay(startOfMonth(now))
  const datesWithEvents = useMemo(() => new Set(eventos.map(e => e.data)), [eventos])
  const mesLabel = format(now, 'MMMM yyyy', { locale: ptBR })

  const cells: (number | null)[] = [
    ...Array<null>(firstDay).fill(null),
    ...Array.from({ length: daysInMonth }, (_, i) => i + 1),
  ]

  return (
    <div className="px-1">
      <p className="text-xs text-muted-foreground capitalize mb-2">{mesLabel}</p>
      <div className="grid grid-cols-7 gap-0.5 text-center">
        {WEEK_DAYS.map((d, i) => (
          <span key={i} className="text-[10px] text-muted-foreground font-medium pb-1">{d}</span>
        ))}
        {cells.map((day, i) => {
          if (!day) return <span key={i} />
          const iso = `${format(now, 'yyyy-MM')}-${String(day).padStart(2, '0')}`
          const hasEvent = datesWithEvents.has(iso)
          const today = isToday(new Date(now.getFullYear(), now.getMonth(), day))
          return (
            <span key={i} className={`
              text-[11px] w-6 h-6 flex items-center justify-center rounded-full mx-auto
              ${today ? 'bg-primary-start text-white font-bold' : ''}
              ${hasEvent && !today ? 'text-academic-blue font-semibold' : ''}
              ${!today && !hasEvent ? 'text-muted-foreground' : ''}
            `}>
              {day}
            </span>
          )
        })}
      </div>
    </div>
  )
}
