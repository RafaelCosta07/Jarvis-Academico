# MEMORY.md — Estado do Projeto JARVIS Acadêmico

---

## Visão Geral

| Item | Detalhe |
|---|---|
| Stack Backend | FastAPI + Python 3.11 + SQLite + FAISS |
| Stack Frontend | Next.js + Tailwind v4 + React |
| Entrega atual | Trabalho 1 — Funcionalidades 3.1, 3.2, 3.3 |
| Status geral | ✅ T1 Concluído |

---

## Progresso por Fase

### Backend

| Fase | Status | Descrição |
|---|---|---|
| Ingestão de Requisitos | ✅ Concluída | Leitura e validação do edital; stack definida (Next.js + Tailwind v4 / FastAPI + SQLite + FAISS) |
| Especificação Técnica | ✅ Concluída | SPEC.md criado com arquitetura, contratos de Tool Calling e estrutura de diretórios |
| Fase 1 — Estrutura de Diretórios | ✅ Concluída | 28 diretórios do SPEC.md Seção 3 criados fisicamente (frontend/, backend/, evaluation/) |
| Fase 2 — Fundação de Dados (SQLite + Models) | ✅ Concluída | requirements.txt, database.py (engine async + Base + get_db + create_all_tables), evento.py (Evento + TipoEvento, índice em data), tarefa.py (Tarefa + StatusTarefa, índices em disciplina/status/prazo), models/__init__.py |
| Fase 2 — Code Review e Validação | ✅ Concluída | Correções: logging adicionado ao get_db, funções _make_engine/_make_session_factory extraídas, configure_for_testing() adicionada para testabilidade. Validação: 4/4 verificações passaram. Observação: SQLAlchemy 2.0.25 incompatível com Python 3.14 — venv com Python 3.11.15. |
| Fase 3 — Schemas Pydantic e Rotas CRUD | ✅ Concluída | Arquivos criados: schemas/evento.py, schemas/tarefa.py, schemas/__init__.py, api/routes/agenda.py, api/routes/tasks.py, main.py |
| Fase 3 — Code Review e Validação | ✅ Concluída | Correções: FastAPI renomeada para `app` (compatível com uvicorn), type hint AsyncGenerator adicionado ao lifespan, try/except com logger.exception em todas as rotas. Endpoints validados 8/8. |
| Fase 4 — Motor RAG (FAISS + LangChain) | ✅ Concluída | rag_service.py criado. Chunking: chunk_size=800, overlap=100. Embedding: paraphrase-multilingual-MiniLM-L12-v2 (384 dims, CPU). FAISS: IndexFlatL2, persistido em data/faiss_index.bin. Score: 1/(1+distancia_L2). |
| Fase 4 — Code Review e Validação RAG | ✅ Concluída | Correções: try/except adicionado em construir_indice e recuperar_chunks, guarda self.index is None. Validações funcionais: 8/8 passaram com mock _MockST (DIP do construtor). Pacotes: faiss-cpu==1.7.4, langchain==0.1.5, PyPDF2==3.0.1, numpy==1.26.4. |
| Fase 5 — Tool Calling e Orquestrador LLM | ✅ Concluída | 9 arquivos criados: logger.py, 5 tools (consultar_agenda, listar_tarefas, adicionar_tarefa, concluir_tarefa, buscar_material_rag), tools/__init__.py, orchestrator.py, api/routes/chat.py. Logger dual-output: JSONL + terminal colorido. Orquestrador: AsyncOpenAI, loop máx. 10 iterações. |
| Fase 5 — Code Review e Validação (v2) | ✅ Concluída | Correções: imports lazy (TYPE_CHECKING) em buscar_material_rag.py e orchestrator.py, _NullRAGService (Null Object) como fallback, try/except em _obter_rag_service, tool_choice removido. Validações T1–T7: 6/7 passaram (T3 ambiente: vLLM rejeita tools sem --enable-auto-tool-choice). Servidor inicia limpo. |

---

### Frontend

| Fase | Status | Descrição |
|---|---|---|
| Sprint 0 — Setup | ✅ Concluída | Next.js 16.2.6 com TypeScript + Tailwind v4 + ESLint + App Router. shadcn@latest: 9 componentes. Dependências: react-markdown, remark-gfm, lucide-react, date-fns. next.config.ts: devIndicators:false + output:standalone. globals.css: @theme inline com todos os tokens SPEC 2.5 + keyframes pulse-wave/blink/fade-slide-up. Fontes: Inter + JetBrains Mono. Build OK. |
| Sprint 1 — Layout 3 Colunas | ✅ Concluída | AppShell.tsx (grid 18/64/18 → 20/60/20 → 22/56/22%), LeftSidebar.tsx, RightSidebar.tsx, page.tsx. Breakpoints: 1280/1440/1920px via @layer utilities. Build OK. |
| Sprint 2 — Chat UI (Mock) | ✅ Concluída | 14 arquivos criados: types (chat.ts, api.ts), ui (NeuralPulse, GlassCard, GradientButton), chat (ChatMessageUser, ChatMessageAssistant, ChatMessage, ChatInput, ChatEmpty, ChatMessageList, ChatHeader, ChatWindow). globals.css: prose-jarvis, chat-header-pulse, chat-input-focused. Build OK. |
| Sprint 3 — SSE + Typewriter | ✅ Concluída | lib/api.ts (postChat com AbortSignal), hooks/useSSE.ts (parseBuffer + readStream + AbortController), hooks/useChat.ts (typewriter 15ms/2chars, stopTypewriter, makeCallbacks). Mock removido. .env.local criado. Build OK. |
| Sprint 4 — Sidebar Direita (Agenda + Tarefas) | ✅ Concluída | 9 arquivos criados: GradientBadge, AgendaEventItem, AgendaMiniCal, AgendaWidget, TaskItem (otimistic update + PATCH), TaskList, TaskWidget, TaskQuickAdd. RightSidebar atualizado. Build OK. |
| Sprint 5 — Sidebar Esquerda + Conversas | ✅ Concluída | Arquivos criados: types/conversation.ts, lib/conversation-store.ts (DIP: ConversationStore + LocalStorageStore + factory), hooks/useConversations.ts. Editados: useChat.ts (onCreate/onComplete, loadMessages), LeftSidebar.tsx (ConversationItem, formatDate, avatar), page.tsx (store useMemo, useConversations + useChat integrados, activeIdRef). Build OK. |
| Sprint 6 — Polish + Animações + Erros | ✅ Concluída | Novos: lib/toast.ts (emitter singleton), ui/ToastContainer.tsx, ui/ConfettiParticles.tsx. globals.css: +5 keyframes (confetti-fly, send-flash, shake, send-flash-bar, scrollbar). Editados 11 componentes: GlassCard (estado error), ChatHeader (Loader2 spin, ⚠ Erro), ChatInput (send-flash), mensagens (fade-slide-up), retry em erro, TaskItem (confetti + toast), hover lift em cards. Build OK, zero erros TypeScript. |

