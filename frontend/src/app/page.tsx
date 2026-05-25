'use client'
import { useMemo, useEffect, useRef, useCallback } from 'react'
import AppShell from '@/components/layout/AppShell'
import LeftSidebar from '@/components/layout/LeftSidebar'
import RightSidebar from '@/components/layout/RightSidebar'
import ChatWindow from '@/components/chat/ChatWindow'
import { useChat } from '@/hooks/useChat'
import { useConversations } from '@/hooks/useConversations'
import { createConversationStore } from '@/lib/conversation-store'
import { toast } from '@/lib/toast'

export default function Home() {
  const store = useMemo(() => createConversationStore(), [])
  const { conversations, activeId, createConversation, selectConversation, deleteConversation, updateConversation } = useConversations(store)

  const activeIdRef = useRef(activeId)
  activeIdRef.current = activeId

  const isSystemActiveIdChange = useRef(false)

  const handleCreate = useCallback(() => {
    isSystemActiveIdChange.current = true
    createConversation()
  }, [createConversation])

  type WinWithRefresh = Window & { recarregarTarefas?: () => void; recarregarAgenda?: () => void }

  const { messages, status, sendMessage, clearMessages, loadMessages, retry } = useChat({
    onCreate: handleCreate,
    activeId,
    onComplete: (msgs) => {
      const id = activeIdRef.current
      if (id) updateConversation(id, msgs)
      const win = window as WinWithRefresh
      win.recarregarTarefas?.()
      win.recarregarAgenda?.()
    },
  })

  useEffect(() => {
    if (isSystemActiveIdChange.current) {
      isSystemActiveIdChange.current = false
      return
    }
    const conv = activeId ? store.getById(activeId) : null
    loadMessages(conv?.messages ?? [])
  }, [activeId, store, loadMessages])

  function handleDelete(id: string) {
    deleteConversation(id)
    toast('Conversa removida', 'info')
  }

  const activeTitle = conversations.find(c => c.id === activeId)?.title ?? 'Nova conversa'

  return (
    <AppShell>
      <LeftSidebar
        conversations={conversations}
        activeId={activeId}
        onNew={clearMessages}
        onSelect={selectConversation}
        onDelete={handleDelete}
      />
      <ChatWindow
        messages={messages}
        status={status}
        title={activeTitle}
        onSend={sendMessage}
        onRetry={retry}
      />
      <RightSidebar />
    </AppShell>
  )
}
