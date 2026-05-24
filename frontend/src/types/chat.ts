export type MessageRole = 'user' | 'assistant'
export type ChatStatus = 'idle' | 'loading' | 'streaming' | 'error'

export interface Message {
  id: string
  role: MessageRole
  content: string
  timestamp: Date
}
