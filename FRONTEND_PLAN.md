# FRONTEND_PLAN.md — Plano Completo de Implementação (v2 — Corrigido e Validado)
# JARVIS Acadêmico — Trabalho 1 (Funcionalidades 3.1, 3.2, 3.3)

> **Referência principal:** `SPEC.md` (mesma pasta)
> **Design system:** `SPEC.md` seção 2.5
> **Estrutura de arquivos:** `SPEC.md` seção 3
> **Diretório do projeto:** `C:\Users\teste.5\projetos\ia`
> **Frontend em:** `C:\Users\teste.5\projetos\ia\frontend\`
> **Versão:** v2 — Corrigida e validada contra o backend real
> **Decisões de implementação:**
> - Tailwind v4: tokens via `@theme {}` em `globals.css` (sem `tailwind.config.ts`)
> - shadcn: pacote `shadcn@latest` (não `shadcn-ui@latest` — deprecated)
> - Conclusão de tarefa: `PATCH /api/tasks/{id}/concluir` (REST, não via LLM)
> - Streaming: typewriter simulado no frontend (backend envia resposta única em SSE)
> - SSE parser: buffer obrigatório para chunks fragmentados
> - Conversas: `ConversationStore` com DIP (LocalStorageStore agora, ApiStore no T2)

---

## ÍNDICE

1. [FASE 2 — Wireframes ASCII](#fase-2)
2. [FASE 3 — Arquitetura de Componentes](#fase-3)
3. [FASE 4 — Plano de Implementação (7 sprints)](#fase-4)
4. [FASE 5 — Prompts para Claude CLI](#fase-5)

---

## FASE 2 — WIREFRAMES ASCII DETALHADOS {#fase-2}

### Convenções

```
┌─┐ └─┘ │        → bordas de containers
╭─╮ ╰─╯          → cards com border-radius (glass/academic)
▓▓▓▓▓▓▓▓▓▓       → gradiente roxo→azul (primary)
░░░░░░░░░░       → glassmorphism / surface escura
●  ●  ●          → Neural Pulse (loading)
···              → texto truncado
[N]              → nota numerada (ver legenda abaixo do wireframe)
```

---

### WIREFRAME 1 — Tela Principal (1440px, conversa ativa)

```
┌────────────────────────────────────────────────────────────────────────────────────────────────────────┐
│ background: hsl(240 10% 3.9%)                                                                          │
│                                                                                                        │
│ ╭──────────────────────╮  ╭──────────────────────────────────────────────────╮  ╭──────────────────╮  │
│ │░░░░░░░░░░░░░░░░░░░░░░│  │░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░│  │░░░░░░░░░░░░░░░░░░│  │
│ │                      │  │                                                  │  │                  │  │
│ │  ▓▓ J A R V I S ▓▓  │  │  Cálculo II — Integrais por partes          [1]  │  │  Maio  2026  [5] │  │
│ │  Academic Neural     │  │  ──────────────────────────────────────────────  │  │  S  T  Q  Q  S   │  │
│ │                      │  │  ⚡ RAG ativo · 2 tools chamadas                 │  │  ─  ─  ─  ─  ─   │  │
│ │ ╭──────────────────╮ │  │                                                  │  │ 19 20 21 22 23   │  │
│ │ │▓▓▓▓▓Nova conv▓▓▓▓│ │  │  ╭──────────────────────────────────────────╮   │  │ 26 27 28▓▓ 30   │  │
│ │ │▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓│[2]│  │░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░│   │  │                  │  │
│ │ ╰──────────────────╯ │  │  │░ Olá! Pode me explicar integração por    ░│   │  │  Hoje, 24/05 [6] │  │
│ │                      │  │  │░ partes? Vi nos slides mas não entendi   ░│[3]│  │  ──────────────  │  │
│ │  CONVERSAS       [3] │  │  │░ quando usar.                            ░│   │  │  09:00–10:30     │  │
│ │  ─────────────────── │  │  ╰──────────────────────────────────────────╯   │  │  ▓ Cálculo II    │  │
│ │  ◉ Cálculo II ···    │  │                                    você · 14:23  │  │    Sala B-204    │  │
│ │  ○ Resumo Cap. 4     │  │                                                  │  │                  │  │
│ │  ○ Lista exercícios  │  │   ╭──────────────────────────────────────────╮   │  │  14:00–16:00     │  │
│ │  ○ Dúvida POO        │  │   │░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░│   │  │    Lab POO       │  │
│ │  ○ Trabalho EngSW    │  │   │░  Boa pergunta! A integração por partes  ░│   │  │                  │  │
│ │  + ver todas         │  │   │░  vem da regra do produto da derivada.   ░│   │  │  TAREFAS     [7] │  │
│ │                      │  │   │░  A fórmula é:                           ░│[4]│  │  ──────────────  │  │
│ │  MATERIAIS           │  │   │░                                         ░│   │  │  ☐ Entregar TCC  │  │
│ │  ─────────────────── │  │   │░    ∫u·dv  =  u·v  −  ∫v·du             ░│   │  │    ▓ 3 dias      │  │
│ │  📄 Cálculo_2.pdf    │  │   │░                                         ░│   │  │  ☐ Lista Calc 2  │  │
│ │  📄 POO_slides.pdf   │  │   │░  Use quando o integrando for produto    ░│   │  │    amanhã        │  │
│ │  📄 EngSW_apostila   │  │   │░  de funções de tipos diferentes, ex:   ░│   │  │  ☑ Resumo Cap.3  │  │
│ │  + adicionar         │  │   │░  polinômio × exponencial.              ░│   │  │    concluída     │  │
│ │                      │  │   │░                                         ░│   │  │                  │  │
│ │                      │  │   │░  Fontes: Cálculo_2.pdf p.87, p.88      ░│   │  │  + nova tarefa   │  │
│ │                      │  │   ╰──────────────────────────────────────────╯   │  │                  │  │
│ │                      │  │                               JARVIS · 14:23     │  │                  │  │
│ │  ─────────────────── │  │                                                  │  │                  │  │
│ │  ◎ Usuário           │  │  ╭──────────────────────────────────────────╮    │  │                  │  │
│ │                      │  │  │░ Digite sua mensagem...                  ░│    │  │                  │  │
│ │                      │  │  │░                                         ░│    │  │                  │  │
│ │                      │  │  ╰──────────────────────────────────────────╯    │  │                  │  │
│ │                      │  │       [Enter para enviar · Shift+Enter = ↵]  ▓▓▓ │  │                  │  │
│ ╰──────────────────────╯  ╰──────────────────────────────────────────────────╯  ╰──────────────────╯  │
└────────────────────────────────────────────────────────────────────────────────────────────────────────┘

LEGENDA
[1] Header do chat: título + badge de tools ativas
[2] Botão "Nova Conversa": bg-gradient primary-start→primary-end, rounded-lg
[3] Mensagem USUÁRIO (Neural Bubble): gradiente roxo→azul, alinhada à direita
[4] Mensagem IA (Glass Card): glassmorphism, alinhada à esquerda, suporta Markdown
[5] Mini-calendário: dia atual destacado com gradiente
[6] Eventos do dia: borda-esquerda colorida por tipo (aula=blue, prova=red, prazo=yellow)
[7] Tarefas: checkbox interativo; prazo urgente (<2d) com badge vermelho
```

---

### WIREFRAME 2 — Estado de Loading

```
[2] Neural Pulse: 3 dots de 8px, animação staggered (delay 0s / 0.2s / 0.4s)
[3] Input desabilitado: opacity-40, cursor not-allowed
Header: ⚙ animado + "Processando..." + borda do chat pulsa com gradiente
```

### WIREFRAME 3 — Estado de Streaming (Typewriter Simulado)

```
[1] Header: ▶ Gerando resposta...
[2] Mensagem IA preenchida progressivamente via setInterval (typewriter simulado no frontend)
[3] Cursor piscante ▌ some quando typewriter termina (não quando SSE envia done —
    o done chega antes do typewriter terminar)
