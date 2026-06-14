# SPEC.md — Especificação Técnica Completa — JARVIS Acadêmico

---

## 1. VISÃO GERAL DO PROJETO

### 1.1 Objetivo

Desenvolver um assistente pessoal acadêmico (JARVIS) capaz de ajudar estudantes a organizar e melhorar seu desempenho utilizando técnicas modernas de Inteligência Artificial, integrando:

- **RAG** (Retrieval-Augmented Generation) para consulta a materiais de estudo
- **Tool Calling** para execução de ferramentas especializadas
- **LLM** Gemma 12B como motor de raciocínio e decisão
- **Funcionalidades de Aprendizado** para apoio ativo ao estudante

### 1.2 Princípios de Arquitetura

O sistema segue o padrão **Agent-First Architecture**:

1. A LLM (Gemma 12B) recebe a mensagem do usuário + histórico de conversa
2. A LLM decide autonomamente quais ferramentas chamar (ou nenhuma)
3. O backend executa as ferramentas solicitadas e retorna os resultados
4. A LLM processa os resultados e decide se precisa de mais ferramentas ou se pode gerar a resposta final
5. O ciclo se repete até a LLM produzir uma resposta final sem novas chamadas de ferramenta

**Regra crítica:** O frontend NUNCA chama a API do Gemma diretamente. Toda comunicação passa pelo orquestrador no FastAPI.

### 1.3 Entregas do Projeto

**Trabalho 1 (Entrega Parcial):**
- Funcionalidade 3.1: Consulta a materiais de estudo (RAG)
- Funcionalidade 3.2: Agenda acadêmica
- Funcionalidade 3.3: Lista de tarefas

**Trabalho 2 (Entrega Final):**
- Funcionalidade 3.4: Planejamento de estudos
- Melhorias de aprendizado (mínimo 2, sendo 1 interativa)
- Avaliação do sistema (mínimo 10 perguntas)
- Análise de erros (mínimo 3 falhas documentadas)

### 1.4 Princípios de Desenvolvimento de Código

O código produzido deve seguir rigorosamente os princípios de **Clean Code** e **SOLID**:

