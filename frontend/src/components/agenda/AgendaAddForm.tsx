'use client'
import { useState } from 'react'
import GradientButton from '@/components/ui/GradientButton'
import { criarEvento } from '@/lib/api'
import { toast } from '@/lib/toast'
import type { Evento } from '@/types/api'

type TipoEvento = Evento['tipo']

interface AgendaAddFormProps {
  onSaved: (evento: Evento) => void
  onCancel: () => void
  dataSelecionada?: string
}

export default function AgendaAddForm({ onSaved, onCancel, dataSelecionada }: AgendaAddFormProps) {
  const [titulo, setTitulo] = useState('')
  const [horaInicio, setHoraInicio] = useState('')
  const [tipo, setTipo] = useState<TipoEvento>('outro')
  const [loading, setLoading] = useState(false)

  async function handleSalvar() {
    if (!titulo.trim() || loading) return
    setLoading(true)
    try {
      const data = dataSelecionada ?? new Date().toISOString().split('T')[0]
      const novo = await criarEvento({
        titulo: titulo.trim(), data, tipo,
        hora_inicio: horaInicio || null, hora_fim: null, descricao: null, local: null,
      })
      onSaved(novo)
    } catch (err) {
      console.error('AgendaAddForm:', err)
      toast('Erro ao criar evento', 'error')
    } finally {
      setLoading(false)
    }
  }

  return (
    <div className="flex flex-col gap-1.5 p-2 rounded-lg border border-[var(--glass-border)] bg-[var(--glass-bg)]">
      <input
        placeholder="Nome do evento…"
        value={titulo}
        onChange={e => setTitulo(e.target.value)}
        onKeyDown={e => e.key === 'Enter' && void handleSalvar()}
        autoFocus
        className="bg-transparent text-sm outline-none text-foreground placeholder:text-muted-foreground"
      />
      <div className="flex gap-2 items-center">
        <input
          type="time"
          value={horaInicio}
          onChange={e => setHoraInicio(e.target.value)}
          className="bg-transparent text-xs text-muted-foreground outline-none"
        />
        <select
          value={tipo}
          onChange={e => setTipo(e.target.value as TipoEvento)}
          className="bg-transparent text-xs text-muted-foreground outline-none ml-auto"
        >
          <option value="aula">Aula</option>
          <option value="prova">Prova</option>
          <option value="prazo">Prazo</option>
          <option value="outro">Outro</option>
        </select>
      </div>
      <div className="flex gap-1 justify-end">
        <button onClick={onCancel} className="text-xs text-muted-foreground px-2 py-1 hover:text-foreground">Cancelar</button>
        <GradientButton onClick={() => void handleSalvar()} disabled={!titulo.trim() || loading} className="text-xs px-2 py-1">
          {loading ? '…' : 'Salvar'}
        </GradientButton>
      </div>
    </div>
  )
}
