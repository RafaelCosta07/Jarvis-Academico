'use client'
import { useMemo } from 'react'
import { getDaysInMonth, getDay, startOfMonth } from 'date-fns'
import type { Evento } from '@/types/api'

const WEEK_DAYS = ['D', 'S', 'T', 'Q', 'Q', 'S', 'S']
const MESES_PT = ['Janeiro','Fevereiro','Março','Abril','Maio','Junho',
  'Julho','Agosto','Setembro','Outubro','Novembro','Dezembro']

interface AgendaMiniCalProps {
  ano: number
  mes: number
  eventos: Evento[]
  dataSelecionada: string
  onDayClick: (data: string) => void
  onMesAnterior: () => void
  onMesProximo: () => void
  podeMesAnterior: boolean
}

interface DiaCalendarioProps {
  dia: number
  dataStr: string
  isHoje: boolean
  isSelecionado: boolean
  temEvento: boolean
  isPast: boolean
  onClick: (data: string) => void
}

function DiaCalendario({ dia, dataStr, isHoje, isSelecionado, temEvento, isPast, onClick }: DiaCalendarioProps) {
  return (
    <button
      onClick={() => !isPast && onClick(dataStr)}
      disabled={isPast}
      className={[
        'w-7 h-7 text-[11px] rounded-full flex items-center justify-center mx-auto',
        'transition-all duration-150 relative',
        isPast ? 'opacity-30 cursor-not-allowed' : 'cursor-pointer hover:bg-surface',
        isHoje && !isSelecionado ? 'ring-1 ring-[var(--color-primary-start)]' : '',
        isSelecionado
          ? 'bg-gradient-to-br from-[var(--color-primary-start)] to-[var(--color-primary-end)] text-white font-semibold'
          : 'text-foreground',
      ].join(' ')}
    >
      {dia}
      {temEvento && !isSelecionado && (
        <span className="absolute bottom-0.5 left-1/2 -translate-x-1/2 w-1 h-1 rounded-full bg-[var(--color-primary-start)]" />
      )}
    </button>
  )
}

function buildDataStr(ano: number, mes: number, dia: number): string {
  return `${ano}-${String(mes + 1).padStart(2, '0')}-${String(dia).padStart(2, '0')}`
}

interface CelulasProps {
  cells: (number | null)[]
  ano: number
  mes: number
  hojeStr: string
  dataSelecionada: string
  datesWithEvents: Set<string>
  onDayClick: (data: string) => void
}

function CelulasCalendario({ cells, ano, mes, hojeStr, dataSelecionada, datesWithEvents, onDayClick }: CelulasProps) {
  return (
    <>
      {cells.map((dia, i) => {
        if (!dia) return <span key={i} />
        const dataStr = buildDataStr(ano, mes, dia)
        return (
          <DiaCalendario
            key={i} dia={dia} dataStr={dataStr}
            isHoje={dataStr === hojeStr} isSelecionado={dataStr === dataSelecionada}
            temEvento={datesWithEvents.has(dataStr)} isPast={dataStr < hojeStr}
            onClick={onDayClick}
          />
        )
      })}
    </>
  )
}

export default function AgendaMiniCal({ ano, mes, eventos, dataSelecionada, onDayClick, onMesAnterior, onMesProximo, podeMesAnterior }: AgendaMiniCalProps) {
  const refData = new Date(ano, mes, 1)
  const daysInMonth = getDaysInMonth(refData)
  const firstDay = getDay(startOfMonth(refData))
  const hojeStr = new Date().toISOString().split('T')[0]
  const datesWithEvents = useMemo(() => new Set(eventos.map(e => e.data)), [eventos])
  const cells: (number | null)[] = [
    ...Array<null>(firstDay).fill(null),
    ...Array.from({ length: daysInMonth }, (_, i) => i + 1),
  ]

  return (
    <div className="px-1">
      <div className="flex items-center justify-between mb-2">
        <button onClick={onMesAnterior} disabled={!podeMesAnterior} aria-label="Mês anterior" className="text-muted-foreground hover:text-foreground disabled:opacity-30 disabled:cursor-not-allowed transition-colors px-1 text-base">‹</button>
        <span className="text-xs text-muted-foreground capitalize">{MESES_PT[mes]} {ano}</span>
        <button onClick={onMesProximo} aria-label="Próximo mês" className="text-muted-foreground hover:text-foreground transition-colors px-1 text-base">›</button>
      </div>
      <div className="grid grid-cols-7 gap-0.5 text-center">
        {WEEK_DAYS.map((d, i) => <span key={i} className="text-[10px] text-muted-foreground font-medium pb-1">{d}</span>)}
        <CelulasCalendario cells={cells} ano={ano} mes={mes} hojeStr={hojeStr} dataSelecionada={dataSelecionada} datesWithEvents={datesWithEvents} onDayClick={onDayClick} />
      </div>
    </div>
  )
}
