import type { Tarefa } from '@/types/api'
import TaskItem from './TaskItem'
import { parseISO } from 'date-fns'

interface TaskListProps {
  tarefas: Tarefa[]
  onConcluida: (id: string) => void
  onRevert: (id: string) => void
}

function sortTarefas(tarefas: Tarefa[]): Tarefa[] {
  return [...tarefas].sort((a, b) => {
    if (a.status !== b.status) return a.status === 'pendente' ? -1 : 1
    if (!a.prazo && !b.prazo) return 0
    if (!a.prazo) return 1
    if (!b.prazo) return -1
    return parseISO(a.prazo).getTime() - parseISO(b.prazo).getTime()
  })
}

export default function TaskList({ tarefas, onConcluida, onRevert }: TaskListProps) {
  const sorted = sortTarefas(tarefas)
  return (
    <div className="flex flex-col divide-y divide-border">
      {sorted.map(t => (
        <TaskItem key={t.id} tarefa={t} onConcluida={onConcluida} onRevert={onRevert} />
      ))}
    </div>
  )
}