```

### WIREFRAME 4 — Estado Vazio

```
[1] 3 cards de sugestão clicáveis que disparam sendMessage automaticamente
```

### WIREFRAME 5 — Sidebar Direita

```
CORES POR TIPO DE EVENTO:
  aula  → academic-blue  hsl(199 89% 48%)
  prova → academic-red   hsl(0 72% 51%)
  prazo → academic-yellow hsl(45 93% 58%)
  outro → muted-foreground

CORES POR URGÊNCIA DE TAREFA:
  gradiente → prazo ≤ 3 dias (urgente)
  ⚠ amarelo → prazo = amanhã
  normal    → prazo > 3 dias
  riscado   → concluída (opacity-50)
```

### WIREFRAME 6 — Área de Input (estados)

```
Normal:   border 1px var(--color-border)
Focused:  borda gradiente animada 2s loop (roxo→azul percorre contorno)
Com texto: botão enviar ativo (GradientButton)
Disabled: opacity-40, cursor not-allowed
```

---

## FASE 3 — ARQUITETURA DE COMPONENTES {#fase-3}

### Árvore de Componentes

```
app/
├── layout.tsx                    ← providers globais (fontes, tema)
└── page.tsx                      ← orquestra hooks + monta AppShell

src/
├── components/
│   ├── layout/
│   │   ├── AppShell.tsx          ← grid 3 colunas, 100vh
│   │   ├── LeftSidebar.tsx       ← 20% — nav + histórico + materiais
│   │   └── RightSidebar.tsx      ← 20% — agenda + tarefas
│   ├── chat/
│   │   ├── ChatWindow.tsx        ← 60% — orquestra Header+List+Input
│   │   ├── ChatHeader.tsx        ← título + badge status
│   │   ├── ChatMessageList.tsx   ← ScrollArea + auto-scroll + proteção 100 msgs
│   │   ├── ChatMessage.tsx       ← decide user vs assistant
│   │   ├── ChatMessageUser.tsx   ← Neural Bubble (gradiente)
│   │   ├── ChatMessageAssistant.tsx ← Glass Card + Markdown + cursor
│   │   ├── ChatInput.tsx         ← textarea + envio + atalhos
│   │   └── ChatEmpty.tsx         ← tela inicial com sugestões
│   ├── agenda/
│   │   ├── AgendaWidget.tsx      ← fetch + exibe eventos
│   │   ├── AgendaMiniCal.tsx     ← calendário do mês
│   │   └── AgendaEventItem.tsx   ← item de evento
│   ├── tasks/
│   │   ├── TaskWidget.tsx        ← fetch + exibe tarefas
│   │   ├── TaskList.tsx          ← lista ordenada
│   │   ├── TaskItem.tsx          ← checkbox + otimistic update
│   │   └── TaskQuickAdd.tsx      ← input rápido nova tarefa
│   └── ui/
│       ├── NeuralPulse.tsx       ← 3 dots animados
│       ├── GradientBadge.tsx     ← badge por tipo
│       ├── GlassCard.tsx         ← glassmorphism
│       └── GradientButton.tsx    ← botão roxo→azul
├── hooks/
│   ├── useChat.ts                ← estado do chat + typewriter + integra useConversations
│   ├── useSSE.ts                 ← fetch + parser SSE com buffer
│   └── useConversations.ts       ← gerencia conversas (recebe ConversationStore via DIP)
├── lib/
│   ├── api.ts                    ← fetch wrappers para todos os endpoints
│   ├── utils.ts                  ← cn(), generateId(), formatTimestamp()
│   └── conversation-store.ts     ← interface ConversationStore + LocalStorageStore
└── types/
    ├── chat.ts                   ← Message, MessageRole, ChatStatus
    ├── api.ts                    ← SSEEvent, Evento, Tarefa
    └── conversation.ts           ← Conversation
```

### Types TypeScript

```typescript
// types/chat.ts
export type MessageRole = 'user' | 'assistant'
export type ChatStatus = 'idle' | 'loading' | 'streaming' | 'error'
export interface Message {
  id: string
  role: MessageRole
  content: string
  timestamp: Date
}

// types/api.ts
export interface SSEToken { type: 'token'; content: string }
export interface SSEDone  { type: 'done' }
export interface SSEError { type: 'error'; content: string }
export type SSEEvent = SSEToken | SSEDone | SSEError

export interface Evento {
  id: string; titulo: string; descricao: string | null
  data: string; hora_inicio: string | null; hora_fim: string | null
  tipo: 'aula' | 'prova' | 'prazo' | 'outro'; local: string | null
}

export interface Tarefa {
  id: string; titulo: string; descricao: string | null
  disciplina: string | null; status: 'pendente' | 'concluida'
  prazo: string | null; criada_em: string; concluida_em: string | null
}

// types/conversation.ts
export interface Conversation {
  id: string
  title: string
  messages: Message[]
  createdAt: Date
  updatedAt: Date
}
```

### Fluxo de Dados — Envio de Mensagem

```
ChatInput (Enter)
  └─► useChat.sendMessage(content)
        ├─ 1. Adiciona mensagem user
        ├─ 2. status = 'loading'
        ├─ 3. Adiciona mensagem assistant vazia
        └─► useSSE.connect(messages[])
              ├─ POST /api/chat → 1 evento SSE com resposta inteira
              ├─ onToken(fullContent):
              │    status = 'streaming'
              │    TYPEWRITER: setInterval 15ms/2chars até exibir tudo
              └─ onDone: quando typewriter termina → status = 'idle'
```

---

## FASE 4 — PLANO DE IMPLEMENTAÇÃO (7 Sprints) {#fase-4}

> **Regras globais (CLAUDE.md):**
> - `next.config.ts`: devIndicators: false, output: 'standalone'
> - TypeScript: zero `any`, props com `interface` explícita
> - Componentes: máx 20 linhas JSX, responsabilidade única (SRP)
> - Tailwind v4: tokens em `@theme {}` no `globals.css`

---

### SPRINT 0 — Setup Completo (~30 min) — MANUAL + CLI

**Parte 1 — Manual no terminal:**
```bash
cd C:\Users\teste.5\projetos\ia
# Deletar pasta vazia e recriar com create-next-app
Remove-Item -Recurse -Force frontend
npx create-next-app@latest frontend --typescript --tailwind --eslint --app --src-dir --import-alias "@/*" --no-git

