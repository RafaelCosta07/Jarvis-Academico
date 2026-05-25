'use client'
import { useState, useEffect, useCallback, useMemo } from 'react'
import { format } from 'date-fns'
import { ptBR } from 'date-fns/locale'
import { getTodosEventos } from '@/lib/api'
import type { Evento } from '@/types/api'
import AgendaEventItem from './AgendaEventItem'
import AgendaMiniCal from './AgendaMiniCal'
import AgendaAddForm from './AgendaAddForm'

type Win = Window & { recarregarAgenda?: () => void }

interface ListaProps {
  loading: boolean
  error: string | null
  eventos: Evento[]
  labelData: string
}

function AgendaEventosLista({ loading, error, eventos, labelData }: ListaProps) {
  return (
    <div className="flex flex-col gap-2 mt-1">
      {loading && <p className="text-xs text-muted-foreground px-1">Carregando…</p>}
      {error && <p className="text-xs text-academic-red px-1">{error}</p>}
      {!loading && !error && <p className="text-xs font-semibold text-foreground px-1 mb-1 capitalize">{labelData}</p>}
      {!loading && !error && eventos.length === 0 && <p className="text-xs text-muted-foreground px-1">Nenhum evento.</p>}
      {eventos.map(e => <AgendaEventItem key={e.id} evento={e} />)}
    </div>
  )
}

export default function AgendaWidget() {
  const hojeStr = useMemo(() => new Date().toISOString().split('T')[0], [])
  const hoje = useMemo(() => new Date(), [])
  const [dataSelecionada, setDataSelecionada] = useState(hojeStr)
  const [mesAtual, setMesAtual] = useState({ ano: hoje.getFullYear(), mes: hoje.getMonth() })
  const [todosEventos, setTodosEventos] = useState<Evento[]>([])
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState<string | null>(null)
  const [adicionando, setAdicionando] = useState(false)

  const carregarEventos = useCallback(() => {
    getTodosEventos()
      .then(data => { setTodosEventos(data); setError(null) })
      .catch((err: unknown) => { console.error('AgendaWidget:', err); setError('Erro ao carregar agenda.') })
      .finally(() => setLoading(false))
  }, [])

  useEffect(() => {
    carregarEventos()
    const id = setInterval(carregarEventos, 30_000)
    return () => clearInterval(id)
  }, [carregarEventos])

  useEffect(() => {
    (window as Win).recarregarAgenda = carregarEventos
    return () => { delete (window as Win).recarregarAgenda }
  }, [carregarEventos])

  const eventosDia = useMemo(
    () => todosEventos.filter(e => e.data === dataSelecionada),
    [todosEventos, dataSelecionada],
  )

  const podeMesAnterior = mesAtual.ano > hoje.getFullYear() ||
    (mesAtual.ano === hoje.getFullYear() && mesAtual.mes > hoje.getMonth())

  const irParaMesAnterior = () => {
    setMesAtual(prev => {
      const novaData = new Date(prev.ano, prev.mes - 1, 1)
      const inicioHoje = new Date(hoje.getFullYear(), hoje.getMonth(), 1)
      return novaData < inicioHoje ? prev : { ano: novaData.getFullYear(), mes: novaData.getMonth() }
    })
  }

  const irParaMesProximo = () => {
    setMesAtual(prev => {
      const novaData = new Date(prev.ano, prev.mes + 1, 1)
      return { ano: novaData.getFullYear(), mes: novaData.getMonth() }
    })
  }

  const handleDayClick = (data: string) => { setDataSelecionada(data); setAdicionando(false) }
  const handleSaved = (novo: Evento) => { setTodosEventos(prev => [...prev, novo]); setAdicionando(false) }

  const [ano, mes, dia] = dataSelecionada.split('-').map(Number)
  const dataLocal = new Date(ano, mes - 1, dia)
  const labelData = dataSelecionada === hojeStr
    ? `Hoje, ${format(dataLocal, 'dd/MM', { locale: ptBR })}`
    : format(dataLocal, "EEEE, dd 'de' MMMM", { locale: ptBR })

  return (
    <section className="flex flex-col gap-3">
      <h2 className="text-xs font-semibold uppercase tracking-widest text-muted-foreground px-1">Agenda</h2>
      <AgendaMiniCal
        ano={mesAtual.ano} mes={mesAtual.mes} eventos={todosEventos}
        dataSelecionada={dataSelecionada} onDayClick={handleDayClick}
        onMesAnterior={irParaMesAnterior} onMesProximo={irParaMesProximo}
        podeMesAnterior={podeMesAnterior}
      />
      <AgendaEventosLista loading={loading} error={error} eventos={eventosDia} labelData={labelData} />
      {adicionando
        ? <AgendaAddForm dataSelecionada={dataSelecionada} onSaved={handleSaved} onCancel={() => setAdicionando(false)} />
        : <button onClick={() => setAdicionando(true)} className="text-xs text-muted-foreground hover:text-foreground flex items-center gap-1 mt-1 px-1">+ Adicionar evento</button>
      }
    </section>
  )
}
