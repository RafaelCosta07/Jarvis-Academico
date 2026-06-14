interface GradientButtonProps extends React.ButtonHTMLAttributes<HTMLButtonElement> {}

export default function GradientButton({ children, disabled, className = '', style, ...props }: GradientButtonProps) {
  return (
    <button
      disabled={disabled}
      className={`px-4 py-2 text-sm font-medium text-white transition-all
        ${disabled ? 'opacity-40 cursor-not-allowed' : 'cursor-pointer hover:opacity-90 active:scale-[0.98]'}
        ${className}`}
      style={{
        background: 'var(--color-primary)',
        borderRadius: 'var(--radius-md)',
        ...style,
      }}
      {...props}
    >
      {children}
    </button>
  )
}
