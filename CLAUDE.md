# CLAUDE.md — Instruções Persistentes para o Claude Code

Este arquivo é lido automaticamente pelo Claude Code a cada sessão. Contém regras
não-negociáveis do projeto. Seguir TUDO sem exceção.

---

## 0. Contexto rápido

- **Projeto:** JARVIS Acadêmico — assistente de estudos com RAG + Tool Calling + LLM Gemma 12B.
- **Raiz:** `C:\Users\teste.5\projetos\ia\`
- **Stack:** FastAPI + Python 3.11 (backend, pronto até Fase 5) | Next.js 14 + Tailwind v4 (frontend, em construção — Fase 6).
- **Entrega atual:** Trabalho 1 — funcionalidades 3.1 (RAG), 3.2 (Agenda), 3.3 (Tarefas).

## 1. Arquivos que SEMPRE devem ser lidos antes de qualquer alteração

Ordem obrigatória de leitura no início de cada sessão de trabalho:

1. `SPEC.md` — especificação técnica completa. Seção 1.4 (Clean Code + SOLID) e 2.5 (Design System) são leitura obrigatória do frontend.
2. `MEMORY.md` — estado atual e histórico de fases. Sempre consulte qual fase está em andamento antes de propor mudanças.
3. `FRONTEND_PLAN.md` — plano dos 6 sprints do frontend. Cada prompt do CLI corresponde a um sprint.

Nunca implemente nada sem antes confirmar que leu os três.

## 2. Regras de Backend (Python)

- Python 3.11 (NÃO usar 3.14 — SQLAlchemy 2.0.25 incompatível).
- Toda função: máximo 20 linhas.
- Zero `except: pass`. Toda exceção logada com `logger.exception(...)` ou `logger.error(..., exc_info=True)` e re-lançada quando apropriado.
- Type hints em TUDO. `-> None` é obrigatório.
- Imports lazy (TYPE_CHECKING) para `sentence_transformers`, `torch`, `RAGService`. Isso protege o startup quando o pacote não está instalado.
- DIP em todo lugar: funções/classes recebem dependências como parâmetros, não as instanciam internamente.
- venv em `backend/.venv` com Python 3.11. Pacotes instalados via `uv pip install`.

## 3. Regras de Frontend (Next.js + TypeScript)

### Estrutura

- Frontend vive em `frontend/`. Todos os comandos rodam a partir dessa pasta.
- `src/` com alias `@/*`.
- Componentes em `src/components/{layout,chat,agenda,tasks,ui}/`.
- Hooks em `src/hooks/`. Tipos em `src/types/`. API em `src/lib/api.ts`.

### Configuração Next.js

`next.config.ts` deve ter:
- `devIndicators: false`
- `output: 'standalone'`

### TypeScript

- **ZERO `any`.** Sem exceção. Se precisar de tipo desconhecido, use `unknown` + narrowing.
- Toda prop tipada com `interface` ou `type` exportado. Sem `props: any`.
- Tipos compartilhados em `src/types/`. Não duplicar `Message`, `Evento`, `Tarefa` em múltiplos arquivos.

### Componentes

- Máximo 20 linhas de JSX por componente. Se passar disso, extrair sub-componente.
- Responsabilidade única: componente de UI não faz fetch; componente de dados não faz layout.
- Sem `useEffect` para lógica de negócio — usar custom hooks (`useChat`, `useSSE`, etc.).

### Estilização

- **Tailwind v4** — tokens em `src/app/globals.css` via `@theme`. **Não criar nem editar `tailwind.config.ts` para tokens.** O arquivo pode existir vazio ou só com plugins; cores, fontes, radius vão em CSS.
- Cores sempre via tokens (`bg-background`, `text-foreground`, etc.). Não usar valores hex inline em JSX.

### Tratamento de erros

- Toda chamada `fetch` em try/catch com feedback visual (toast ou estado de erro).
- Estado de erro tipado: `status: 'idle' | 'loading' | 'streaming' | 'error'`.
- Não silenciar erros no console. Logar com contexto: `console.error('useSSE:', error)`.

## 4. Regras de Tool Calling / LLM

- TOOLS_REGISTRY em `backend/app/tools/__init__.py` é a fonte da verdade. Nunca duplicar schemas.
- A LLM decide quais tools chamar. Nunca implementar lógica fixa de "se a mensagem contém X, chama tool Y".
- Logger dual (JSON + terminal) é obrigatório em qualquer nova tool.

## 5. Como o Claude Code deve trabalhar

- **Atualizar `MEMORY.md` ao concluir cada fase/sprint** — adicionar linha na tabela com status, arquivos criados/editados, problemas encontrados, validações executadas.
- Antes de criar arquivo, conferir se já existe (`MEMORY.md` lista o que foi feito).
- Antes de editar contrato (rota REST, schema Pydantic), conferir se o frontend já depende dele.
- Após implementar, rodar validação concreta (não declarativa): `npm run build`, `curl` no endpoint, ou script de teste. Nunca dizer "implementado" sem validação.
- Quando encontrar divergência entre SPEC e código, **parar e perguntar**, não decidir sozinho.

## 6. Princípios SOLID aplicados ao frontend (SPEC seção 1.4)

- **S** — Cada componente faz uma coisa. `ChatMessage` renderiza; não busca dados.
- **O** — Novos tipos de evento ou tarefa entram via mapa de configuração, não via `if/else` em vários lugares.
- **L** — `ChatMessageUser` e `ChatMessageAssistant` honram o contrato `ChatMessageProps`.
- **I** — Interfaces específicas (`ConversationStore` ≠ `MessageStore`), não uma `StorageProps` monolítica.
- **D** — `useChat` recebe um `ConversationStore`; não importa `localStorage` diretamente. Isso permite trocar por API no T2.

## 7. Endpoints REST disponíveis (estado atual do backend)

Antes de chamar qualquer endpoint, conferir esta lista — refletindo o que está em `backend/app/api/routes/`:

| Método | Rota | Query params | Status |
|---|---|---|---|
| POST | `/api/chat` | — | OK (não streama token-a-token; envia resposta única em 1 evento SSE) |
| GET | `/api/agenda` | `tipo`, `data` (YYYY-MM-DD) | OK |
| POST | `/api/agenda` | — | OK |
| GET | `/api/tasks` | `status` (pendente\|concluisda), `disciplina` | OK |
| POST | `/api/tasks` | — | OK |
| PATCH | `/api/tasks/{id}/concluir` | — | **A ADICIONAR** antes do Sprint 4 |

CORS já libera `http://localhost:3000`.

## 8. Comunicação com o usuário (advogado, não técnico em frontend)

- Português brasileiro, registro profissional.
- Sem muita explicação normalmente resuma só quando for inevitável
- Decisões irreversíveis (excluir arquivo, editar SPEC, mudar contrato) → mostrar e pedir "ok".
- Resumir mudanças ao final de cada sprint.