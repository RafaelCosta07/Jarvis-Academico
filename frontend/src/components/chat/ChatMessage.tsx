import type { Message } from '@/types/chat'
import ChatMessageUser from './ChatMessageUser'
import ChatMessageAssistant from './ChatMessageAssistant'

interface ChatMessageProps {
  message: Message
  isStreaming?: boolean
  isError?: boolean
  onRetry?: () => void
}

export default function ChatMessage({ message, isStreaming, isError, onRetry }: ChatMessageProps) {
  if (message.role === 'user') {
    return <ChatMessageUser content={message.content} timestamp={message.timestamp} />
  }
  return (
    <ChatMessageAssistant
      content={message.content}
      timestamp={message.timestamp}
      isStreaming={isStreaming}
      isError={isError}
      onRetry={onRetry}
    />
  )
}
