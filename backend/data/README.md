# Dataset — Materiais de Estudo de IA/ML

## 1. Origem dos Dados

| # | Arquivo | Fonte | Licença |
|---|---|---|---|
| 01 | apostila_machine_learning_ufes.pdf | PET Engenharia Mecânica — UFES | Educacional, uso acadêmico |
| 02 | apostila_inteligencia_artificial_uece.pdf | CCT — UECE | Educacional, uso acadêmico |
| 03 | redes_neurais_aprendizado_artificial.pdf | Fernando Osório — I Forum de IA | Educacional, uso acadêmico |
| 04 | ia_machine_learning_scielo.pdf | SciELO — Revista Estudos Avançados | Acesso aberto |
| 05 | apostila_ia_esesp.pdf | ESESP — Governo do ES | Público |
| 06 | introduction_to_machine_learning_arxiv.pdf | arXiv:2409.02668 (Laurent Younes, 2024) | arXiv non-exclusive license |
| 07 | intro_ml_for_sciences_arxiv.pdf | arXiv:2102.04883 (Neupert et al.) | arXiv non-exclusive license |
| 08 | brief_intro_ml_engineers_arxiv.pdf | arXiv:1709.02840 (Simeone) | arXiv non-exclusive license |
| 09 | deep_learning_nlp_trends_arxiv.pdf | arXiv:1708.02709 | arXiv non-exclusive license |
| 10 | nlp_network_embedding_tutorial_arxiv.pdf | arXiv:1910.07212 | arXiv non-exclusive license |

**Critério de seleção:** Materiais introdutórios e intermediários de IA/ML com cobertura ampla de tópicos (regressão, redes neurais, CNN, NLP, embeddings, clustering) que suportam as perguntas do conjunto de avaliação.

**Data de coleta:** 2026-05-24

## 2. Tipo de Conteúdo

- **Domínio:** Inteligência Artificial e Machine Learning
- **Tópicos cobertos:** Fundamentos de ML, regressão linear e logística, redes neurais, CNNs, NLP, embeddings, deep learning, aprendizado supervisionado e não-supervisionado
- **Idiomas:** Português (5 documentos) + Inglês (5 documentos)
- **Formatos:** 10 PDFs
- **Volume total:** ~25 MB, estimativa de 800–1 200 chunks após processamento

## 3. Limitações Conhecidas

- Documentos em inglês podem gerar chunks com menor precisão de recuperação para queries em português (mitigado pelo modelo multilingual MiniLM-L12-v2)
- Alguns PDFs foram gerados via LaTeX com fórmulas matemáticas — OCR pode perder símbolos complexos
- Papers do arXiv têm conteúdo mais denso e técnico; podem não ser ideais para perguntas conceituais simples
- Apostilas de 1999 (doc 03) têm terminologia menos atual

## 4. Estratégia de Chunking

- **Método:** RecursiveCharacterTextSplitter (LangChain)
- **chunk_size:** 800 caracteres
- **chunk_overlap:** 100 caracteres
- **Separadores:** `["\n\n", "\n", ". ", " ", ""]`
- **Justificativa:** 800 caracteres captura 1–2 parágrafos completos, preservando contexto suficiente para que a LLM responda com precisão. Overlap de 100 (~12,5%) garante que conceitos que cruzam a fronteira entre chunks não sejam perdidos. Separadores priorizam quebras naturais (parágrafo > sentença > palavra).

## 5. Impacto no RAG

**Vantagens:**
- Mix de idiomas aumenta cobertura temática
- Apostilas brasileiras respondem melhor a perguntas em português
- Papers arXiv cobrem tópicos avançados (embeddings, NLP, deep learning)

**Desvantagens:**
- Fórmulas LaTeX viram texto sem sentido após extração de texto de PDF
- Documentos longos (>100 páginas) geram muitos chunks; aumenta latência no primeiro startup

**Alternativas consideradas:**
- Chunks de 400 chars — descartado: perdia contexto de parágrafos inteiros
- Chunks de 1 500 chars — descartado: diluía relevância, retornava muito ruído nas buscas