---

### Correções e Fixes

| Fix | Status | Descrição |
|---|---|---|
| Fix-A — Backend SSE + Estrutura | ✅ Concluída | Estado verificado: SSE já correto, hora HH:MM já correto, todos os services e arquivos estruturais já existiam. Correções: try/except + logger.exception nos services, db.flush() em task_service, except HTTPException: raise antes do except Exception no endpoint concluir_tarefa. Validações: 6/6 passaram. |
| Fix-B — Frontend Bugs | ✅ Concluída | Bug 1: race condition SSE — corrigido com isSystemActiveIdChange ref em page.tsx. Bug 2: conversa duplicada — condição trocada de messages.length === 0 para !activeId em useChat.ts. Bug 3: rollback otimistic update ausente — onRevert adicionado à cadeia TaskItem → TaskList → TaskWidget. Cosmético: stream:true adicionado em postChat. Build OK, zero erros. |
| Fix-1 — Hydration LeftSidebar | ✅ Concluída | Causa: useState lazy initializer chamava localStorage.getItem() no SSR, retornando [] no servidor e conversas reais no cliente. Correção: useState([]) + useEffect para diferir leitura ao mount. Build OK. |
| Fix-2 — Backend SSE + Estrutura (revalidação) | ✅ Concluída | Estado verificado: todos os itens já corretos. Única correção: import de RAGService movido para TYPE_CHECKING em tools/base.py (regra lazy import). Validações: 7/7 passaram. |
| Validação Final T1 | ✅ Concluída | Backend: SSE OK, hora HH:MM OK, CRUD agenda/tasks OK, 6 arquivos estruturais presentes. Frontend: build OK, tsc --noEmit OK. Observação: data/documents/ vazia — RAG funcional no código, validação end-to-end requer documentos PDF/TXT. |

---

## Estado Final — Trabalho 1 (T1)

### Checklist de Entrega

**Funcionalidades obrigatórias:**
- [x] 3.1 — RAG: `buscar_material_rag` registrada, RAGService funcional. Validação end-to-end requer documentos em `backend/data/documents/`
- [x] 3.2 — Agenda acadêmica: GET/POST /api/agenda + AgendaWidget. Hora serializada em HH:MM
- [x] 3.3 — Lista de tarefas: GET/POST/PATCH /api/tasks + TaskWidget. Otimistic update com rollback

**Interface:**
- [x] Chat SSE funcional — protocolo token/done/error correto
- [x] Layout 3 colunas (LeftSidebar + Chat + RightSidebar)
- [x] Conversas persistidas em localStorage com DIP (ConversationStore interface)
- [x] Typewriter simulado no frontend (15ms/2chars)

**Qualidade de código:**
- [x] Zero `any` no TypeScript
- [x] `npm run build` sem erros
- [x] `npx tsc --noEmit` sem erros
- [x] Estrutura de arquivos conforme SPEC.md seção 3
- [x] Clean Code + SOLID (SPEC seção 1.4)

### Bugs corrigidos

1. Race condition SSE — `page.tsx` cancelava SSE quando `activeId` mudava durante `sendMessage`
2. Conversa duplicada — `useChat.ts` criava segunda conversa quando `activeId` já existia com messages vazio
3. Rollback otimistic update ausente — `TaskItem.tsx` não revertia tarefa ao falhar PATCH
4. Serialização `HH:MM:SS` → `HH:MM` em hora_inicio/hora_fim
5. HTTPException 404/409 logadas incorretamente como erro de servidor

### Observações para T2

- Streaming real (token a token) a implementar no orquestrador — atualmente emite um único evento token com a resposta completa
- Adicionar documentos em `backend/data/documents/` e chamar `RAGService.construir_indice()` para validar funcionalidade 3.1 end-to-end
- `ConversationStore` com DIP — pronto para `ApiStore` no T2 sem alterar hooks
- Funcionalidades 3.4, exercícios, active recall e avaliação do sistema pendentes para T2

---

## Próximo Passo

Trabalho 1 encerrado. Próximo: **T2** — Funcionalidade 3.4 + melhorias de aprendizado + avaliação do sistema + análise de erros.