cd frontend
npx shadcn@latest init --defaults
npx shadcn@latest add button card input textarea badge avatar scroll-area separator tooltip
npm install react-markdown remark-gfm lucide-react date-fns
```

**Parte 2 — Claude CLI** (ver Prompt Sprint 0 na Fase 5):
- `next.config.ts`: devIndicators + standalone
- `globals.css`: @import tailwindcss + @theme com todos os tokens SPEC 2.5
- `layout.tsx`: fontes Inter + JetBrains Mono

**⚠️ Tailwind v4:** tokens em `@theme {}`. Não editar `tailwind.config.ts` para cores/fontes.

**Critério:** localhost:3000 com fundo hsl(240 10% 3.9%) + gradiente roxo→azul visível.

---

### SPRINT 1 — Layout 3 Colunas (~1.5h)

Criar: `AppShell.tsx`, `LeftSidebar.tsx` (placeholder), `RightSidebar.tsx` (placeholder), `page.tsx`.

Breakpoints (SPEC 2.5): 1280px=18/64/18%, 1440px=20/60/20%, 1920px+=22/56/22%.

**Critério:** 3 colunas visíveis em 1440px. Sidebar com "JARVIS" em gradiente.

---

### SPRINT 2 — Chat UI com Mock (~2h)

Criar: `src/types/`, todos os `chat/`, `ui/NeuralPulse`, `GlassCard`, `GradientButton`.

Sem SSE. Dados mock hardcoded. Foco: visual correto.

**Critério:** Neural Bubble + Glass Card renderizam. NeuralPulse em loading. Cursor ▌ em streaming.

---

### SPRINT 3 — SSE + Typewriter Simulado (~1.5h)

Criar: `lib/api.ts`, `hooks/useSSE.ts` (parser com buffer), `hooks/useChat.ts` (typewriter 15ms/2chars).

**Critério:** mensagem enviada → resposta aparece progressivamente → input reabilita.

---

### SPRINT 4 — Sidebar Direita: Agenda + Tarefas (~2h)

**Endpoints reais do backend (CONFIRMADOS):**

| Método | Rota | Params | Retorno |
|---|---|---|---|
| GET | /api/agenda | ?data=YYYY-MM-DD | list[EventoRead] |
| GET | /api/tasks | ?status=pendente\|concluida | list[TarefaRead] |
| POST | /api/tasks | body TarefaCreate | TarefaRead |
| PATCH | /api/tasks/{id}/concluir | — | TarefaRead |

⚠️ **Atenção:**
- `?periodo=hoje` NÃO existe — calcular: `new Date().toISOString().split('T')[0]`
- `?status=todas` NÃO existe — omitir o param para buscar todas
- `POST /api/tasks/{id}/concluir` NÃO existe — usar `PATCH`

Criar: `AgendaWidget`, `AgendaMiniCal`, `AgendaEventItem`, `TaskWidget`, `TaskList`, `TaskItem` (otimistic update), `TaskQuickAdd`, `GradientBadge`.

**Critério:** eventos reais na sidebar, checkbox funciona com PATCH e reverte se falhar.

---

### SPRINT 5 — Sidebar Esquerda + Conversas (~1.5h)

Criar: `lib/conversation-store.ts` (interface + LocalStorageStore), `hooks/useConversations.ts` (recebe store via DIP), `LeftSidebar.tsx` real, integrar `useChat`.

**Critério:** nova conversa, trocar entre conversas, F5 persiste histórico.

---

### SPRINT 6 — Polish + Erros + Animações (~1h)

Implementar: hover cards, borda gradiente animada, fade-slide-up, smart scroll, proteção >100 msgs, toasts, retry em erro SSE.

**Critério:** `npm run build` limpo. Zero `any`. Zero warnings de console.

---

## FASE 5 — PROMPTS PARA CLAUDE CLI {#fase-5}

> **Regra de uso:** Sempre referenciar arquivos por caminho absoluto.
> O CLI lê os arquivos — não copiar conteúdo no prompt.
> Um prompt = um sprint. Terminar com "Não pergunte, implemente."

---

### PROMPT SPRINT 0 — Setup Completo do Zero

```
Você está criando o frontend JARVIS Acadêmico do zero. A pasta frontend/ existe mas está vazia (só estrutura de pastas sem arquivos).

CONTEXTO OBRIGATÓRIO — LEIA ANTES DE QUALQUER AÇÃO:
1. Leia C:\Users\teste.5\projetos\ia\SPEC.md — seção 2.5 completa (Design System Frontend). Extraia TODOS os tokens: cores, tipografia, espaçamentos, border-radius, sombras, glassmorphism.
2. Leia C:\Users\teste.5\projetos\ia\SPEC.md — seção 1.4 (Clean Code + SOLID).
3. Leia C:\Users\teste.5\projetos\ia\CLAUDE.md — regras obrigatórias do projeto.
4. Leia C:\Users\teste.5\projetos\ia\SPEC.md — seção 3 (Estrutura de Diretórios — parte do frontend/).
5. Verifique o conteúdo atual de C:\Users\teste.5\projetos\ia\frontend\ — liste os arquivos existentes para entender o estado real.

O ESTADO ATUAL: A pasta frontend/ tem apenas a estrutura de diretórios vazia:
frontend/
├── public/
└── src/
    ├── app/
    ├── components/
    │   ├── agenda/
    │   ├── chat/
    │   ├── tasks/
    │   └── ui/
    ├── hooks/
    ├── lib/
    └── types/

NÃO existe: package.json, node_modules, next.config.ts, globals.css, layout.tsx, tsconfig.json.

ETAPA 1 — INICIALIZAR O PROJETO (executar no terminal)

cd C:\Users\teste.5\projetos\ia

Remove-Item -Recurse -Force frontend
npx create-next-app@latest frontend --typescript --tailwind --eslint --app --src-dir --import-alias "@/*" --no-git

Se o create-next-app pedir input interativo, usar: --yes

Após criar, verificar que existem: package.json, next.config.ts, src/app/layout.tsx, src/app/globals.css, tsconfig.json.

ETAPA 2 — INSTALAR DEPENDÊNCIAS

cd C:\Users\teste.5\projetos\ia\frontend

npx shadcn@latest init --defaults
npx shadcn@latest add button card input textarea badge avatar scroll-area separator tooltip
npm install react-markdown remark-gfm lucide-react date-fns

ETAPA 3 — RECRIAR ESTRUTURA DE PASTAS

mkdir -p src/components/layout
mkdir -p src/components/chat
mkdir -p src/components/agenda
mkdir -p src/components/tasks
mkdir -p src/hooks
mkdir -p src/lib
mkdir -p src/types

ETAPA 4 — CONFIGURAR next.config.ts

Editar com as regras do CLAUDE.md:
- devIndicators: false
- output: 'standalone'

Ler o arquivo existente primeiro para adaptar ao formato correto da versão instalada.

ETAPA 5 — REESCREVER src/app/globals.css

ATENÇÃO CRÍTICA: Tailwind v4.
- Usar @import "tailwindcss" (NÃO @tailwind base/components/utilities)
- Tokens em @theme {} (NÃO em tailwind.config.ts nem em :root{})

Conteúdo completo:

@import "tailwindcss";

@theme {
  --color-background: hsl(240 10% 3.9%);
  --color-surface: hsl(240 5% 6%);
  --color-foreground: hsl(0 0% 98%);
  --color-muted-foreground: hsl(240 5% 64.9%);
  --color-primary-start: hsl(250 95% 65%);
  --color-primary-end: hsl(217 91% 60%);
  --color-primary-glow: hsla(250 95% 65% / 0.15);
  --color-academic-yellow: hsl(45 93% 58%);
  --color-academic-green: hsl(142 76% 36%);
  --color-academic-red: hsl(0 72% 51%);
  --color-academic-blue: hsl(199 89% 48%);
  --color-glass-bg: hsla(240 10% 15% / 0.6);
  --color-glass-border: hsla(0 0% 100% / 0.1);
  --color-border: hsl(240 3.7% 15.9%);
  --color-input: hsl(240 3.7% 15.9%);
  --color-ring: hsl(250 95% 65%);
  --font-sans: 'Inter Variable', system-ui, sans-serif;
  --font-mono: 'JetBrains Mono', 'Fira Code', monospace;
  --radius-sm: 0.375rem;
  --radius-md: 0.5rem;
  --radius-lg: 0.75rem;
  --radius-xl: 1rem;
  --radius-2xl: 1.5rem;
  --shadow-neural: 0 0 30px hsla(250 95% 65% / 0.2), 0 10px 25px rgb(0 0 0 / 0.3);
}

