const COLORS = [
  'var(--color-academic-green)',
  'var(--color-primary-start)',
  'var(--color-academic-yellow)',
  'var(--color-primary-end)',
  'var(--color-academic-blue)',
  'var(--color-academic-green)',
]

interface ConfettiParticlesProps {
  active: boolean
}

export default function ConfettiParticles({ active }: ConfettiParticlesProps) {
  if (!active) return null
  return (
    <div className="pointer-events-none absolute inset-0 overflow-visible">
      {[0, 60, 120, 180, 240, 300].map((angle, i) => (
        <div
          key={i}
          className="absolute left-1/2 top-1/2 w-1.5 h-1.5 rounded-full"
          style={{
            background: COLORS[i],
            '--confetti-r': `${angle}deg`,
            animationDelay: `${i * 25}ms`,
            animation: 'confetti-fly 0.8s cubic-bezier(0.4, 0, 0.2, 1) forwards',
          } as React.CSSProperties}
        />
      ))}
    </div>
  )
}
