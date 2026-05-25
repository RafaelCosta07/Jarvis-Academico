'use client'
import { useState, useEffect } from 'react'
import { FileText } from 'lucide-react'
import { getMateriais, getUrlMaterial, type Material } from '@/lib/api'

export default function MateriaisList() {
  const [materiais, setMateriais] = useState<Material[]>([])

  useEffect(() => {
    getMateriais().then(setMateriais).catch(() => setMateriais([]))
  }, [])

  if (materiais.length === 0) {
    return <p className="text-xs text-muted-foreground px-2">Nenhum material disponível</p>
  }

  return (
    <div className="flex flex-col gap-1">
      {materiais.map(m => (
        <a
          key={m.nome}
          href={getUrlMaterial(m.nome)}
          target="_blank"
          rel="noopener noreferrer"
          title={m.nome}
          className="flex items-center gap-2 px-2 py-1.5 rounded-md text-xs cursor-pointer bg-surface border border-border text-muted-foreground hover:text-foreground hover:border-[var(--color-primary-end)] hover:bg-glass-bg transition-all duration-150 group"
        >
          <FileText className="w-3.5 h-3.5 flex-shrink-0 group-hover:text-[var(--color-primary-end)] transition-colors" aria-hidden="true" />
          <span className="truncate flex-1">{m.titulo}</span>
        </a>
      ))}
    </div>
  )
}
