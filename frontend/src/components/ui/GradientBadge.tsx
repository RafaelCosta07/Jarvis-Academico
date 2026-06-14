import { cn } from '@/lib/utils'

type BadgeVariant = 'aula' | 'prova' | 'prazo' | 'outro' | 'pendente' | 'concluida'

const DOT_COLORS: Record<BadgeVariant, string> = {
  aula:      'bg-academic-blue',
  prova:     'bg-academic-red',
  prazo:     'bg-academic-yellow',
  outro:     'bg-muted-foreground',
  pendente:  'bg-academic-yellow',
  concluida: 'bg-academic-green',
}

const VARIANT_LABELS: Record<BadgeVariant, string> = {
  aula: 'Aula', prova: 'Prova', prazo: 'Prazo', outro: 'Outro',
  pendente: 'Pendente', concluida: 'Concluída',
}

interface GradientBadgeProps {
  variant: BadgeVariant
  className?: string
}

export default function GradientBadge({ variant, className }: GradientBadgeProps) {
  return (
    <span className={cn(
      'inline-flex items-center gap-1.5 px-2 py-0.5 rounded-full text-xs font-medium',
      'bg-surface-2 border border-hairline text-foreground',
      className,
    )}>
      <span className={cn('w-1.5 h-1.5 rounded-full shrink-0', DOT_COLORS[variant])} aria-hidden="true" />
      {VARIANT_LABELS[variant]}
    </span>
  )
}
