'use client'
import { useState, useEffect, useCallback } from 'react'
import { getTarefas } from '@/lib/api'
import type { Tarefa } from '@/types/api'
import TaskList from './TaskList'
import TaskQuickAdd from './TaskQuickAdd'

export default function TaskWidget() {
  const [tarefas, setTarefas] = useState<Tarefa[]>([])
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState<string | null>(null)

  useEffect(() => {
    getTarefas()
      .then(setTarefas)
      .catch((err: unknown) => {
        console.error('TaskWidget:', err)
        setError('Erro ao carregar tarefas.')
      })
      .finally(() => setLoading(false))
  }, [])

  const handleConcluida = useCallback((id: string) => {
    setTarefas(prev => prev.map(t => t.id === id ? { ...t, status: 'concluida' as const } : t))
  }, [])

  const handleRevert = useCallback((id: string) => {
    setTarefas(prev => prev.map(t => t.id === id ? { ...t, status: 'pendente' as const } : t))
  }, [])

  const handleAdded = useCallback((nova: Tarefa) => {
    setTarefas(prev => [nova, ...prev])
  }, [])

  const pendentes = tarefas.filter(t => t.status === 'pendente').length

  return (
    <section className="flex flex-col gap-3">
      <div className="flex items-center justify-between px-1">
        <h2 className="text-xs font-semibold uppercase tracking-widest text-muted-foreground">Tarefas</h2>
        {pendentes > 0 && (
          <span className="text-xs text-academic-yellow font-medium">{pendentes} pendente{pendentes > 1 ? 's' : ''}</span>
        )}
      </div>
      <TaskQuickAdd onAdded={handleAdded} />
      {loading && <p className="text-xs text-muted-foreground px-1">Carregando…</p>}
      {error && <p className="text-xs text-academic-red px-1">{error}</p>}
      {!loading && !error && tarefas.length === 0 && (
        <p className="text-xs text-muted-foreground px-1">Nenhuma tarefa cadastrada.</p>
      )}
      {!loading && <TaskList tarefas={tarefas} onConcluida={handleConcluida} onRevert={handleRevert} />}
    </section>
  )
}