--glass-blur: 12px; /* fora do @theme — não gera utility class */

body {
  background: var(--color-background);
  color: var(--color-foreground);
  font-family: var(--font-sans);
}

@keyframes pulse-wave {
  0%, 80%, 100% { transform: scale(0); }
  40% { transform: scale(1.0); }
}
@keyframes blink {
  0%, 100% { opacity: 1; }
  50% { opacity: 0; }
}
@keyframes fade-slide-up {
  from { opacity: 0; transform: translateY(8px); }
  to { opacity: 1; transform: translateY(0); }
}

NOTA: Se o shadcn init gerou variáveis próprias (--background, --foreground etc.),
manter compatibilidade. Nossos tokens com prefixo --color- são adicionais.

ETAPA 6 — EDITAR src/app/layout.tsx

- Importar Inter e JetBrains Mono via next/font/google
- Aplicar variáveis no <html lang="pt-BR">
- Metadata: title "JARVIS Acadêmico", description "Assistente pessoal acadêmico com IA"
- Importar globals.css

ETAPA 7 — CRIAR src/app/page.tsx (placeholder)

export default function Home() {
  return (
    <main className="flex min-h-screen items-center justify-center">
      <h1 className="text-2xl font-bold bg-gradient-to-r from-[var(--color-primary-start)] to-[var(--color-primary-end)] bg-clip-text text-transparent">
        JARVIS Acadêmico
      </h1>
    </main>
  )
}

CRITÉRIO DE CONCLUSÃO — VERIFICAR EXECUTANDO:
1. npm run dev → inicia sem erro
2. localhost:3000: fundo quase preto + texto "JARVIS Acadêmico" com gradiente roxo→azul
3. DevTools Computed: --color-primary-start resolve corretamente
4. npm run build → sem erros TypeScript
5. Existem: src/components/ui/ (shadcn), src/hooks/, src/lib/, src/types/ (pastas)

Atualizar MEMORY.md:
| Fase 6 — Sprint 0 (Setup Completo) | ✅ Concluída | create-next-app + shadcn@latest + dependências. next.config.ts (devIndicators:false, output:standalone). globals.css @theme Tailwind v4 com todos os tokens SPEC 2.5. layout.tsx Inter + JetBrains Mono. page.tsx placeholder com gradiente validado. |

Não pergunte, implemente.
```

---

### PROMPT SPRINT 1 — Layout 3 Colunas

```
Você está implementando o layout 3 colunas do JARVIS Acadêmico.

Os sprints anteriores já foram implementados. Confira os arquivos existentes em src/ antes de implementar.

CONTEXTO OBRIGATÓRIO — LEIA ANTES DE QUALQUER AÇÃO:
1. Leia C:\Users\teste.5\projetos\ia\SPEC.md — seção 2.5 (Layout Híbrido — 3 Colunas, Breakpoints Responsivos).
2. Leia C:\Users\teste.5\projetos\ia\SPEC.md — seção 1.4 (Clean Code + SOLID).
3. Leia C:\Users\teste.5\projetos\ia\CLAUDE.md — regras obrigatórias.
4. Leia C:\Users\teste.5\projetos\ia\frontend\src\app\globals.css — tokens já configurados.
5. Leia C:\Users\teste.5\projetos\ia\frontend\src\app\layout.tsx — fontes já configuradas.

REGRAS DE CÓDIGO (SPEC seção 1.4):
- Máximo 20 linhas de JSX por componente.
- Props tipadas com interface explícita. Zero 'any'.
- Nomes auto-explicativos. Componentes com responsabilidade única (SRP).

CRIAR:

1. src/components/layout/AppShell.tsx
   - Grid CSS 3 colunas. Proporções por viewport (SPEC seção 2.5):
     - 1280px: 18% | 64% | 18%
     - 1440px: 20% | 60% | 20% (padrão)
     - 1920px+: 22% | 56% | 22%
   - Altura 100vh, overflow hidden.
   - background: var(--color-background)
   - Props: interface AppShellProps { children: React.ReactNode }

2. src/components/layout/LeftSidebar.tsx
   - Placeholder: fundo var(--color-surface), borda direita 1px var(--color-border).
   - Texto "JARVIS" com bg-clip-text sobre gradiente primary-start→primary-end.
   - Altura 100%, overflow-y auto.
   - Interface: LeftSidebarProps (vazia por ora).

3. src/components/layout/RightSidebar.tsx
   - Placeholder: fundo var(--color-surface), borda esquerda 1px var(--color-border).
   - Texto "Agenda + Tarefas" centralizado em muted-foreground.
   - Altura 100%, overflow-y auto.
   - Interface: RightSidebarProps (vazia por ora).

4. src/app/page.tsx
   - Importa AppShell, LeftSidebar, RightSidebar.
   - Área central: div vazia com fundo var(--color-background).
   - Sem lógica, sem estado (SRP).

CRITÉRIO DE CONCLUSÃO — VERIFICAR EXECUTANDO:
1. npm run dev → 3 colunas visivelmente separadas.
2. Sidebar esquerda: fundo mais claro, "JARVIS" com gradiente roxo→azul.
3. Sidebar direita: fundo mais claro, texto placeholder.
4. Redimensionar: proporções mudam nos breakpoints.
5. npm run build sem erros.

Atualizar MEMORY.md:
| Fase 6 — Sprint 1 (Layout 3 Colunas) | ✅ Concluída | AppShell.tsx, LeftSidebar.tsx, RightSidebar.tsx, page.tsx. Grid responsivo 3 breakpoints. |

Não pergunte, implemente.
```

---

### PROMPT SPRINT 2 — Chat UI (Mock)

```
Você está implementando os componentes visuais de chat do JARVIS Acadêmico.

Os sprints anteriores já foram implementados. Confira os arquivos existentes em src/ antes de implementar.

CONTEXTO OBRIGATÓRIO — LEIA ANTES DE QUALQUER AÇÃO:
1. Leia C:\Users\teste.5\projetos\ia\SPEC.md — seção 2.5 COMPLETA (Neural Bubble, Glass Card, Neural Pulse, Micro-interações, estados interativos).
2. Leia C:\Users\teste.5\projetos\ia\SPEC.md — seção 1.4 (Clean Code + SOLID).
3. Leia C:\Users\teste.5\projetos\ia\CLAUDE.md — regras obrigatórias.
4. Leia C:\Users\teste.5\projetos\ia\frontend\src\app\globals.css — keyframes disponíveis.
5. Leia C:\Users\teste.5\projetos\ia\frontend\src\components\layout\AppShell.tsx — onde o chat será montado.

FOCO: Componentes visuais apenas. SEM SSE, SEM API. Usar dados mock.

CRIAR:

