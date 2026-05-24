interface NeuralPulseProps {
  size?: 'sm' | 'md'
}

const DELAYS = [0, 0.2, 0.4]
const SIZE: Record<string, string> = { sm: '6px', md: '8px' }

export default function NeuralPulse({ size = 'md' }: NeuralPulseProps) {
  const px = SIZE[size]
  return (
    <div className="flex items-center gap-1.5 p-3">
      {DELAYS.map((delay) => (
        <div
          key={delay}
          style={{
            width: px,
            height: px,
            borderRadius: '50%',
            background: 'linear-gradient(135deg, var(--color-primary-start), var(--color-primary-end))',
            animation: `pulse-wave 1.4s ease-in-out ${delay}s infinite`,
          }}
        />
      ))}
    </div>
  )
}
