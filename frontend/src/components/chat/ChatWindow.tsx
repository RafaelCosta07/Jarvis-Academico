import type { Message, ChatStatus } from '@/types/chat'
import ChatHeader from './ChatHeader'
import ChatMessageList from './ChatMessageList'
import ChatInput from './ChatInput'
import ChatEmpty from './ChatEmpty'

interface ChatWindowProps {
  messages: Message[]
  status: ChatStatus
  title: string
  onSend: (content: string) => void
  onRetry?: () => void
}

export default function ChatWindow({ messages, status, title, onSend, onRetry }: ChatWindowProps) {
  const isEmpty = messages.length === 0 && status === 'idle'
  return (
    <div className="flex flex-col h-full bg-background overflow-hidden">
      <ChatHeader title={title} status={status} />
      {isEmpty
        ? <ChatEmpty onSuggestionClick={onSend} />
        : <ChatMessageList messages={messages} status={status} onRetry={onRetry} />
      }
      <ChatInput onSend={onSend} disabled={status === 'loading' || status === 'streaming'} />
    </div>
  )
}
