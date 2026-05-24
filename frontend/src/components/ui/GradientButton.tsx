interface GradientButtonProps extends React.ButtonHTMLAttributes<HTMLButtonElement> {}

export default function GradientButton({ children, disabled, className = '', style, ...props }: GradientButtonProps) {
  return (
    <button
      disabled={disabled}
      className={`px-4 py-2 text-sm font-medium text-white transition-opacity
        ${disabled ? 'opacity-40 cursor-not-allowed' : 'cursor-pointer hover:opacity-90'}
        ${className}`}
      style={{
        background: 'linear-gradient(135deg, var(--color-primary-start), var(--color-primary-end))',
        borderRadius: 'var(--radius-md)',
        ...style,
      }}
      {...props}
    >
      {children}
    </button>
  )
}