1. src/types/chat.ts
export type MessageRole = 'user' | 'assistant'
export type ChatStatus = 'idle' | 'loading' | 'streaming' | 'error'
export interface Message { id: string; role: MessageRole; content: string; timestamp: Date }

2. src/types/api.ts
export interface SSEToken { type: 'token'; content: string }
export interface SSEDone  { type: 'done' }
export interface SSEError { type: 'error'; content: string }
export type SSEEvent = SSEToken | SSEDone | SSEError
export interface Evento { id:string; titulo:string; descricao:string|null; data:string; hora_inicio:string|null; hora_fim:string|null; tipo:'aula'|'prova'|'prazo'|'outro'; local:string|null }
export interface Tarefa { id:string; titulo:string; descricao:string|null; disciplina:string|null; status:'pendente'|'concluida'; prazo:string|null; criada_em:string; concluida_em:string|null }

3. src/components/ui/NeuralPulse.tsx
   - 3 círculos 8px com gradiente primary-start→primary-end.
   - Animação pulse-wave 1.4s ease-in-out infinite. Delays: 0s, 0.2s, 0.4s.
   - Props: interface NeuralPulseProps { size?: 'sm' | 'md' }

4. src/components/ui/GlassCard.tsx
   - bg: var(--color-glass-bg), backdrop-blur: 12px
   - border: 1px solid var(--color-glass-border), border-radius: var(--radius-lg)
   - Props: interface GlassCardProps { children: React.ReactNode; className?: string }

5. src/components/ui/GradientButton.tsx
   - bg: linear-gradient(135deg, var(--color-primary-start), var(--color-primary-end))
   - Props: interface GradientButtonProps extends React.ButtonHTMLAttributes<HTMLButtonElement> {}
   - Disabled: opacity-40, cursor not-allowed.

6. src/components/chat/ChatMessageUser.tsx
   - Neural Bubble: gradiente 135deg, alinhado direita, max-width 75%, padding 1rem.
   - Timestamp: text-xs font-mono muted-foreground abaixo.
   - Props: interface ChatMessageUserProps { content: string; timestamp: Date }

7. src/components/chat/ChatMessageAssistant.tsx
   - Usa GlassCard. Alinhado esquerda, max-width 85%.
   - react-markdown + remark-gfm. Code blocks: font-mono bg-surface.
   - isStreaming=true: cursor ▌ piscante (animação blink do globals.css).
   - Props: interface ChatMessageAssistantProps { content: string; timestamp: Date; isStreaming?: boolean }

8. src/components/chat/ChatMessage.tsx
   - Decide ChatMessageUser vs ChatMessageAssistant.
   - Props: interface ChatMessageProps { message: Message; isStreaming?: boolean }

9. src/components/chat/ChatInput.tsx
   - Textarea shadcn controlada, auto-resize 1-6 linhas.
   - Foco: borda gradiente animada 2s loop.
   - Botão: GradientButton (desabilitado se disabled=true OU texto vazio).
   - Enter envia, Shift+Enter quebra linha.
   - Props: interface ChatInputProps { onSend: (content: string) => void; disabled?: boolean }

10. src/components/chat/ChatEmpty.tsx
    - Logo JARVIS centralizado com gradiente texto.
    - 3 cards GlassCard clicáveis com hover translateY(-4px) + shadow-neural:
      "📚 Explicar um conceito", "📅 O que tenho hoje?", "✅ Ver tarefas"
    - Props: interface ChatEmptyProps { onSuggestionClick: (text: string) => void }

11. src/components/chat/ChatMessageList.tsx
    - ScrollArea shadcn. Auto-scroll quando messages[] muda.
    - Mapeia messages[] → ChatMessage. NeuralPulse quando status='loading'.
    - Props: interface ChatMessageListProps { messages: Message[]; status: ChatStatus }

12. src/components/chat/ChatHeader.tsx
    - Título (prop title). Badge: idle=nada, loading="⚙ Processando...", streaming="▶ Gerando...", error="⚠ Erro".
    - loading/streaming: borda inferior pulsa com gradiente.
    - Props: interface ChatHeaderProps { title: string; status: ChatStatus }

13. src/components/chat/ChatWindow.tsx
    - Compõe: ChatHeader + ChatMessageList + ChatInput.
    - messages vazio + status idle → ChatEmpty.
    - MOCK TEMPORÁRIO (remover no Sprint 3):
      const mockMessages: Message[] = [
        { id:'1', role:'user', content:'O que são embeddings?', timestamp: new Date() },
        { id:'2', role:'assistant', content:'Embeddings são representações vetoriais densas...', timestamp: new Date() },
      ]
    - Props: interface ChatWindowProps { messages: Message[]; status: ChatStatus; title: string; onSend: (content: string) => void }

14. Editar src/app/page.tsx
    - Importar ChatWindow no slot central do AppShell.
    - Passar mock messages e status idle.

CRITÉRIO DE CONCLUSÃO — VERIFICAR EXECUTANDO:
1. 2 mensagens mock: Neural Bubble (direita, gradiente) + Glass Card (esquerda, glassmorphism).
2. Mudar mockStatus para 'loading': NeuralPulse aparece (3 dots animados).
3. ChatMessageAssistant com isStreaming=true: cursor ▌ pisca.
4. ChatInput: foco mostra borda gradiente. Enter chama onSend. Shift+Enter quebra linha.
5. messages=[] (testar removendo mock): ChatEmpty com 3 sugestões.
6. npm run build sem erros. Zero 'any'.

Atualizar MEMORY.md:
| Fase 6 — Sprint 2 (Chat UI Mock) | ✅ Concluída | 14 componentes: types/, chat/, ui/. Neural Bubble + Glass Card + NeuralPulse + ChatInput + ChatEmpty funcionais com mock. |

Não pergunte, implemente.
```

---

### PROMPT SPRINT 3 — SSE + Typewriter Simulado

```
Você está implementando a integração SSE do JARVIS Acadêmico com typewriter simulado.

Os sprints anteriores já foram implementados. Confira os arquivos existentes em src/ antes de implementar.

CONTEXTO OBRIGATÓRIO — LEIA ANTES DE QUALQUER AÇÃO:
1. Leia C:\Users\teste.5\projetos\ia\SPEC.md — seção 2.3 (Padrões de Comunicação).
2. Leia C:\Users\teste.5\projetos\ia\SPEC.md — seção 1.4 (Clean Code + SOLID).
3. Leia C:\Users\teste.5\projetos\ia\CLAUDE.md — regras obrigatórias (seção 7: endpoints).
4. Leia C:\Users\teste.5\projetos\ia\backend\app\api\routes\chat.py — formato EXATO do SSE.
5. Leia C:\Users\teste.5\projetos\ia\frontend\src\types\chat.ts — tipos disponíveis.
6. Leia C:\Users\teste.5\projetos\ia\frontend\src\types\api.ts — SSEEvent disponível.
7. Leia C:\Users\teste.5\projetos\ia\frontend\src\components\chat\ChatWindow.tsx — onde o mock será removido.

INFORMAÇÃO CRÍTICA SOBRE O BACKEND:
O chat.py NÃO faz streaming token-a-token. Ele:
1. Aguarda resposta COMPLETA do orchestrator
2. Emite UM ÚNICO evento: data: {"type":"token","content":"<resposta inteira>"}\n\n
3. Emite: data: {"type":"done"}\n\n
O typewriter DEVE ser simulado no frontend para preservar a UX dos wireframes.

CRIAR:

