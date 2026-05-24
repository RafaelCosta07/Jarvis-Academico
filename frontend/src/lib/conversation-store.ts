import type { Conversation } from '@/types/conversation'
import type { Message } from '@/types/chat'

export interface ConversationStore {
  getAll(): Conversation[]
  getById(id: string): Conversation | null
  create(conversation: Conversation): void
  update(id: string, data: Partial<Conversation>): void
  remove(id: string): void
}

function parseMessage(m: Record<string, unknown>): Message {
  return { ...(m as unknown as Message), timestamp: new Date(m.timestamp as string) }
}

function parseConversation(raw: Record<string, unknown>): Conversation {
  return {
    ...(raw as unknown as Conversation),
    createdAt: new Date(raw.createdAt as string),
    updatedAt: new Date(raw.updatedAt as string),
    messages: (raw.messages as Array<Record<string, unknown>>).map(parseMessage),
  }
}

const STORAGE_KEY = 'jarvis_conversations'

export class LocalStorageStore implements ConversationStore {
  private fallback: Conversation[] = []

  private read(): Conversation[] {
    try {
      const raw = localStorage.getItem(STORAGE_KEY)
      if (!raw) return []
      return (JSON.parse(raw) as Array<Record<string, unknown>>).map(parseConversation)
    } catch {
      return this.fallback
    }
  }

  private write(conversations: Conversation[]): void {
    try {
      localStorage.setItem(STORAGE_KEY, JSON.stringify(conversations))
    } catch {
      this.fallback = conversations
    }
  }

  getAll(): Conversation[] {
    return this.read().sort((a, b) => b.updatedAt.getTime() - a.updatedAt.getTime())
  }

  getById(id: string): Conversation | null {
    return this.read().find(c => c.id === id) ?? null
  }

  create(conversation: Conversation): void {
    this.write([...this.read(), conversation])
  }

  update(id: string, data: Partial<Conversation>): void {
    this.write(this.read().map(c => c.id === id ? { ...c, ...data } : c))
  }

  remove(id: string): void {
    this.write(this.read().filter(c => c.id !== id))
  }
}

export function createConversationStore(): ConversationStore {
  return new LocalStorageStore()
}
