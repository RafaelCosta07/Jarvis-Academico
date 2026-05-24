'use client'
import { useState } from 'react'
import { Checkbox } from '@/components/ui/checkbox'
import ConfettiParticles from '@/components/ui/ConfettiParticles'
import { concluirTarefa } from '@/lib/api'
import { toast } from '@/lib/toast'
import type { Tarefa } from '@/types/api'
import { format, isPast, parseISO } from 'date-fns'
import { ptBR } from 'date-fns/locale'

interface TaskItemProps {
  tarefa: Tarefa
  onConcluida: (id: string) => void
  onRevert: (id: string) => void
}

export default function TaskItem({ tarefa, onConcluida, onRevert }: TaskItemProps) {
  const [loading, setLoading] = useState(false)
  const [celebrating, setCelebrating] = useState(false)
  const concluida = tarefa.status === 'concluida'
  const vencida = !concluida && tarefa.prazo && isPast(parseISO(tarefa.prazo))

  async function handleCheck() {
    if (concluida || loading) return
    setLoading(true)
    onConcluida(tarefa.id)
    setCelebrating(true)
    setTimeout(() => setCelebrating(false), 900)
    try {
      await concluirTarefa(tarefa.id)
      toast('Tarefa marcada como concluída', 'success')
    } catch (err) {
      console.error('TaskItem concluir:', err)
      onRevert(tarefa.id)
      toast('Erro ao concluir tarefa', 'error')
    } finally {
      setLoading(false)
    }
  }

  return (
    <div className="relative flex items-start gap-2 py-1.5 px-1 rounded-md transition-all duration-200 hover:-translate-y-1 hover:shadow-[var(--shadow-neural)]">
      <ConfettiParticles active={celebrating} />
      <Checkbox checked={concluida} disabled={loading} onCheckedChange={handleCheck} className="mt-0.5 shrink-0" />
      <div className="flex-1 min-w-0">
        <p className={`text-sm truncate ${concluida ? 'line-through text-muted-foreground' : 'text-foreground'}`}>
          {tarefa.titulo}
        </p>
        <p className="text-xs text-muted-foreground truncate">
          {tarefa.disciplina ?? ''}
          {tarefa.prazo && (
            <span className={vencida ? 'text-academic-red' : ''}>
              {tarefa.disciplina ? ' · ' : ''}
              {format(parseISO(tarefa.prazo), 'd MMM', { locale: ptBR })}
            </span>
          )}
        </p>
      </div>
    </div>
  )
}
