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
        background: 'var(--color-surface)',
        borderColor: error ? 'var(--color-academic-red)' : 'var(--color-hairline)',
        borderRadius: 'var(--radius-lg)',
        padding: '1rem',
        animation: error ? 'shake 0.4s ease-out' : undefined,
      }}
    >
      {children}
    </div>
  )
}
