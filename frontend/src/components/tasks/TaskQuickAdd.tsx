'use client'
import { useState, type KeyboardEvent } from 'react'
import { Input } from '@/components/ui/input'
import GradientButton from '@/components/ui/GradientButton'
import { criarTarefa } from '@/lib/api'
import { toast } from '@/lib/toast'
import type { Tarefa } from '@/types/api'

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
    <div className="flex gap-2 items-center">
      <Input
        placeholder="Nova tarefa…"
        value={value}
        onChange={e => setValue(e.target.value)}
        onKeyDown={onKeyDown}
        disabled={loading}
        className="flex-1 h-8 text-xs bg-surface border-glass-border placeholder:text-muted-foreground"
      />
      <GradientButton
        onClick={() => void submit()}
        disabled={!value.trim() || loading}
        className="h-8 px-3 py-0 text-xs shrink-0"
      >
        {loading ? '…' : '+'}
      </GradientButton>
    </div>
  )
}