#### Clean Code
- **Nomes significativos:** Variáveis, funções e classes com nomes que expressem claramente sua intenção (ex: `calcular_prazo_entrega()` em vez de `calc()`)
- **Funções pequenas:** Máximo de 20 linhas por função; cada função faz apenas uma coisa
- **Evitar duplicação:** DRY (Don't Repeat Yourself) — extrair código repetido para funções reutilizáveis
- **Comentários apenas quando necessário:** Código auto-explicativo é preferível; comentar apenas lógica complexa inevitável
- **Formatação consistente:** Seguir PEP 8 (Python) e ESLint/Prettier (TypeScript)
- **Tratamento de erros explícito:** Nunca usar `except: pass`; sempre logar e tratar erros adequadamente

#### Princípios SOLID

**S — Single Responsibility Principle (Responsabilidade Única)**
- Cada classe/módulo tem apenas uma razão para mudar
- Exemplo: `RAGService` cuida apenas de RAG; não mistura lógica de banco de dados

**O — Open/Closed Principle (Aberto/Fechado)**
- Aberto para extensão, fechado para modificação
- Usar abstrações (protocolos/interfaces) para permitir novos comportamentos sem alterar código existente
- Exemplo: Novas ferramentas devem ser adicionadas ao `TOOLS_REGISTRY` sem modificar `OrquestradorLLM`

**L — Liskov Substitution Principle (Substituição de Liskov)**
- Subtipos devem ser substituíveis por seus tipos base
- Garantir que implementações concretas respeitem contratos de interfaces/abstrações

**I — Interface Segregation Principle (Segregação de Interface)**
- Clientes não devem depender de interfaces que não usam
- Criar interfaces específicas em vez de uma interface geral monolítica
- Exemplo: Separar `BaseToolProtocol` de `AsyncToolProtocol` se necessário

**D — Dependency Inversion Principle (Inversão de Dependência)**
- Depender de abstrações, não de implementações concretas
- Usar injeção de dependências via `Depends()` no FastAPI
- Exemplo: `OrquestradorLLM` recebe `LLMClient` abstrato, não instância fixa de `GemmaClient`

#### Aplicação no Frontend

**Os princípios acima aplicam-se igualmente ao código TypeScript/React:**
- Componentes com responsabilidade única (ex: `ChatMessage` apenas renderiza, não gerencia estado global)
- Hooks customizados para lógica reutilizável (`useChat`, `useSSE`)
- Props tipadas com interfaces TypeScript explícitas
- Separação clara: componentes de UI (`Button`, `Card`) não contêm lógica de negócio
- Tratamento de erros em chamadas async/await com feedback visual ao usuário

#### Estrutura de Código Recomendada

```python
# ✅ BOM: Responsabilidade única, nome claro, tratamento de erros
async def buscar_chunks_relevantes(
    query: str, 
    top_k: int, 
    embedding_service: EmbeddingService
) -> list[DocumentChunk]:
    """Recupera os top-k chunks mais relevantes para a query."""
    try:
        query_vector = await embedding_service.embed(query)
        chunks = await self.index.search(query_vector, k=top_k)
        logger.info(f"Recuperados {len(chunks)} chunks para query: {query[:50]}")
        return chunks
    except Exception as e:
        logger.error(f"Erro ao buscar chunks: {e}", exc_info=True)
        raise

# ❌ RUIM: Nome vago, múltiplas responsabilidades, erro silencioso
def process(q, k):
    try:
        v = embed(q)
        c = search(v, k)
        save_to_db(c)  # Mistura recuperação com persistência
        return c
    except:
        pass  # Erro ignorado
```

#### Code Review Checklist
Antes de finalizar qualquer módulo, verificar:
- [ ] Funções com no máximo 20 linhas
- [ ] Zero duplicação de código
- [ ] Todas as exceções tratadas e logadas
- [ ] Nomes de variáveis/funções auto-explicativos
- [ ] Cada classe tem responsabilidade única
- [ ] Dependências injetadas (não instanciadas internamente)
- [ ] Código testável (sem lógica acoplada a I/O)

---

## 2. ARQUITETURA GERAL

### 2.1 Diagrama de Fluxo

```
┌──────────────────────────────────────────────────────────────────────┐
│                     FRONTEND (Next.js 14 + React)                    │
│                                                                      │
│  ChatUI ──► useChat hook ──► API Client (fetch SSE)                  │
└─────────────────────────────────────┬────────────────────────────────┘
                                      │ HTTP POST /api/chat
                                      │ Server-Sent Events (streaming)
                                      ▼
┌──────────────────────────────────────────────────────────────────────┐
│                      BACKEND (FastAPI + Python 3.11+)                │
│                                                                      │
│  POST /api/chat                                                      │
│    └──► OrquestradorLLM (Agent Loop)                                 │
│           │                                                          │
│           │  WHILE True:                                             │
│           │    1. Monta messages[] + tools[] schemas                 │
│           │    2. Chama Gemma 12B via OpenAI SDK                     │
│           │    3. SE tool_calls → executa ferramentas                │
│           │    4. SE resposta final → retorna via SSE                │
│           │                                                          │
│           ▼                                                          │
│         Tool Router                                                  │
│           ├──► consultar_agenda   ──► SQLite (eventos)               │
│           ├──► listar_tarefas     ──► SQLite (tarefas)               │
│           ├──► adicionar_tarefa   ──► SQLite (tarefas)               │
│           ├──► concluir_tarefa    ──► SQLite (tarefas)               │
│           └──► buscar_material_rag                                   │
│                    └──► EmbeddingService (MiniLM-L12-v2)             │
│                             └──► FAISS Index (top-k chunks)          │
│                                                                      │
│  Logger (Dual Output)                                                │
│    ├──► logs/tool_calls.jsonl  (JSON estruturado)                    │
│    └──► stdout  (terminal colorido)                                  │
│                                                                      │
└──────────────────────────────────────────────────────────────────────┘
                                      │
                                      ▼
┌──────────────────────────────────────────────────────────────────────┐
│                    SERVIÇO EXTERNO — Gemma 12B                       │
│  Endpoint : https://llm.liaufms.org/v1/gemma-3-12b-it               │
│  Model    : google/gemma-3-12b-it                                    │
│  Protocolo: OpenAI-compatible (chat.completions.create)              │
│  Recebe   : messages[] + tools[]                                     │
│  Retorna  : texto OU tool_calls[]                                    │
└──────────────────────────────────────────────────────────────────────┘
```

### 2.2 Stack Tecnológico

| Camada | Tecnologia | Justificativa |
|---|---|---|
| Frontend | Next.js 14 + React 18 | App Router, SSR, streaming nativo |
| Estilização | Tailwind CSS v4 | Utilitário, produtividade |
| Backend | FastAPI + Python 3.11+ | Assíncrono, Pydantic, OpenAPI |
| LLM | Gemma 12B via OpenAI SDK | Modelo obrigatório do edital |
| Embeddings | sentence-transformers/paraphrase-multilingual-MiniLM-L12-v2 | Suporte a português |
| Banco Vetorial | FAISS (IndexFlatL2) | In-process, sem dependências externas |
| Banco Relacional | SQLite + SQLAlchemy async + aiosqlite | Local, zero configuração |
| Chunking | LangChain RecursiveCharacterTextSplitter | Split por sentença |
| Logging | Python logging + JSON | Dual output: arquivo + terminal |
| Deploy | Docker + docker-compose | Isolamento e reprodutibilidade |

### 2.3 Padrões de Comunicação

**Frontend → Backend:**
- Request: `POST /api/chat` com body `{ "messages": [...], "stream": true }`
- Response: Server-Sent Events no formato `data: {"type": "token", "content": "..."}\n\n`
- Encerramento: `data: {"type": "done"}\n\n`

**Backend → Gemma 12B:**
- Cliente: `openai.OpenAI(base_url=GEMMA_BASE_URL, api_key=GEMMA_API_KEY)`
- Request: `client.chat.completions.create(model=..., messages=..., tools=...)`
- Response: `choices[0].message` contém `content` (texto) OU `tool_calls[]`

**Backend → FAISS:**
- Input: vetor numpy float32 de shape `(1, 384)` (embedding da query)
- Output: `(distances, indices)` dos top-k vizinhos

**Backend → SQLite:**
- ORM async via SQLAlchemy 2.0 + aiosqlite
- Sessões injetadas via `Depends(get_db)` no FastAPI

### 2.4 Formato do Log de Tool Calling

Cada chamada de ferramenta gera uma linha no arquivo `logs/tool_calls.jsonl`:

```json
{
  "timestamp": "2025-05-23T14:32:01Z",
  "tool": "buscar_material_rag",
  "input": {"query": "regressão logística", "top_k": 5},
  "output": {"chunks": [], "total_recuperado": 5},
  "execution_time_ms": 234,
  "sucesso": true,
  "erro": null
}
```

### 2.5 Design System Frontend
 
**Conceito Visual:** "Academic Editorial" — Dark neutro em camadas, tipografia com hierarquia forte, acento violeta usado com economia. Referência: Linear / Vercel / Things. Identidade JARVIS preservada pela família violeta, sem "neon em tudo".
 
> **Nota de implementação:** Esta seção substitui a especificação anterior ("Academic Neural Interface"). O redesign foi decidido em 14/06/2026 para elevar o acabamento visual e evitar estética genérica de "gerado por IA". Nenhuma funcionalidade foi alterada.
 
---
 
#### Tokens de Design
 
**Paleta de Cores — Dark em Camadas**
 
Superfícies (elevação por lightness, não por blur):
- `--bg`: hsl(240 8% 4%) — canvas principal
- `--surface-1`: hsl(240 6% 7%) — cards, sidebars
- `--surface-2`: hsl(240 6% 10%) — inputs, hover, estados levantados
- `--hairline`: hsl(0 0% 100% / 0.06) — borda padrão
- `--border-strong`: hsl(0 0% 100% / 0.12) — borda com ênfase
Texto:
- `--fg`: hsl(0 0% 96%) — texto principal
- `--fg-muted`: hsl(240 5% 65%) — texto secundário (≥4.5:1 contraste)
- `--fg-subtle`: hsl(240 5% 48%) — metadados, labels (≥3:1, uso parcimonioso)
Acento único (família violeta, sem neon):
- `--accent`: hsl(255 85% 68%) — acento principal
- `--accent-soft`: hsl(255 85% 68% / 0.12) — fundo de estado ativo
- Gradiente roxo→azul: **apenas** no wordmark e CTA primário
Cores semânticas (usadas como dots/labels pequenos, não como preenchimentos grandes):
- `--semantic-yellow`: hsl(45 93% 58%) — prazo próximo
- `--semantic-green`: hsl(142 76% 36%) — concluído
- `--semantic-red`: hsl(0 72% 51%) — urgente/erro
- `--semantic-blue`: hsl(199 89% 48%) — informacional
Elevação (sombras pretas suaves, sem glow colorido):
- `--shadow-1`: 0 1px 3px rgb(0 0 0 / 0.4)
- `--shadow-2`: 0 4px 12px rgb(0 0 0 / 0.5)
---
 
#### Tipografia — Eixo Editorial
 
Famílias de Fonte:
- `--font-display`: 'Space Grotesk', system-ui — wordmark, títulos grandes
- `--font-sans`: 'Inter Variable', system-ui, sans-serif — corpo, UI, mensagens
- `--font-mono`: 'JetBrains Mono', monospace — código, timestamps, contadores (tabular numbers)
Escala com contraste real:
- display: 2.25–3rem, tracking -0.02em — wordmark, hero
- `text-xl`: 1.375rem (22px), weight 600 — títulos de seção
- `text-base`: 1rem (16px), line-height 1.6 — corpo principal
- `text-sm`: 0.875rem (14px) — corpo secundário
- labels de seção: 11px uppercase, tracking 0.12em, `--fg-subtle`
- timestamps/contadores: JetBrains Mono tabular (evita pulo de layout)
Medida de leitura: máximo ~66ch nas mensagens do chat.
 
---
 
#### Espaçamentos — Ritmo Base 8px
 
- `spacing-1`: 0.5rem (8px)
- `spacing-2`: 1rem (16px)
- `spacing-3`: 1.5rem (24px)
- `spacing-4`: 2rem (32px)
- `spacing-6`: 3rem (48px)
- `spacing-8`: 4rem (64px)
Seções usam tiers 16/24/32px. Sidebars com mais respiro que o design anterior.
 
---
 
#### Border Radius
 
- `radius-sm`: 0.375rem (6px) — badges, dots
- `radius-md`: 0.5rem (8px) — buttons, inputs
- `radius-lg`: 0.75rem (12px) — cards
- `radius-xl`: 1rem (16px) — modais
---
 
#### Componentes — Decisões de Implementação
 
**GradientButton**
- Primário: fill sólido `--accent`, sem gradiente
- Secundário: ghost com `--hairline`
- CTA principal (Nova Conversa): gradiente roxo→azul permitido aqui
**GlassCard**
- Fundo: `--surface-1` sólido (sem backdrop-blur)
- Borda: `--hairline`
- Props e assinatura mantidos para não quebrar usos existentes
**GradientBadge**
- Dot 6px + texto sólido, fundo `--accent-soft`
- Um único estilo (sem variantes translúcidas /20)
**Chat Message — Usuário**
- Background: `--accent` sólido (ou `--surface-2` + borda de acento)
- Border-radius assimétrico no canto de origem
**Chat Message — Assistente**
- Background: `--surface-1` plano, sem blur
- Medida de leitura ~66ch, line-height 1.6
**ChatEmpty**
- Ícones Lucide: BookOpen, CalendarDays, CheckSquare (zero emoji estrutural)
- Cards com `--surface-1` + `--hairline`
**NeuralPulse (loading)**
- 3 dots com `--accent` sólido
- Timing sóbrio (1.4s, ease-in-out)
**Sidebar — Labels de Seção**
- "CONVERSAS", "MATERIAIS", "AGENDA", "TAREFAS": 11px uppercase, `--fg-subtle`
- Estado ativo: `--accent-soft` + barra lateral sólida de 2px em `--accent`
**AgendaMiniCal**
- Dia selecionado: fundo `--accent` sólido
- Hoje: ring fino `--accent`, sem fill
**Ícones**
- Família única: Lucide
- Tamanhos: icon-sm 16px / icon-md 20px
- Stroke consistente (1.5px)
- Zero emoji em elementos estruturais de UI
---
 
#### Animações — Movimento com Propósito
 
**Removidos (loops ambientes):**
- `input-glow-pulse` (2s loop no input)
- `border-gradient-pulse` no header durante streaming
**Mantidos e refinados (disparados por ação):**
- Entrada de mensagem: fade-slide-up, 200ms ease-out, stagger 30–50ms em lista
- Feedback de envio: pulso único (não loop)
- Tarefa concluída: confetti sutil 4–6 partículas, 0.8s (pode ficar mais sóbrio)
- Hover lift: `translateY(-2px)` + `--shadow-2`, 150ms ease-out
- Foco de input: ring `--accent`, transição 150ms
**Easing padrão:** 150–300ms, ease-out na entrada.
 
**Acessibilidade obrigatória:**
```css
@media (prefers-reduced-motion: reduce) {
  *, *::before, *::after {
    animation-duration: 0.01ms !important;
    transition-duration: 0.01ms !important;
  }
}
```
 
---
 
#### Acessibilidade
 
- `aria-label` em todos os botões só-ícone (fechar conversa, enviar, etc.)
- Contraste `--fg-muted` ≥ 4.5:1, `--fg-subtle` ≥ 3:1
- Foco visível consistente em todos os elementos interativos
- Navegação por teclado (Tab, Enter, Esc)
---
 
#### Layout — 3 Colunas (mantido)
 
```
┌────────┬─────────────────────────┬──────────┐
│ NAV    │   CHAT CENTRAL          │ WIDGETS  │
│ 20%    │   60%                   │  20%     │
├────────┼─────────────────────────┼──────────┤
│        │                         │          │
│ JARVIS │  ┌──────────────────┐   │ AGENDA   │
│ ─────  │  │ User Message     │   │ ──────── │
│ Chats  │  │ [accent sólido]  │   │ eventos  │
│ ─────  │  └──────────────────┘   │          │
│ Materiais  ┌──────────────────┐   │ TAREFAS  │
│        │  │ AI Response      │   │ ──────── │
│        │  │ [surface-1 plano]│   │ itens    │
│        │  └──────────────────┘   │          │
│        │  [Input + hairline]     │          │
└────────┴─────────────────────────┴──────────┘
```
 
Proporções idênticas ao design anterior. Apenas tokens, espaçamento e natureza das animações mudam.
 
---
 
#### Breakpoints (mantidos)
 
- 1280px: HD — Sidebars 18%, Chat 64%
- 1440px: Full HD — Sidebars 20%, Chat 60% (padrão)
- 1920px: Full HD — Sidebars 22%, Chat 56%
- 2560px+: Max-width 2200px centralizado

## 3. ESTRUTURA DE DIRETÓRIOS

```
jarvis-academico/
│
├── README.md                          # Instruções de instalação + IAs utilizadas
├── SPEC.md                            # Este arquivo
├── docker-compose.yml
├── Dockerfile.frontend
├── Dockerfile.backend
├── .dockerignore
├── .gitignore
│
├── frontend/
│   ├── public/
│   │   └── favicon.ico
│   └── src/
│       ├── app/
│       │   ├── layout.tsx             # Layout raiz
│       │   ├── page.tsx               # Página inicial (ChatUI)
│       │   └── globals.css
│       ├── components/
│       │   ├── chat/
│       │   │   ├── ChatWindow.tsx     # Container do chat
│       │   │   ├── ChatMessage.tsx    # Mensagem individual (user/assistant)
│       │   │   └── ChatInput.tsx      # Textarea + botão enviar
│       │   ├── agenda/
│       │   │   └── AgendaCard.tsx     # Card de evento
│       │   ├── tasks/
│       │   │   ├── TaskList.tsx
│       │   │   └── TaskItem.tsx
│       │   └── ui/
│       │       ├── Button.tsx
│       │       ├── Card.tsx
│       │       └── Spinner.tsx
│       ├── hooks/
│       │   ├── useChat.ts             # Gerencia estado do chat
│       │   └── useSSE.ts              # Conecta Server-Sent Events
│       ├── lib/
│       │   ├── api.ts                 # Wrapper fetch para o backend
│       │   └── utils.ts
│       └── types/
│           ├── chat.ts
│           └── api.ts
│   ├── next.config.ts
│   ├── tailwind.config.ts
│   ├── tsconfig.json
│   └── package.json
│
├── backend/
│   ├── app/
│   │   ├── main.py                    # Instância FastAPI + CORS + routers
│   │   ├── api/
│   │   │   └── routes/
│   │   │       ├── __init__.py
│   │   │       ├── chat.py            # POST /api/chat (SSE)
│   │   │       ├── agenda.py          # CRUD /api/agenda
│   │   │       └── tasks.py           # CRUD /api/tasks
│   │   ├── core/
│   │   │   ├── __init__.py
│   │   │   ├── config.py              # pydantic-settings + variáveis de ambiente
│   │   │   └── database.py            # Engine SQLite + session factory async
│   │   ├── models/
│   │   │   ├── __init__.py
│   │   │   ├── evento.py              # SQLAlchemy ORM — tabela eventos
│   │   │   └── tarefa.py              # SQLAlchemy ORM — tabela tarefas
│   │   ├── schemas/
│   │   │   ├── __init__.py
│   │   │   ├── chat.py                # ChatRequest, ChatResponse
│   │   │   ├── evento.py              # EventoCreate, EventoRead, EventoUpdate
│   │   │   └── tarefa.py              # TarefaCreate, TarefaRead, TarefaUpdate
│   │   ├── services/
│   │   │   ├── __init__.py
│   │   │   ├── llm_client.py          # Cliente OpenAI aponta para Gemma 12B
│   │   │   ├── orchestrator.py        # Agent loop + tool dispatch
│   │   │   ├── rag_service.py         # Chunking, embedding, FAISS
│   │   │   ├── agenda_service.py      # CRUD de eventos
│   │   │   ├── task_service.py        # CRUD de tarefas
│   │   │   └── learning_service.py    # Exercícios + active recall
│   │   ├── tools/
│   │   │   ├── __init__.py            # TOOLS_REGISTRY[] com as 5 tools
│   │   │   ├── base.py                # Classe base Tool
│   │   │   ├── consultar_agenda.py
│   │   │   ├── listar_tarefas.py
│   │   │   ├── adicionar_tarefa.py
│   │   │   ├── concluir_tarefa.py
│   │   │   └── buscar_material_rag.py
│   │   └── utils/
│   │       ├── __init__.py
│   │       └── logger.py              # JSON + terminal (dual output)
│   ├── data/
│   │   ├── README.md                  # Origem, tipo, limitações, chunking
│   │   ├── documents/                 # ≥ 10 PDFs/TXTs originais
│   │   │   └── *.pdf / *.txt
│   │   ├── processed/
│   │   │   └── chunks_metadata.json   # Gerado automaticamente no startup
│   │   └── faiss_index.bin            # Índice FAISS persistido
│   ├── logs/
│   │   └── tool_calls.jsonl
│   ├── tests/
│   │   ├── __init__.py
│   │   ├── test_tools.py
│   │   ├── test_rag.py
│   │   ├── test_orchestrator.py
│   │   └── test_learning.py
│   ├── requirements.txt
│   └── .env.example
│
└── evaluation/
    ├── questions.json                 # 10+ perguntas com gabarito
    ├── results.json                   # Respostas geradas + classificação
    ├── error_analysis.md              # 3+ falhas documentadas
    └── evaluate.py                    # Script de avaliação automatizado
```

---

## 4. CONTRATOS DE TOOL CALLING

### 4.1 Visão Geral do Registro

Todas as 5 tools são registradas em `backend/app/tools/__init__.py` no array `TOOLS_REGISTRY[]`, no formato exigido pelo protocolo OpenAI (`tools[]` do `chat.completions.create`).

A LLM (Gemma 12B) lê os schemas e decide **autonomamente** qual tool chamar. O backend valida o input com Pydantic antes de executar a função. Não há lógica fixa de despacho — a decisão é sempre da LLM.

---

### 4.2 Tool 1 — `consultar_agenda`

**Quando a LLM deve chamar:** usuário pergunta sobre aulas, provas, compromissos ou o que tem em um período. Exemplos: "o que tenho hoje?", "tenho prova amanhã?", "quais minhas aulas esta semana?".

#### Input Schema (registrado no TOOLS_REGISTRY)

```json
{
  "name": "consultar_agenda",
  "description": "Consulta eventos da agenda acadêmica. Use quando o usuário perguntar sobre aulas, provas, compromissos ou o que tem em um período específico. Exemplos: 'o que tenho hoje?', 'tenho prova amanhã?', 'quais minhas aulas esta semana?'.",
  "parameters": {
    "type": "object",
    "properties": {
      "periodo": {
        "type": "string",
        "enum": ["hoje", "amanha", "semana", "mes"],
        "description": "Período relativo de consulta. 'hoje' = dia atual, 'amanha' = próximo dia, 'semana' = próximos 7 dias, 'mes' = próximos 30 dias."
      },
      "data_inicio": {
        "type": "string",
        "description": "Data de início no formato YYYY-MM-DD. Ignorado se 'periodo' for informado."
      },
      "data_fim": {
        "type": "string",
        "description": "Data de fim no formato YYYY-MM-DD. Opcional. Usado junto com 'data_inicio' para intervalos customizados."
      }
    },
    "oneOf": [
      {"required": ["periodo"]},
      {"required": ["data_inicio"]}
    ]
  }
}
```

#### Output Schema (retornado ao orquestrador como tool_result)

```json
{
  "type": "object",
  "properties": {
    "eventos": {
      "type": "array",
      "description": "Lista de eventos no período consultado, ordenados por data/hora.",
      "items": {
        "type": "object",
        "properties": {
          "id":          { "type": "string", "format": "uuid" },
          "titulo":      { "type": "string", "description": "Ex: 'Aula de IA', 'Prova de Estatística'." },
          "descricao":   { "type": "string", "nullable": true },
          "data":        { "type": "string", "format": "date", "description": "YYYY-MM-DD" },
          "hora_inicio": { "type": "string", "description": "HH:MM (24h). Null se não definida.", "nullable": true },
          "hora_fim":    { "type": "string", "description": "HH:MM (24h). Null se não definida.", "nullable": true },
          "tipo":        { "type": "string", "enum": ["aula", "prova", "prazo", "outro"] },
          "local":       { "type": "string", "nullable": true, "description": "Ex: 'Sala 301', 'Google Meet'." }
        },
        "required": ["id", "titulo", "data", "tipo"]
      }
    },
    "total":             { "type": "integer", "minimum": 0 },
    "periodo_consultado":{ "type": "string", "description": "Ex: 'Hoje (23/05/2025)'." }
  },
  "required": ["eventos", "total", "periodo_consultado"]
}
```

#### Exemplo completo

**Input da LLM:**
```json
{ "periodo": "hoje" }
```

**Output do backend:**
```json
{
  "eventos": [
    {
      "id": "e8a3c7b2-4f1e-4d9a-b5c6-7e8f9a0b1c2d",
      "titulo": "Aula de Inteligência Artificial",
      "descricao": "Tópico: Redes Neurais Convolucionais",
      "data": "2025-05-23",
      "hora_inicio": "14:00",
      "hora_fim": "16:00",
      "tipo": "aula",
      "local": "Sala 301"
    },
    {
      "id": "f9b4d8c3-5e2f-4e0b-a6d7-8fab0h1i2j3k",
      "titulo": "Prazo: Entrega Trabalho 1 de IA",
      "descricao": null,
      "data": "2025-05-23",
      "hora_inicio": null,
      "hora_fim": "23:59",
      "tipo": "prazo",
      "local": null
    }
  ],
  "total": 2,
  "periodo_consultado": "Hoje (23/05/2025)"
}
```

---

### 4.3 Tool 2 — `listar_tarefas`

**Quando a LLM deve chamar:** usuário pergunta o que tem para fazer, quais tarefas estão pendentes ou concluídas. Exemplos: "o que tenho que fazer?", "quais tarefas de IA faltam?", "mostra minhas tarefas concluídas".

#### Input Schema

```json
{
  "name": "listar_tarefas",
  "description": "Lista tarefas do estudante. Use quando o usuário perguntar o que tem para fazer, quais tarefas estão pendentes ou concluídas. Exemplos: 'o que tenho que fazer?', 'quais tarefas de IA faltam?', 'mostra minhas tarefas concluídas'.",
  "parameters": {
    "type": "object",
    "properties": {
      "status": {
        "type": "string",
        "enum": ["pendente", "concluida", "todas"],
        "default": "pendente",
        "description": "'pendente' retorna apenas não concluídas, 'concluida' apenas concluídas, 'todas' retorna ambas."
      },
      "disciplina": {
        "type": "string",
        "description": "Filtrar por disciplina específica. Opcional. Ex: 'Inteligência Artificial', 'Estatística'. Se omitido, retorna de todas."
      }
    }
  }
}
```

#### Output Schema

```json
{
  "type": "object",
  "properties": {
    "tarefas": {
      "type": "array",
      "items": {
        "type": "object",
        "properties": {
          "id":           { "type": "string", "format": "uuid" },
          "titulo":       { "type": "string" },
          "descricao":    { "type": "string", "nullable": true },
          "disciplina":   { "type": "string", "nullable": true },
          "status":       { "type": "string", "enum": ["pendente", "concluida"] },
          "prazo":        { "type": "string", "format": "date", "nullable": true, "description": "YYYY-MM-DD" },
          "criada_em":    { "type": "string", "format": "date-time", "description": "ISO 8601" },
          "concluida_em": { "type": "string", "format": "date-time", "nullable": true }
        },
        "required": ["id", "titulo", "status", "criada_em"]
      }
    },
    "total": { "type": "integer", "minimum": 0 },
    "filtros_aplicados": {
      "type": "object",
      "properties": {
        "status":     { "type": "string" },
        "disciplina": { "type": "string", "nullable": true }
      }
    }
  },
  "required": ["tarefas", "total", "filtros_aplicados"]
}
```

#### Exemplo completo

**Input da LLM:**
```json
{ "status": "pendente", "disciplina": "Inteligência Artificial" }
```

**Output do backend:**
```json
{
  "tarefas": [
    {
      "id": "a1b2c3d4-e5f6-7890-abcd-ef1234567890",
      "titulo": "Estudar Redes Neurais Convolucionais",
      "descricao": "Revisar conceitos de CNN e fazer exercícios práticos",
      "disciplina": "Inteligência Artificial",
      "status": "pendente",
      "prazo": "2025-05-30",
      "criada_em": "2025-05-20T10:30:00Z",
      "concluida_em": null
    }
  ],
  "total": 1,
  "filtros_aplicados": {
    "status": "pendente",
    "disciplina": "Inteligência Artificial"
  }
}
```

---

### 4.4 Tool 3 — `adicionar_tarefa`

**Quando a LLM deve chamar:** usuário pede para registrar algo a fazer, criar lembrete ou adicionar atividade. Exemplos: "adiciona uma tarefa para estudar capítulo 3", "cria um lembrete para entregar o trabalho".

#### Input Schema

```json
{
  "name": "adicionar_tarefa",
  "description": "Adiciona uma nova tarefa à lista do estudante. Use quando o usuário pedir para registrar algo a fazer, criar um lembrete acadêmico ou adicionar uma atividade. Exemplos: 'adiciona uma tarefa para estudar capítulo 3', 'cria um lembrete para entregar o trabalho'.",
  "parameters": {
    "type": "object",
    "required": ["titulo"],
    "properties": {
      "titulo": {
        "type": "string",
        "minLength": 1,
        "maxLength": 200,
        "description": "Título obrigatório da tarefa. Ex: 'Estudar regressão logística', 'Fazer exercícios da lista 3'."
      },
      "descricao": {
        "type": "string",
        "maxLength": 1000,
        "description": "Descrição detalhada. Opcional."
      },
      "disciplina": {
        "type": "string",
        "maxLength": 100,
        "description": "Disciplina relacionada. Opcional. Ex: 'Inteligência Artificial'."
      },
      "prazo": {
        "type": "string",
        "description": "Data limite no formato YYYY-MM-DD. Opcional."
      }
    }
  }
}
```

#### Output Schema

```json
{
  "type": "object",
  "properties": {
    "sucesso":   { "type": "boolean" },
    "tarefa_id": { "type": "string", "format": "uuid" },
    "mensagem":  { "type": "string", "description": "Ex: 'Tarefa criada com sucesso' ou descrição do erro." },
    "tarefa": {
      "type": "object",
      "description": "Objeto completo da tarefa criada.",
      "properties": {
        "id":           { "type": "string", "format": "uuid" },
        "titulo":       { "type": "string" },
        "descricao":    { "type": "string", "nullable": true },
        "disciplina":   { "type": "string", "nullable": true },
        "status":       { "type": "string", "enum": ["pendente"] },
        "prazo":        { "type": "string", "nullable": true },
        "criada_em":    { "type": "string", "format": "date-time" },
        "concluida_em": { "type": "null" }
      }
    }
  },
  "required": ["sucesso", "tarefa_id", "mensagem"]
}
```

#### Exemplo completo

**Input da LLM:**
```json
{
  "titulo": "Estudar Transformers e Attention Mechanisms",
  "descricao": "Ler paper 'Attention is All You Need' e fazer resumo",
  "disciplina": "Inteligência Artificial",
  "prazo": "2025-06-01"
}
```

**Output do backend:**
```json
{
  "sucesso": true,
  "tarefa_id": "c3d4e5f6-a7b8-9c0d-1e2f-a3b4c5d6e7f8",
  "mensagem": "Tarefa 'Estudar Transformers e Attention Mechanisms' criada com sucesso",
  "tarefa": {
    "id": "c3d4e5f6-a7b8-9c0d-1e2f-a3b4c5d6e7f8",
    "titulo": "Estudar Transformers e Attention Mechanisms",
    "descricao": "Ler paper 'Attention is All You Need' e fazer resumo",
    "disciplina": "Inteligência Artificial",
    "status": "pendente",
    "prazo": "2025-06-01",
    "criada_em": "2025-05-23T15:45:30Z",
    "concluida_em": null
  }
}
```

---

### 4.5 Tool 4 — `concluir_tarefa`

**Quando a LLM deve chamar:** usuário disser que terminou uma tarefa. Exemplos: "terminei os exercícios da lista 3", "marca a tarefa de CNN como concluída".

> **Fluxo obrigatório:** se o usuário não fornecer o UUID diretamente, a LLM deve primeiro chamar `listar_tarefas` para obter o `tarefa_id` correto antes de chamar `concluir_tarefa`.

#### Input Schema

```json
{
  "name": "concluir_tarefa",
  "description": "Marca uma tarefa como concluída. Use quando o usuário disser que terminou uma tarefa. Se o UUID não for conhecido, chame listar_tarefas primeiro para obtê-lo.",
  "parameters": {
    "type": "object",
    "required": ["tarefa_id"],
    "properties": {
      "tarefa_id": {
        "type": "string",
        "format": "uuid",
        "description": "UUID da tarefa a ser marcada como concluída. Obtenha via listar_tarefas se necessário."
      }
    }
  }
}
```

#### Output Schema

```json
{
  "type": "object",
  "properties": {
    "sucesso":      { "type": "boolean" },
    "tarefa_id":    { "type": "string", "format": "uuid" },
    "titulo":       { "type": "string", "description": "Título da tarefa concluída, para confirmação." },
    "mensagem":     { "type": "string" },
    "concluida_em": { "type": "string", "format": "date-time", "description": "Timestamp ISO 8601 de quando foi concluída." }
  },
  "required": ["sucesso", "tarefa_id", "titulo", "mensagem"]
}
```

#### Exemplos completos

**Input da LLM:**
```json
{ "tarefa_id": "c3d4e5f6-a7b8-9c0d-1e2f-a3b4c5d6e7f8" }
```

**Output (sucesso):**
```json
{
  "sucesso": true,
  "tarefa_id": "c3d4e5f6-a7b8-9c0d-1e2f-a3b4c5d6e7f8",
  "titulo": "Estudar Transformers e Attention Mechanisms",
  "mensagem": "Tarefa marcada como concluída com sucesso",
  "concluida_em": "2025-05-23T16:20:15Z"
}
```

**Output (erro — tarefa não encontrada):**
```json
{
  "sucesso": false,
  "tarefa_id": "c3d4e5f6-a7b8-9c0d-1e2f-a3b4c5d6e7f8",
  "titulo": "",
  "mensagem": "Erro: Tarefa não encontrada ou já está concluída",
  "concluida_em": null
}
```

---

### 4.6 Tool 5 — `buscar_material_rag`

**Quando a LLM deve chamar:** usuário fizer perguntas sobre conteúdo acadêmico, conceitos, teorias ou quiser explicações. Exemplos: "explique regressão logística", "o que são embeddings?", "resuma o conteúdo sobre redes neurais".

#### Input Schema

```json
{
  "name": "buscar_material_rag",
  "description": "Busca trechos de materiais de estudo usando RAG. Use quando o usuário fizer perguntas sobre conteúdo acadêmico, conceitos ou teorias. Exemplos: 'explique regressão logística', 'o que são embeddings?', 'resuma redes neurais'.",
  "parameters": {
    "type": "object",
    "required": ["query"],
    "properties": {
      "query": {
        "type": "string",
        "minLength": 3,
        "maxLength": 500,
        "description": "Pergunta ou tema a ser buscado. Ex: 'regressão logística', 'como funcionam redes convolucionais'."
      },
      "top_k": {
        "type": "integer",
        "default": 5,
        "minimum": 1,
        "maximum": 20,
        "description": "Número máximo de chunks a retornar. Use 3-5 para respostas objetivas, 10-15 para análises abrangentes."
      },
      "documento": {
        "type": "string",
        "description": "Nome do arquivo para filtrar a busca. Opcional. Ex: 'apostila_ia_01.pdf'. Se omitido, busca em todos."
      },
      "threshold": {
        "type": "number",
        "minimum": 0.0,
        "maximum": 1.0,
        "default": 0.0,
        "description": "Score mínimo de similaridade. 0.0 = sem filtro. Use 0.5-0.7 para filtrar resultados pouco relevantes."
      }
    }
  }
}
```

#### Output Schema

```json
{
  "type": "object",
  "properties": {
    "chunks": {
      "type": "array",
      "description": "Chunks recuperados, ordenados por score decrescente.",
      "items": {
        "type": "object",
        "properties": {
          "conteudo":    { "type": "string", "description": "Texto do trecho recuperado." },
          "fonte":       { "type": "string", "description": "Nome do arquivo de origem. Ex: 'apostila_ia_01.pdf'." },
          "pagina":      { "type": "integer", "nullable": true, "description": "Página do documento. Null para TXT/MD." },
          "chunk_index": { "type": "integer", "description": "Índice sequencial do chunk no documento (0-based)." },
          "score": {
            "type": "number",
            "minimum": 0.0,
            "maximum": 1.0,
            "description": "Score de similaridade cossenoidal. Próximo de 1.0 = alta relevância."
          },
          "metadata": {
            "type": "object",
            "additionalProperties": true,
            "description": "Metadados extras: autor, seção, data, etc."
          }
        },
        "required": ["conteudo", "fonte", "chunk_index", "score"]
      }
    },
    "query":            { "type": "string", "description": "Query original processada." },
    "total_recuperado": { "type": "integer", "minimum": 0 },
    "tempo_busca_ms":   { "type": "number", "description": "Tempo de execução em milissegundos." }
  },
  "required": ["chunks", "query", "total_recuperado"]
}
```

#### Exemplo completo

**Input da LLM:**
```json
{
  "query": "como funcionam redes neurais convolucionais",
  "top_k": 3,
  "threshold": 0.6
}
```

**Output do backend:**
```json
{
  "chunks": [
    {
      "conteudo": "Redes Neurais Convolucionais (CNNs) são arquiteturas especializadas em processar dados com estrutura de grade, como imagens. A operação fundamental é a convolução, que aplica filtros aprendíveis para detectar características locais como bordas, texturas e formas.",
      "fonte": "apostila_ia_01.pdf",
      "pagina": 42,
      "chunk_index": 127,
      "score": 0.89,
      "metadata": { "secao": "Capítulo 5 - Deep Learning" }
    },
    {
      "conteudo": "As CNNs utilizam três tipos principais de camadas: convolucionais (extraem features), pooling (reduzem dimensionalidade) e fully-connected (classificação final). A arquitetura típica segue: CONV → ReLU → POOL → FC → Softmax.",
      "fonte": "apostila_ia_01.pdf",
      "pagina": 43,
      "chunk_index": 128,
      "score": 0.85,
      "metadata": { "secao": "Capítulo 5 - Deep Learning" }
    },
    {
      "conteudo": "Arquiteturas clássicas de CNNs incluem LeNet (1998), AlexNet (2012), VGG (2014) e ResNet (2015). A ResNet introduziu conexões residuais (skip connections), permitindo treinar redes muito profundas sem sofrer com vanishing gradient.",
      "fonte": "tutorial_cnn_avancado.pdf",
      "pagina": 8,
      "chunk_index": 23,
      "score": 0.78,
      "metadata": { "secao": "Evolução das Arquiteturas" }
    }
  ],
  "query": "como funcionam redes neurais convolucionais",
  "total_recuperado": 3,
  "tempo_busca_ms": 42.3
}
```

---

## 5. FLUXO DE RAG

### 5.1 Pipeline — Fase 1: Indexação (executa no startup do backend)

```
PASSO 1 — CARREGAMENTO
  ├─ Lê todos os arquivos de /backend/data/documents/
  ├─ Suporta: PDF (PyPDF2), TXT, MD
  └─ Output: lista de objetos Document {conteudo, fonte, pagina}

PASSO 2 — CHUNKING
  ├─ Método: LangChain RecursiveCharacterTextSplitter
  ├─ chunk_size   : 800 caracteres
  ├─ chunk_overlap: 100 caracteres
  ├─ separators   : ["\n\n", "\n", ". ", " ", ""]
  └─ Output: lista de chunks com metadata {fonte, pagina, chunk_index}

PASSO 3 — EMBEDDING
  ├─ Modelo: sentence-transformers/paraphrase-multilingual-MiniLM-L12-v2
  ├─ Dimensão do vetor: 384
  ├─ Device: CPU
  └─ Output: array numpy float32 de shape (n_chunks, 384)

PASSO 4 — ÍNDICE FAISS
  ├─ Index type: IndexFlatL2 (busca exaustiva)
  ├─ Adiciona todos os embeddings
  ├─ Persiste em: /backend/data/faiss_index.bin
  └─ Salva metadata em: /backend/data/processed/chunks_metadata.json
```

### 5.2 Pipeline — Fase 2: Recuperação (executa a cada chamada de buscar_material_rag)

```
PASSO 5 — EMBEDDING DA QUERY
  ├─ Recebe query (string)
  ├─ Gera embedding com o mesmo modelo (384 dims)
  └─ Normaliza vetor L2

PASSO 6 — BUSCA FAISS
  ├─ index.search(query_embedding, top_k)
  └─ Retorna (distances[], indices[])

PASSO 7 — MONTAGEM DO RESULTADO
  ├─ Recupera chunks via indices[]
  ├─ Calcula score: 1 / (1 + distance)
  ├─ Aplica threshold (descarta score < threshold)
  └─ Ordena por score decrescente

PASSO 8 — RETORNO
  └─ JSON com chunks, fontes, páginas, scores, tempo_busca_ms
```

### 5.3 Justificativa das Escolhas de Chunking

| Parâmetro | Valor | Justificativa |
|---|---|---|
| chunk_size | 800 chars | Captura 1-2 parágrafos completos. Chunks menores (< 400) perdem contexto; maiores (> 1500) diluem relevância. |
| chunk_overlap | 100 chars | ~12.5% de overlap garante que conceitos na fronteira entre chunks não sejam perdidos. |
| Separadores | `\n\n, \n, ". "` | Prioriza quebras naturais (parágrafo > sentença > palavra) para manter coerência semântica. |
| Modelo de embedding | paraphrase-multilingual-MiniLM-L12-v2 | Suporta português nativamente; 384 dims = trade-off qualidade × velocidade. |
| FAISS IndexFlatL2 | — | Busca exaustiva (100% recall). Dataset pequeno (~1200 chunks) não exige ANN aproximado. |

### 5.4 Dataset — Especificação Obrigatória

**Localização:** `/backend/data/`

**Requisitos mínimos (edital):**
- ≥ 10 documentos
- Conteúdo acadêmico de qualidade suficiente para perguntas
- `/backend/data/README.md` com: origem, tipo, limitações, estratégia de chunking e impacto no RAG

**Conteúdo obrigatório do `/backend/data/README.md`:**

```markdown
# Dataset — Materiais de Estudo de IA/ML

## 1. Origem dos Dados
- Fonte: [descrever]
- Critério de seleção: [descrever]
- Licença: [descrever]
- Data de coleta: [descrever]

## 2. Tipo de Conteúdo
- Domínio: Inteligência Artificial e Machine Learning
- Tópicos cobertos: [listar]
- Formatos: [ex: 10 PDFs, 3 TXTs]
- Volume total: [ex: ~500 páginas, ~2MB]

## 3. Limitações Conhecidas
- [listar limitações: idioma, atualização, cobertura, qualidade de OCR, etc.]

## 4. Estratégia de Chunking
- Método: RecursiveCharacterTextSplitter (LangChain)
- chunk_size: 800 caracteres
- chunk_overlap: 100 caracteres
- Separadores: ["\n\n", "\n", ". ", " ", ""]
- Justificativa: [explicar por que esses valores foram escolhidos]

## 5. Impacto no RAG
- Vantagens: [ex: contexto suficiente, busca precisa]
- Desvantagens: [ex: fragmentação de conceitos longos]
- Alternativas consideradas: [ex: chunks de 400 chars — por que descartado]
```

---

## 6. FUNCIONALIDADES DE APRENDIZADO

O edital exige **mínimo 2 funcionalidades**, sendo **pelo menos 1 interativa** (o sistema pergunta e avalia a resposta do estudante).

### 6.1 Funcionalidade 1 — Geração de Exercícios (não-interativa)

**Trigger:** usuário pede "gere exercícios sobre X" ou "crie questões de Y".

**Fluxo:**
1. Sistema chama `buscar_material_rag(query=topico, top_k=10)`
2. Monta prompt com os chunks recuperados
3. Envia para Gemma 12B com instrução para gerar questões de múltipla escolha
4. Retorna exercícios formatados

**Prompt template para Gemma 12B:**
```
Com base nestes trechos sobre {topico}:

{chunks_recuperados}

Gere 3 questões de múltipla escolha com 4 alternativas cada.
Formato:
1. [Enunciado]
   a) [Alternativa A]
   b) [Alternativa B]
   c) [Alternativa C]
   d) [Alternativa D]
   Resposta correta: [letra]
   Explicação: [por que essa é a resposta correta]
```

**Critérios de qualidade:**
- Questões baseadas diretamente no conteúdo recuperado via RAG (nunca inventadas)
- Alternativas incorretas devem ser plausíveis
- Cada questão cobre um conceito diferente do tópico
- Inclui resposta correta + explicação breve

---

### 6.2 Funcionalidade 2 — Active Recall Interativo (interativa)

**Trigger:** usuário pede "me teste sobre X" ou "quero praticar Y".

**Fluxo de interação:**
```
Sistema  → "Vamos testar seu conhecimento sobre {tópico}. Pronto?"
Usuário  → "Sim"
Sistema  → [Faz pergunta baseada no material]
Usuário  → [Responde]
Sistema  → [Avalia resposta e dá feedback construtivo]
Sistema  → "Quer tentar outra pergunta?"
[loop até o usuário encerrar]
```

**Prompt de avaliação para Gemma 12B:**
```
Pergunta feita ao estudante: {pergunta}
Resposta esperada (baseada no material): {resposta_referencia}
Resposta do estudante: {resposta_usuario}

Avalie a resposta:
- Correta: conceito explicado corretamente (aceitar sinônimos e reformulações)
- Parcialmente correta: conceito presente mas incompleto ou impreciso
- Incorreta: conceito errado ou ausente

Forneça feedback construtivo:
1. O que o estudante acertou (se aplicável)
2. O que faltou ou está incorreto (se aplicável)
3. Explicação breve do conceito correto
```

**Persistência no SQLite:**
- Registrar perguntas feitas, respostas do estudante e avaliações
- Identificar tópicos com mais erros (taxa de erro > 50%)
- Historico usado pela Funcionalidade 3.4 (planejamento de estudos)

---

## 7. PLANEJAMENTO DE ESTUDOS (Funcionalidade 3.4)

**Descrição:** Combina agenda, tarefas e materiais para gerar um plano de estudos personalizado. Esta é a funcionalidade do Trabalho 2 que integra todas as anteriores.

### 7.1 Casos de Uso

**Caso 1:** "Monte um plano de estudos para a prova de IA na sexta-feira"
1. `consultar_agenda(periodo="semana")` → encontra prova de IA na sexta
2. `listar_tarefas(status="pendente", disciplina="Inteligência Artificial")` → tarefas pendentes
3. `buscar_material_rag(query="tópicos de Inteligência Artificial", top_k=15)` → material relevante
4. Gemma 12B gera plano dia a dia até a prova

**Caso 2:** "O que devo priorizar hoje?"
1. `consultar_agenda(periodo="hoje")` → eventos do dia
2. `listar_tarefas(status="pendente")` → tarefas ordenadas por prazo
3. Gemma 12B usa histórico de erros no active recall para priorizar tópicos fracos
4. Retorna lista priorizada com estimativas de tempo

### 7.2 Lógica de Priorização

| Critério | Peso | Regra |
|---|---|---|
| Prazos | 40% | Prazo ≤ 24h = URGENTE; ≤ 48h = ALTA; 3-7 dias = MÉDIA |
| Dificuldade | 30% | Taxa de erro > 50% no active recall = priorizar |
| Carga horária | 20% | Sessões de no máximo 3h; fragmentar tarefas grandes |
| Balanceamento | 10% | Evitar concentrar apenas uma disciplina por dia |

---

## 8. AVALIAÇÃO DO SISTEMA (Trabalho 2)

### 8.1 Estrutura do `evaluation/questions.json`

```json
{
  "metadata": {
    "dataset": "Materiais de IA/ML",
    "total_questions": 10,
    "created_at": "2025-05-23T10:00:00Z"
  },
  "questions": [
    {
      "id": 1,
      "pergunta": "Explique o que é regressão logística e quando ela é usada.",
      "categoria": "conceito_basico",
      "documentos_esperados": ["apostila_ml_02.pdf"],
      "resposta_esperada": "Regressão logística é um algoritmo de classificação binária que modela a probabilidade usando a função sigmoid. É usada quando a variável alvo é categórica.",
      "criterios_avaliacao": [
        "Menciona que é classificação (não regressão)",
        "Explica o uso da função sigmoid",
        "Dá pelo menos um exemplo de aplicação"
      ]
    }
  ]
}
```

### 8.2 Estrutura do `evaluation/results.json`

```json
{
  "metadata": {
    "evaluated_at": "2025-05-25T14:30:00Z",
    "total_questions": 10,
    "correct": 7,
    "partial": 2,
    "incorrect": 1,
    "accuracy": 0.70
  },
  "results": [
    {
      "question_id": 1,
      "pergunta": "Explique o que é regressão logística...",
      "chunks_recuperados": [
        {
          "fonte": "apostila_ml_02.pdf",
          "pagina": 15,
          "score": 0.92,
          "conteudo": "[trecho recuperado]"
        }
      ],
      "resposta_gerada": "[resposta do sistema]",
      "classificacao": "correta",
      "justificativa": "[por que foi classificada assim]",
      "criterios_atendidos": 3,
      "criterios_totais": 3
    }
  ]
}
```

### 8.3 Script `evaluation/evaluate.py`

O script deve:
1. Ler `questions.json`
2. Para cada pergunta: chamar `buscar_material_rag` + Gemma 12B
3. Salvar respostas geradas em `results_intermediate.json`
4. O avaliador humano preenche `classificacao` e `justificativa`
5. Script calcula e adiciona métricas ao `metadata`

---

## 9. ANÁLISE DE ERROS (Trabalho 2)

O arquivo `evaluation/error_analysis.md` deve documentar **mínimo 3 falhas** com a seguinte estrutura para cada:

```markdown
## Erro N: [Nome descritivo]

### Pergunta
[pergunta que gerou o erro]

### Resposta Gerada
[o que o sistema respondeu]

### Classificação
[correta | parcialmente_correta | incorreta]

### Tipo de Erro
[Recuperação | Geração | Ambiguidade | Outro]

### Causa Raiz
[análise técnica da causa]

### Evidência
[chunks recuperados, scores, etc.]

### Solução Proposta
[mudança técnica concreta para corrigir]

### Impacto Esperado
[melhoria estimada]
```

---

## 10. MODELOS DE DADOS

### 10.1 SQLAlchemy — Tabela `eventos`

| Coluna | Tipo SQL | Nullable | Índice | Descrição |
|---|---|---|---|---|
| id | UUID | NOT NULL | PK | Gerado automaticamente |
| titulo | VARCHAR(200) | NOT NULL | — | Título do evento |
| descricao | VARCHAR(1000) | NULL | — | Descrição opcional |
| data | DATE | NOT NULL | SIM | Data do evento |
| hora_inicio | TIME | NULL | — | Horário de início (HH:MM) |
| hora_fim | TIME | NULL | — | Horário de término (HH:MM) |
| tipo | ENUM | NOT NULL | — | aula, prova, prazo, outro |
| local | VARCHAR(200) | NULL | — | Local físico ou virtual |

### 10.2 SQLAlchemy — Tabela `tarefas`

| Coluna | Tipo SQL | Nullable | Índice | Descrição |
|---|---|---|---|---|
| id | UUID | NOT NULL | PK | Gerado automaticamente |
| titulo | VARCHAR(200) | NOT NULL | — | Título da tarefa |
| descricao | VARCHAR(1000) | NULL | — | Descrição opcional |
| disciplina | VARCHAR(100) | NULL | SIM | Disciplina relacionada |
| status | ENUM | NOT NULL | SIM | pendente, concluida |
| prazo | DATE | NULL | SIM | Data limite |
| criada_em | DATETIME | NOT NULL | — | Timestamp de criação (UTC) |
| concluida_em | DATETIME | NULL | — | Timestamp de conclusão (UTC) |

---

## 11. CONFIGURAÇÃO E DEPLOY

### 11.1 `backend/requirements.txt`

```
fastapi==0.109.0
uvicorn[standard]==0.27.0
python-multipart==0.0.6
sqlalchemy==2.0.25
aiosqlite==0.19.0
pydantic==2.5.3
pydantic-settings==2.1.0
openai==1.10.0
langchain==0.1.5
sentence-transformers==2.3.1
faiss-cpu==1.7.4
pypdf2==3.0.1
python-dotenv==1.0.0
python-dateutil==2.8.2
```

### 11.2 `backend/.env.example`

```env
GEMMA_API_KEY=Cxt2ftLF7d3mHS2JdiFqB-eSDAQeZvFATPXPs02lV9A
GEMMA_BASE_URL=https://llm.liaufms.org/v1/gemma-3-12b-it
GEMMA_MODEL=google/gemma-3-12b-it
DATABASE_URL=sqlite:///./jarvis.db
LOG_LEVEL=INFO
LOG_FILE=logs/tool_calls.jsonl
EMBEDDING_MODEL=sentence-transformers/paraphrase-multilingual-MiniLM-L12-v2
CHUNK_SIZE=800
CHUNK_OVERLAP=100
FAISS_INDEX_PATH=data/faiss_index.bin
```

### 11.3 `docker-compose.yml`

```yaml
version: '3.8'

services:
  backend:
    build:
      context: ./backend
      dockerfile: Dockerfile
    container_name: jarvis-backend
    ports:
      - "8000:8000"
    env_file:
      - ./backend/.env
    volumes:
      - ./backend/data:/app/data
      - ./backend/logs:/app/logs
    command: uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload

  frontend:
    build:
      context: ./frontend
      dockerfile: Dockerfile
    container_name: jarvis-frontend
    ports:
      - "3000:3000"
    environment:
      - NEXT_PUBLIC_API_URL=http://localhost:8000
    depends_on:
      - backend
    command: npm run dev
```

---

## 12. CHECKLIST DE IMPLEMENTAÇÃO

### Trabalho 1

- [ ] Estrutura de diretórios criada conforme Seção 3
- [ ] FastAPI configurado (main.py, CORS, routers)
- [ ] SQLite + SQLAlchemy async configurados
- [ ] Modelos ORM criados (Evento, Tarefa)
- [ ] Schemas Pydantic criados (Create, Read, Update)
- [ ] Dataset com ≥ 10 documentos em `/data/documents/`
- [ ] `/data/README.md` completo
- [ ] RAGService implementado (chunking 800/100, FAISS, MiniLM-L12-v2)
- [ ] Tool `buscar_material_rag` implementada e testada
- [ ] Tool `consultar_agenda` implementada e testada
- [ ] Tools `listar_tarefas`, `adicionar_tarefa`, `concluir_tarefa` implementadas e testadas
- [ ] TOOLS_REGISTRY[] registrado com todas as 5 tools
- [ ] OrquestradorLLM com agent loop implementado
- [ ] LLM chamando tools autonomamente (não por lógica fixa)
- [ ] Logger dual output (JSON em arquivo + terminal) funcionando
- [ ] Frontend Next.js com ChatUI + SSE
- [ ] Docker + docker-compose funcionando
- [ ] Testes básicos em `/tests/`

### Trabalho 2

- [ ] Funcionalidade 3.4 (Planejamento de Estudos) implementada
- [ ] Geração de Exercícios implementada
- [ ] Active Recall Interativo implementado
- [ ] `evaluation/questions.json` com ≥ 10 perguntas
- [ ] `evaluation/evaluate.py` executável
- [ ] `evaluation/results.json` preenchido
- [ ] `evaluation/error_analysis.md` com ≥ 3 falhas documentadas
- [ ] README.md atualizado com lista de IAs utilizadas
- [ ] Vídeo de demonstração (≤ 3 min) gravado
