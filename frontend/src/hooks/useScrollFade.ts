import { useRef, useCallback } from 'react'

export function useScrollFade() {
  const timerRef = useRef<ReturnType<typeof setTimeout> | null>(null)

  const handleScroll = useCallback((e: React.UIEvent<HTMLElement>) => {
    const el = e.currentTarget
    el.classList.add('scrolling')
    if (timerRef.current) clearTimeout(timerRef.current)
    timerRef.current = setTimeout(() => {
      el.classList.remove('scrolling')
    }, 1500)
  }, [])

  return handleScroll
}
