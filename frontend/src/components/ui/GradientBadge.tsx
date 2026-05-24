import { cn } from '@/lib/utils'

type BadgeVariant = 'aula' | 'prova' | 'prazo' | 'outro' | 'pendente' | 'concluida'

const VARIANT_STYLES: Record<BadgeVariant, string> = {
  aula:      'bg-academic-blue/20 text-academic-blue border-academic-blue/30',
  prova:     'bg-academic-red/20 text-academic-red border-academic-red/30',
  prazo:     'bg-academic-yellow/20 text-academic-yellow border-academic-yellow/30',
  outro:     'bg-muted-foreground/20 text-muted-foreground border-muted-foreground/30',
  pendente:  'bg-academic-yellow/20 text-academic-yellow border-academic-yellow/30',
  concluida: 'bg-academic-green/20 text-academic-green border-academic-green/30',
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
      'inline-flex items-center px-2 py-0.5 rounded-full text-xs font-medium border',
      VARIANT_STYLES[variant],
      className,
    )}>
      {VARIANT_LABELS[variant]}
    </span>
  )
}
