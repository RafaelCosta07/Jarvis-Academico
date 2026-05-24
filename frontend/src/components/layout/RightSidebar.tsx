import { Separator } from '@/components/ui/separator'
import AgendaWidget from '@/components/agenda/AgendaWidget'
import TaskWidget from '@/components/tasks/TaskWidget'

export default function RightSidebar() {
  return (
    <aside className="h-full overflow-y-auto bg-surface border-l border-border flex flex-col p-4 gap-6">
      <AgendaWidget />
      <Separator className="bg-border" />
      <TaskWidget />
    </aside>
  )
}
