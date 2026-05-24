'use client'
import { useState, type KeyboardEvent } from 'react'
import { Input } from '@/components/ui/input'
import { criarTarefa } from '@/lib/api'
import { toast } from '@/lib/toast'
import type { Tarefa } from '@/types/api'
import { Plus } from 'lucide-react'

interface TaskQuickAddProps {
  onAdded: (tarefa: Tarefa) => void
}

export default function TaskQuickAdd({ onAdded }: TaskQuickAddProps) {
  const [value, setValue] = useState('')
  const [loading, setLoading] = useState(false)

  async function submit() {
    const titulo = value.trim()
    if (!titulo || loading) return
    setLoading(true)
    try {
      const nova = await criarTarefa(titulo)
      onAdded(nova)
      setValue('')
      toast('Tarefa adicionada', 'success')
    } catch (err) {
      console.error('TaskQuickAdd:', err)
      toast('Erro ao criar tarefa', 'error')
    } finally {
      setLoading(false)
    }
  }

  function onKeyDown(e: KeyboardEvent<HTMLInputElement>) {
    if (e.key === 'Enter') void submit()
  }

  return (
    <div className="relative flex items-center">
      <Plus className="absolute left-2 w-3.5 h-3.5 text-muted-foreground pointer-events-none" />
      <Input
        placeholder="Nova tarefa…"
        value={value}
        onChange={e => setValue(e.target.value)}
        onKeyDown={onKeyDown}
        disabled={loading}
        className="pl-7 h-8 text-xs bg-surface border-glass-border placeholder:text-muted-foreground"
      />
    </div>
  )
}
