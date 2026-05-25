'use client'
import { useState, useCallback, useEffect } from 'react'
import type { ConversationStore } from '@/lib/conversation-store'
import type { Conversation } from '@/types/conversation'
import type { Message } from '@/types/chat'
import { generateId } from '@/lib/utils'

function titleFromMessages(messages: Message[]): string {
  const first = messages.find(m => m.role === 'user')
  if (!first) return 'Nova conversa'
  return first.content.slice(0, 40) + (first.content.length > 40 ? '…' : '')
}

export function useConversations(store: ConversationStore) {
  const [conversations, setConversations] = useState<Conversation[]>([])
  const [activeId, setActiveId] = useState<string | null>(null)

  useEffect(() => {
    setConversations(store.getAll())
  }, [store])

  const refresh = useCallback(() => setConversations(store.getAll()), [store])

  const createConversation = useCallback((): string => {
    const conv: Conversation = {
      id: generateId(), title: 'Nova conversa', messages: [],
      createdAt: new Date(), updatedAt: new Date(),
    }
    store.create(conv)
    refresh()
    setActiveId(conv.id)
    return conv.id
  }, [store, refresh])

  const selectConversation = useCallback((id: string) => setActiveId(id), [])

  const deleteConversation = useCallback((id: string) => {
    store.remove(id)
    refresh()
    setActiveId(prev => prev === id ? null : prev)
  }, [store, refresh])

  const updateConversation = useCallback((id: string, messages: Message[]) => {
    store.update(id, { messages, title: titleFromMessages(messages), updatedAt: new Date() })
    refresh()
  }, [store, refresh])

  const activeConversation = conversations.find(c => c.id === activeId) ?? null

  return {
    conversations, activeId, activeConversation,
    createConversation, selectConversation, deleteConversation, updateConversation,
  }
}
