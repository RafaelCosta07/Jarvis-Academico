interface AppShellProps {
  children: React.ReactNode;
}

export default function AppShell({ children }: AppShellProps) {
  return (
    <div className="shell-grid h-screen overflow-hidden bg-background">
      {children}
    </div>
  );
}
