interface GlassCardProps {
  children: React.ReactNode
  className?: string
  error?: boolean
}

export default function GlassCard({ children, className = '', error = false }: GlassCardProps) {
  return (
    <div
      className={`border ${className}`}
      style={{
        background: 'var(--color-glass-bg)',
        backdropFilter: 'blur(var(--glass-blur))',
        borderColor: error ? 'var(--color-academic-red)' : 'var(--color-glass-border)',
        borderRadius: 'var(--radius-lg)',
        padding: '1rem',
        animation: error ? 'shake 0.4s ease-out' : undefined,
      }}
    >
      {children}
    </div>
  )
}
