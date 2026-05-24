'use client'
import { useState, useEffect } from 'react'
import { getAgendaHoje } from '@/lib/api'
import type { Evento } from '@/types/api'
import AgendaEventItem from './AgendaEventItem'
import AgendaMiniCal from './AgendaMiniCal'

export default function AgendaWidget() {
  const [eventos, setEventos] = useState<Evento[]>([])
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState<string | null>(null)

  useEffect(() => {
    getAgendaHoje()
      .then(setEventos)
      .catch((err: unknown) => {
        console.error('AgendaWidget:', err)
        setError('Erro ao carregar agenda.')
      })
      .finally(() => setLoading(false))
  }, [])

  return (
    <section className="flex flex-col gap-3">
      <h2 className="text-xs font-semibold uppercase tracking-widest text-muted-foreground px-1">Agenda</h2>
      <AgendaMiniCal eventos={eventos} />
      <div className="flex flex-col gap-2 mt-1">
        {loading && <p className="text-xs text-muted-foreground px-1">Carregando…</p>}
        {error && <p className="text-xs text-academic-red px-1">{error}</p>}
        {!loading && !error && eventos.length === 0 && (
          <p className="text-xs text-muted-foreground px-1">Nenhum evento hoje.</p>
        )}
        {eventos.map(e => <AgendaEventItem key={e.id} evento={e} />)}
      </div>
    </section>
  )
}
