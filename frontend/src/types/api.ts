export interface SSEToken { type: 'token'; content: string }
export interface SSEDone  { type: 'done' }
export interface SSEError { type: 'error'; content: string }
export type SSEEvent = SSEToken | SSEDone | SSEError

export interface Evento {
  id: string
  titulo: string
  descricao: string | null
  data: string
  hora_inicio: string | null
  hora_fim: string | null
  tipo: 'aula' | 'prova' | 'prazo' | 'outro'
  local: string | null
}

export interface Tarefa {
  id: string
  titulo: string
  descricao: string | null
  disciplina: string | null
  status: 'pendente' | 'concluida'
  prazo: string | null
  criada_em: string
  concluida_em: string | null
}