1. src/lib/api.ts
   - API_URL: process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000'
   - postChat(messages: Array<{role:string; content:string}>): Promise<Response>
     fetch POST /api/chat, Content-Type application/json

2. src/lib/utils.ts
   - cn(): classnames helper (padrão shadcn)
   - generateId(): string — crypto.randomUUID()
   - formatTimestamp(date: Date): string — formato HH:MM

3. src/hooks/useSSE.ts
   Responsabilidade única: gerenciar conexão fetch + parsing SSE.

   Interface:
   interface UseSSECallbacks { onToken: (c: string)=>void; onDone: ()=>void; onError: (m: string)=>void }

   PARSER COM BUFFER OBRIGATÓRIO:
   let buffer = ""
   // A cada chunk lido:
   buffer += decoder.decode(value, { stream: true })
   while (buffer.includes("\n\n")) {
     const idx = buffer.indexOf("\n\n")
     const rawEvent = buffer.slice(0, idx).trim()
     buffer = buffer.slice(idx + 2)
     if (rawEvent.startsWith("data: ")) {
       const json = JSON.parse(rawEvent.slice(6))
       // chamar callback por json.type
     }
   }
   // Isso evita tokens cortados em chunks fragmentados.

   - AbortController no cleanup. Retornar abort().

4. src/hooks/useChat.ts
   Estado: messages: Message[], status: ChatStatus

   sendMessage(content: string):
   1. Gerar UUID para user. Adicionar a messages[].
   2. status = 'loading'.
   3. Gerar UUID para assistant (vazio). Adicionar a messages[].
   4. Chamar useSSE.
   5. onToken(fullContent):
      - status = 'streaming'
      - TYPEWRITER: NÃO setar content inteiro de uma vez.
        setInterval a cada 15ms: adicionar 2 chars à última mensagem.
        Constantes: TYPEWRITER_SPEED_MS = 15, CHARS_PER_TICK = 2.
        Se fullContent.length < 50: setar direto (resposta curta).
   6. onDone: quando typewriter terminar → status = 'idle'.
   7. onError(msg): status = 'error', setar content da última mensagem.

   clearMessages(): estado inicial.
   Retorna: { messages, status, sendMessage, clearMessages }

5. EDITAR src/app/page.tsx
   - Substituir mock por useChat.
   - Passar messages, status, sendMessage para ChatWindow.
   - Remover dados mock do Sprint 2.

6. CRIAR frontend/.env.local
   NEXT_PUBLIC_API_URL=http://localhost:8000

CRITÉRIO DE CONCLUSÃO — VERIFICAR COM BACKEND RODANDO:
1. Digitar mensagem → resposta aparece progressivamente (typewriter).
2. Cursor ▌ durante streaming, some quando typewriter termina.
3. Input desabilitado durante loading/streaming. Reabilita após done.
4. Backend offline → "Erro ao conectar. Tente novamente." no lugar da resposta.
5. npm run build sem erros. Zero 'any'.

Atualizar MEMORY.md:
| Fase 6 — Sprint 3 (SSE + Typewriter) | ✅ Concluída | lib/api.ts, lib/utils.ts, hooks/useSSE.ts (parser com buffer), hooks/useChat.ts (typewriter 15ms/2chars). Mock removido. .env.local criado. |

Não pergunte, implemente.
```

---

### PROMPT SPRINT 4 — Agenda + Tarefas

```
Você está implementando os widgets de Agenda e Tarefas do JARVIS Acadêmico.

Os sprints anteriores já foram implementados. Confira os arquivos existentes em src/ antes de implementar.

CONTEXTO OBRIGATÓRIO — LEIA ANTES DE QUALQUER AÇÃO:
1. Leia C:\Users\teste.5\projetos\ia\SPEC.md — seção 2.5 (Academic Card, cores por tipo, Micro-interações).
2. Leia C:\Users\teste.5\projetos\ia\SPEC.md — seções 4.2 e 4.3 (schemas de Evento e Tarefa).
3. Leia C:\Users\teste.5\projetos\ia\SPEC.md — seção 1.4 (Clean Code + SOLID).
4. Leia C:\Users\teste.5\projetos\ia\CLAUDE.md — regras (seção 7: tabela de endpoints).
5. Leia C:\Users\teste.5\projetos\ia\backend\app\api\routes\tasks.py — endpoints REAIS.
6. Leia C:\Users\teste.5\projetos\ia\backend\app\api\routes\agenda.py — endpoints REAIS.
7. Leia C:\Users\teste.5\projetos\ia\frontend\src\types\api.ts — Evento e Tarefa já definidos.
8. Leia C:\Users\teste.5\projetos\ia\frontend\src\lib\api.ts — para adicionar wrappers.

ENDPOINTS REAIS DO BACKEND (confirmados no código — NÃO assumir outros):
- GET  /api/agenda              → list[EventoRead] (?tipo=, ?data=YYYY-MM-DD)
- GET  /api/tasks               → list[TarefaRead] (?status=pendente|concluida, ?disciplina=)
- POST /api/tasks               → TarefaRead (body: {titulo, descricao?, disciplina?, prazo?})
- PATCH /api/tasks/{id}/concluir → TarefaRead (409 se já concluída)

⚠️ ATENÇÃO:
- ?periodo=hoje NÃO EXISTE → calcular: new Date().toISOString().split('T')[0]
- ?status=todas NÃO EXISTE → omitir param para buscar todas (None = sem filtro)
- POST /tasks/{id}/concluir NÃO EXISTE → usar PATCH

CRIAR:

1. Adicionar a src/lib/api.ts:
   getAgendaHoje(): Promise<Evento[]>        → GET /api/agenda?data={hoje}
   getTarefas(status?): Promise<Tarefa[]>    → GET /api/tasks ou ?status=pendente
   concluirTarefa(id: string): Promise<Tarefa> → PATCH /api/tasks/{id}/concluir
   criarTarefa(titulo, disciplina?, prazo?): Promise<Tarefa> → POST /api/tasks

2. src/components/ui/GradientBadge.tsx
   - tipo: 'aula'|'prova'|'prazo'|'outro'|'urgente'|'concluida'
   - Mapa de cores: aula=academic-blue, prova=academic-red, prazo=academic-yellow,
     urgente=academic-red pulsante, concluida=academic-green
   - text-xs, padding horizontal, radius-sm.

3. src/components/agenda/AgendaEventItem.tsx
   - Borda esquerda 3px colorida por tipo.
   - Exibe: hora_inicio–hora_fim (ou "Dia todo"), titulo, local.
   - GradientBadge do tipo. Hover: translateY(-2px) + shadow-sm, 200ms.
   - Props: interface AgendaEventItemProps { evento: Evento }

4. src/components/agenda/AgendaMiniCal.tsx
   - Grid 7 colunas (D S T Q Q S S — formato pt-BR).
   - Dia atual: circle com gradiente primary-start→primary-end.
   - Dias com eventos: dot 4px abaixo (cor do tipo mais urgente).
   - Usa date-fns.
   - Props: interface AgendaMiniCalProps { currentDate: Date; eventos: Evento[] }

5. src/components/agenda/AgendaWidget.tsx
   - useEffect mount: fetch getAgendaHoje().
   - Estado: eventos[], loading, error.
   - Loading: NeuralPulse. Erro: "Não foi possível carregar a agenda".
   - Renderiza: AgendaMiniCal + "Hoje, {data}" + lista AgendaEventItem.
   - Sem eventos: "Nenhum evento para hoje".

