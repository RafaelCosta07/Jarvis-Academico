'use client'
import { Separator } from '@/components/ui/separator'
import AgendaWidget from '@/components/agenda/AgendaWidget'
import TaskWidget from '@/components/tasks/TaskWidget'
import { useScrollFade } from '@/hooks/useScrollFade'

export default function RightSidebar() {
  const handleScroll = useScrollFade()

  return (
    <aside
      className="h-full overflow-y-auto bg-surface border-l border-border flex flex-col p-4 gap-6 scroll-fade"
      onScroll={handleScroll}
    >
      <AgendaWidget />
      <Separator className="bg-border" />
      <TaskWidget />
    </aside>
  )
}
