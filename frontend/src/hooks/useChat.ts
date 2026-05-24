'use client'
import { useState, useCallback, useRef, useEffect } from 'react'
import type { Message, ChatStatus } from '@/types/chat'
import { connectSSE } from './useSSE'
import { generateId } from '@/lib/utils'

const TYPEWRITER_SPEED = 15
const CHARS_PER_TICK = 2

export interface UseChatOptions {
  onCreate?: () => void
  onComplete?: (messages: Message[]) => void
  activeId?: string | null
}

export function useChat(options: UseChatOptions = {}) {
  const [messages, setMessages] = useState<Message[]>([])
  const [status, setStatus] = useState<ChatStatus>('idle')
  const abortRef = useRef<(() => void) | null>(null)
  const intervalRef = useRef<ReturnType<typeof setInterval> | null>(null)
  const optionsRef = useRef(options)
  optionsRef.current = options
  const messagesRef = useRef<Message[]>([])

  const updateLastContent = useCallback((partial: string) => {
    setMessages(prev => {
      const updated = [...prev]
      updated[updated.length - 1] = { ...updated[updated.length - 1], content: partial }
      messagesRef.current = updated
      return updated
    })
  }, [])

  const stopTypewriter = useCallback(() => {
    if (intervalRef.current) { clearInterval(intervalRef.current); intervalRef.current = null }
  }, [])

  const runTypewriter = useCallback((full: string, onComplete: () => void) => {
    stopTypewriter()
    if (full.length < 50) { updateLastContent(full); onComplete(); return }
    let pos = 0
    intervalRef.current = setInterval(() => {
      pos += CHARS_PER_TICK
      if (pos >= full.length) {
        stopTypewriter(); updateLastContent(full); onComplete()
      } else {
        updateLastContent(full.slice(0, pos))
      }
    }, TYPEWRITER_SPEED)
  }, [stopTypewriter, updateLastContent])

  const makeCallbacks = useCallback(() => ({
    onToken: (content: string) => {
      setStatus('streaming')
      runTypewriter(content, () => {
        optionsRef.current.onComplete?.(messagesRef.current)
        setStatus('idle')
      })
    },
    onDone: () => setStatus(prev => prev === 'loading' ? 'idle' : prev),
    onError: (msg: string) => { stopTypewriter(); updateLastContent(msg); setStatus('error') },
  }), [runTypewriter, stopTypewriter, updateLastContent])

  const sendMessage = useCallback((content: string) => {
    if (abortRef.current) abortRef.current()
    stopTypewriter()
    if (!optionsRef.current.activeId) optionsRef.current.onCreate?.()
    const userMsg: Message = { id: generateId(), role: 'user', content, timestamp: new Date() }
    const botMsg: Message = { id: generateId(), role: 'assistant', content: '', timestamp: new Date() }
    setMessages(prev => [...prev, userMsg, botMsg])
    messagesRef.current = [...messages, userMsg, botMsg]
    setStatus('loading')
    const apiMsgs = [...messages, userMsg].map(m => ({ role: m.role, content: m.content }))
    abortRef.current = connectSSE(apiMsgs, makeCallbacks())
  }, [messages, stopTypewriter, makeCallbacks])

  const loadMessages = useCallback((msgs: Message[]) => {
    if (abortRef.current) abortRef.current()
    stopTypewriter()
    setMessages(msgs)
    messagesRef.current = msgs
    setStatus('idle')
  }, [stopTypewriter])

  const clearMessages = useCallback(() => {
    if (abortRef.current) abortRef.current()
    stopTypewriter()
    setMessages([])
    messagesRef.current = []
    setStatus('idle')
    optionsRef.current.onCreate?.()
  }, [stopTypewriter])

  const retry = useCallback(() => {
    const msgs = messagesRef.current
    const lastUserIdx = msgs.reduce((acc, m, i) => m.role === 'user' ? i : acc, -1)
    if (lastUserIdx === -1) return
    if (abortRef.current) abortRef.current()
    stopTypewriter()
    const prevMsgs = msgs.slice(0, lastUserIdx + 1)
    const botMsg: Message = { id: generateId(), role: 'assistant', content: '', timestamp: new Date() }
    const newMsgs = [...prevMsgs, botMsg]
    setMessages(newMsgs)
    messagesRef.current = newMsgs
    setStatus('loading')
    const apiMsgs = prevMsgs.map(m => ({ role: m.role, content: m.content }))
    abortRef.current = connectSSE(apiMsgs, makeCallbacks())
  }, [stopTypewriter, makeCallbacks])

  useEffect(() => () => { if (abortRef.current) abortRef.current(); stopTypewriter() }, [stopTypewriter])

  return { messages, status, sendMessage, clearMessages, loadMessages, retry }
}