6. src/components/tasks/TaskItem.tsx
   - Checkbox + título + GradientBadge disciplina + prazo.
   - Urgência (date-fns): ≤2d=academic-red pulsante, amanhã=academic-yellow ⚠.
   - Concluída: opacity-50, text-line-through.
   - Checkbox click: otimistic update → concluirTarefa(id) → reverter se falhar.
   - Props: interface TaskItemProps { tarefa: Tarefa; onToggle: (id: string) => void }

7. src/components/tasks/TaskList.tsx
   - Ordena: urgentes → por prazo → concluídas. Mapeia → TaskItem.
   - Props: interface TaskListProps { tarefas: Tarefa[]; onToggle: (id: string) => void }

8. src/components/tasks/TaskWidget.tsx
   - useEffect mount: fetch getTarefas() (todas — sem param status).
   - Estado: tarefas[], loading, error. Contador "X de Y concluídas".
   - handleToggle: concluirTarefa → atualiza lista local.
   - Botão "+ Nova tarefa" abre TaskQuickAdd.

9. src/components/tasks/TaskQuickAdd.tsx
   - Input + GradientButton confirmar.
   - criarTarefa(titulo) → limpa input → callback onTaskCreated.
   - Props: interface TaskQuickAddProps { onTaskCreated: () => void }

10. EDITAR src/components/layout/RightSidebar.tsx
    - Substituir placeholder: AgendaWidget + Separator + TaskWidget.

CRITÉRIO DE CONCLUSÃO — VERIFICAR COM BACKEND RODANDO:
1. Mini-cal renderiza mês. Dia de hoje destacado com gradiente.
2. Eventos do dia com cores corretas por tipo.
3. Tarefas listadas. Badges de urgência corretos.
4. Checkbox → concluída instantaneamente (otimistic) → API chamada.
5. API falhar → checkbox reverte + feedback de erro.
6. "+ Nova tarefa" → aparece na lista.
7. npm run build sem erros. Zero 'any'.

Atualizar MEMORY.md:
| Fase 6 — Sprint 4 (Agenda + Tarefas) | ✅ Concluída | AgendaWidget, AgendaMiniCal, AgendaEventItem, TaskWidget, TaskList, TaskItem (otimistic), TaskQuickAdd, GradientBadge. Endpoints: GET /api/agenda?data=, GET /api/tasks, PATCH /tasks/{id}/concluir, POST /api/tasks. |

Não pergunte, implemente.
```

---

### PROMPT SPRINT 5 — Sidebar Esquerda + Conversas

```
Você está implementando a sidebar esquerda e gerenciamento de conversas do JARVIS Acadêmico.

Os sprints anteriores já foram implementados. Confira os arquivos existentes em src/ antes de implementar.

CONTEXTO OBRIGATÓRIO — LEIA ANTES DE QUALQUER AÇÃO:
1. Leia C:\Users\teste.5\projetos\ia\SPEC.md — seção 2.5 (sidebar esquerda, Micro-interações).
2. Leia C:\Users\teste.5\projetos\ia\SPEC.md — seção 1.4 (Clean Code + SOLID — especialmente DIP).
3. Leia C:\Users\teste.5\projetos\ia\CLAUDE.md — regras (seção 6: SOLID no frontend).
4. Leia C:\Users\teste.5\projetos\ia\frontend\src\hooks\useChat.ts — hook a integrar.
5. Leia C:\Users\teste.5\projetos\ia\frontend\src\components\layout\LeftSidebar.tsx — placeholder atual.
6. Leia C:\Users\teste.5\projetos\ia\frontend\src\components\chat\ChatEmpty.tsx — sugestões existentes.
7. Leia C:\Users\teste.5\projetos\ia\frontend\src\app\page.tsx — orquestração atual.

DIP OBRIGATÓRIO: useConversations recebe ConversationStore como parâmetro.
Motivo: no T2 trocaremos LocalStorageStore por ApiConversationStore sem alterar useChat.

CRIAR:

1. src/types/conversation.ts
   export interface Conversation { id:string; title:string; messages:Message[]; createdAt:Date; updatedAt:Date }

2. src/lib/conversation-store.ts
   // Interface abstrata
   export interface ConversationStore {
     getAll(): Conversation[]
     getById(id: string): Conversation | null
     create(c: Conversation): void
     update(id: string, data: Partial<Conversation>): void
     remove(id: string): void
   }

   // Implementação concreta — localStorage
   export class LocalStorageStore implements ConversationStore {
     private readonly KEY = 'jarvis_conversations'
     // getAll(): retorna array ordenado por updatedAt desc
     // Serializar/deserializar Date corretamente (JSON.stringify perde tipo)
     // try/catch com fallback para array em memória se localStorage indisponível
   }

   // Factory (DIP)
   export function createConversationStore(): ConversationStore {
     return new LocalStorageStore()
   }

3. src/hooks/useConversations.ts
   - Recebe store: ConversationStore como parâmetro (DIP — não importar localStorage diretamente).
   - Estado: conversations: Conversation[], activeId: string | null.
   - createConversation(): cria conversa vazia, seta como ativa.
   - selectConversation(id): seta activeId.
   - deleteConversation(id): remove, se ativa limpa activeId.
   - updateConversation(id, messages): atualiza + updatedAt.
   - Título automático: primeiras 40 chars da primeira mensagem user.
   - Retorna: { conversations, activeId, activeConversation, createConversation, selectConversation, deleteConversation, updateConversation }

4. EDITAR src/hooks/useChat.ts
   - sendMessage: se não há conversa ativa → createConversation() automaticamente.
   - Quando typewriter termina: updateConversation(activeId, messages).
   - clearMessages(): cria nova conversa automaticamente.

5. src/components/layout/LeftSidebar.tsx (REESCREVER)
   a) Logo "JARVIS" gradiente + "Academic" em muted-foreground.
   b) GradientButton "Nova Conversa" full-width → createConversation().
   c) ScrollArea com lista de conversas:
      - Ativo: bg-surface + borda esquerda 2px gradiente.
      - Inativo: hover bg-surface/50.
      - Título 40 chars + data relativa via date-fns formatDistanceToNow.
      - Botão X no hover para deletar.
   d) Seção "Materiais": lista hardcoded de PDFs de /backend/data/documents/. Ícone 📄 + nome.
   e) Rodapé: separador + avatar + "Estudante".
   Props: interface LeftSidebarProps { conversations: Conversation[]; activeId: string|null; onNew: ()=>void; onSelect: (id:string)=>void; onDelete: (id:string)=>void }

6. EDITAR src/components/chat/ChatEmpty.tsx
   - Clicar em sugestão → onSuggestionClick(text) → page.tsx chama sendMessage diretamente.

7. EDITAR src/app/page.tsx
   - const store = createConversationStore()
   - const conv = useConversations(store)
   - const chat = useChat(...)
   - Integrar: activeId muda → useChat carrega messages da conversa.
   - Props corretas para LeftSidebar, ChatWindow, RightSidebar.

CRITÉRIO DE CONCLUSÃO — VERIFICAR EXECUTANDO:
1. App abre: ChatEmpty + sidebar com "JARVIS" + lista vazia.
2. Clicar sugestão → mensagem enviada → conversa criada na sidebar.
3. "Nova Conversa" → chat limpa → nova entrada na sidebar.
4. Título muda para primeiros 40 chars após resposta.
5. Clicar conversa anterior → mensagens restauradas.
6. X em conversa → removida da lista.
7. F5 → conversas persistidas na sidebar.
8. npm run build sem erros. Zero 'any'.

