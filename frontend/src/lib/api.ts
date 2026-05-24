import type { Evento, Tarefa } from '@/types/api'

const API_URL = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000'

export async function postChat(
  messages: Array<{ role: string; content: string }>,
  signal?: AbortSignal,
): Promise<Response> {
  return fetch(`${API_URL}/api/chat`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ messages, stream: true }),
    signal,
  })
}

export async function getAgendaHoje(): Promise<Evento[]> {
  const data = new Date().toISOString().split('T')[0]
  const res = await fetch(`${API_URL}/api/agenda?data=${data}`)
  if (!res.ok) throw new Error(`Erro ao buscar agenda: ${res.status}`)
  return res.json() as Promise<Evento[]>
}

export async function getTarefas(status?: 'pendente' | 'concluida'): Promise<Tarefa[]> {
  const url = status ? `${API_URL}/api/tasks?status=${status}` : `${API_URL}/api/tasks`
  const res = await fetch(url)
  if (!res.ok) throw new Error(`Erro ao buscar tarefas: ${res.status}`)
  return res.json() as Promise<Tarefa[]>
}

export async function concluirTarefa(id: string): Promise<Tarefa> {
  const res = await fetch(`${API_URL}/api/tasks/${id}/concluir`, { method: 'PATCH' })
  if (!res.ok) throw new Error(`Erro ao concluir tarefa: ${res.status}`)
  return res.json() as Promise<Tarefa>
}

export async function criarTarefa(
  titulo: string,
  disciplina?: string,
  prazo?: string,
): Promise<Tarefa> {
  const res = await fetch(`${API_URL}/api/tasks`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ titulo, disciplina: disciplina ?? null, prazo: prazo ?? null }),
  })
  if (!res.ok) throw new Error(`Erro ao criar tarefa: ${res.status}`)
  return res.json() as Promise<Tarefa>
}