Atualizar MEMORY.md:
| Fase 6 — Sprint 5 (Sidebar + Conversas) | ✅ Concluída | conversation-store.ts (DIP: ConversationStore + LocalStorageStore), useConversations.ts, LeftSidebar.tsx real, useChat integrado, page.tsx orquestrado. |

Não pergunte, implemente.
```

---

### PROMPT SPRINT 6 — Polish + Erros + Animações

```
Você está finalizando o frontend JARVIS Acadêmico com animações, erros e polish.

Os sprints anteriores já foram implementados. Confira TODOS os arquivos em src/ antes de alterar qualquer coisa.

CONTEXTO OBRIGATÓRIO — LEIA ANTES DE QUALQUER AÇÃO:
1. Leia C:\Users\teste.5\projetos\ia\SPEC.md — seção 2.5 "Micro-interações Distintivas" (5 itens obrigatórios).
2. Leia C:\Users\teste.5\projetos\ia\SPEC.md — seção 2.5 "Estados Interativos" e "Feedback Visual".
3. Leia C:\Users\teste.5\projetos\ia\SPEC.md — seção 1.4 (Clean Code + SOLID).
4. Leia C:\Users\teste.5\projetos\ia\CLAUDE.md — regras obrigatórias.
5. Leia C:\Users\teste.5\projetos\ia\frontend\src\app\globals.css — keyframes existentes.
6. Leia TODOS os componentes em src/components/ — entender o que existe antes de polir.

ESTE SPRINT NÃO CRIA COMPONENTES NOVOS. Polir os existentes.

IMPLEMENTAR:

1. BORDA GRADIENTE NO INPUT (ChatInput.tsx)
   - CSS pseudo-element ou background animado: 2s loop, gradiente percorre contorno.
   - Verificar que já está aplicado no foco. Se não, adicionar.

2. HOVER EM TODOS OS CARDS INTERATIVOS
   - transition: all 200ms cubic-bezier(0.4, 0, 0.2, 1)
   - hover: translateY(-4px) + box-shadow: var(--shadow-neural)
   - Verificar e aplicar em: TaskItem, AgendaEventItem, cards ChatEmpty, itens conversa LeftSidebar.

3. FADE-SLIDE-UP NAS MENSAGENS
   - Keyframe fade-slide-up existe em globals.css.
   - Aplicar animation: fade-slide-up 0.3s ease-out apenas na ÚLTIMA mensagem adicionada.
   - Não re-animar todas ao scroll.

4. PULSO DE BORDA NO ENVIO
   - Quando user envia mensagem: borda do ChatWindow faz flash left→right, 0.6s, uma vez.
   - Implementar via classe CSS temporária + setTimeout para remover.

5. SMART SCROLL (ChatMessageList.tsx)
   - Auto-scroll com behavior:'smooth' quando messages[] muda.
   - Se usuário rolou para cima (scrollTop + clientHeight < scrollHeight - 100): NÃO forçar scroll.
   - useRef no ScrollArea + onScroll handler para rastrear posição.

6. PROTEÇÃO DE PERFORMANCE (ChatMessageList.tsx)
   - messages.length > 100: renderizar apenas os últimos 100.
   - Banner discreto no topo: "Mostrando últimas 100 mensagens" em text-xs muted-foreground.

7. TOASTS DE FEEDBACK
   - Verificar se shadcn Toast existe. Se não: implementar simples com estado em page.tsx.
   - Tarefa concluída: "✓ Tarefa marcada como concluída" (verde, 2s)
   - Tarefa criada: "✓ Tarefa adicionada" (verde, 2s)
   - Erro de API: "✗ Erro ao conectar ao servidor" (vermelho, 4s)
   - Conversa deletada: "Conversa removida" (neutro, 2s)

8. ERRO NO CHAT COM RETRY
   - status='error': última mensagem assistant exibe conteúdo do erro + botão "Tentar novamente".
   - Botão re-envia última mensagem user via sendMessage.
   - Estilo: borda academic-red no GlassCard + ícone ⚠.

9. VERIFICAÇÃO FINAL
   - npx tsc --noEmit → zero erros.
   - npm run build → completa sem erros.
   - DevTools Console com backend rodando → zero warnings, zero errors.
   - Testar todos os estados: ChatEmpty → loading → streaming → idle → erro → retry.

CRITÉRIO DE CONCLUSÃO:
1. npm run build limpo. Zero 'any'. Zero warnings no console.
2. Todas as 5 micro-interações da SPEC 2.5 implementadas.
3. Toasts funcionam para os 4 eventos.
4. Smart scroll: segue ao fundo, para se rolou para cima.
5. Botão "Tentar novamente" funciona.
6. Banner >100 mensagens aparece.

Atualizar MEMORY.md:
| Fase 6 — Sprint 6 (Polish + Erros) | ✅ Concluída | Hover cards, borda gradiente input, fade-slide-up, pulso envio, smart scroll, proteção >100 msgs, toasts (4 eventos), retry em erro SSE. npm run build limpo. |
| Fase 6 — Frontend Next.js | ✅ Concluída | Sprints 0–6 implementados. Chat SSE + typewriter, agenda/tarefas via REST, conversas localStorage (DIP), animações + polish. T1 completo. |

Não pergunte, implemente.
```

---

## ENDPOINTS DO BACKEND — Referência Rápida

| Método | Rota | Params / Body | Retorno | Observação |
|---|---|---|---|---|
| POST | /api/chat | body: {messages[]} | SSE: 1 token + done | Resposta inteira em 1 evento |
| GET | /api/agenda | ?tipo=, ?data=YYYY-MM-DD | list[EventoRead] | NÃO aceita ?periodo= |
| POST | /api/agenda | body: EventoCreate | EventoRead | |
| GET | /api/tasks | ?status=pendente\|concluida, ?disciplina= | list[TarefaRead] | Sem param = todas |
| POST | /api/tasks | body: TarefaCreate | TarefaRead | |
| PATCH | /api/tasks/{id}/concluir | — | TarefaRead | 409 se já concluída |

CORS: `http://localhost:3000` liberado.
Typewriter: simulado no frontend (15ms/2chars). Refatorar para streaming real no T2.

---

## CHECKLIST FINAL — Trabalho 1 Frontend

- [ ] npm run build sem erros TypeScript
- [ ] Layout 3 colunas 20/60/20 em 1440px
- [ ] Chat envia → SSE → typewriter progressivo → cursor some → idle
- [ ] NeuralPulse durante loading
- [ ] Neural Bubble (user) e Glass Card (assistant) com estilos corretos
- [ ] Markdown renderizado (react-markdown + remark-gfm)
- [ ] Agenda: mini-cal + eventos via GET /api/agenda?data=
- [ ] Tarefas: lista via GET /api/tasks
- [ ] Checkbox: PATCH /api/tasks/{id}/concluir + otimistic update
- [ ] Tela vazia com 3 sugestões clicáveis que disparam chat
- [ ] Conversas na sidebar esquerda (localStorage com DIP)
- [ ] "Nova Conversa" limpa e cria nova entrada
- [ ] Toasts de feedback (concluir, criar, erro)
- [ ] Retry quando SSE falha
- [ ] Smart scroll implementado
- [ ] devIndicators: false em next.config.ts
- [ ] Tokens via @theme no globals.css (Tailwind v4)
- [ ] Zero any no TypeScript
