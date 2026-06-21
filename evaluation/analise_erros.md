# Análise de Erros — JARVIS Acadêmico

Avaliação realizada em 14/06/2026. Sistema testado com 10 perguntas sobre conteúdo de IA/ML.
Resultado geral: 3 corretas, 4 parcialmente corretas, 3 incorretas (accuracy 0.30 / 0.70 com parciais).

---

## Erro 1: Ausência de Material Específico sobre Regressão Logística

### Pergunta
Explique o que é regressão logística e quando ela é usada.

### Resposta Gerada
O sistema informou que não encontrou material específico sobre regressão logística nos documentos disponíveis e respondeu com base em conhecimento geral, sem citar nenhum trecho do dataset.

### Classificação
parcialmente_correta

### Tipo de Erro
Recuperação

### Causa Raiz
Os 10 chunks recuperados para esta pergunta tiveram scores baixos (máximo 0.3555), todos abaixo do limiar de relevância semântica adequado. O chunk de maior score veio do `Ebook IA.pdf` (conteúdo jurídico), e os chunks das apostilas técnicas recuperados não continham a definição direta do algoritmo. O modelo de embedding `paraphrase-multilingual-MiniLM-L12-v2` não encontrou correspondência semântica suficiente entre a query em português e os trechos disponíveis sobre regressão logística, que aparecem de forma fragmentada nos documentos.

### Evidência
```
chunk_index 0: fonte=Ebook IA.pdf, pagina=443, score=0.3555
chunk_index 1: fonte=Ebook IA.pdf, pagina=194, score=0.3290
chunk_index 3: fonte=01_apostila_machine_learning_ufes.pdf, pagina=44, score=0.3120
```
Nenhum chunk continha a definição de regressão logística — o chunk da apostila UFES (pág. 44) trata de otimizadores adaptativos (ADAM, ADAGRAD), não do algoritmo em si.

### Solução Proposta
Aumentar o `top_k` de 5 para 10-15 na ferramenta `buscar_material_rag` para perguntas conceituais, aumentando a chance de recuperar chunks relevantes mesmo com scores baixos. Adicionalmente, adicionar ao dataset um documento dedicado a algoritmos clássicos de ML com definições explícitas (ex: apostila de regressão logística com a função sigmoid descrita claramente).

### Impacto Esperado
Com top_k aumentado e dataset mais denso, estima-se que perguntas sobre algoritmos clássicos passem de parcialmente_correta para correta em 60-70% dos casos.

---

## Erro 2: Recuperação Genérica para Pergunta Específica sobre CNNs

### Pergunta
O que são redes neurais convolucionais (CNNs) e para que servem?

### Resposta Gerada
O sistema recuperou chunks sobre redes neurais artificiais genéricas e respondeu sem mencionar os conceitos específicos de CNNs: convolução, pooling, filtros aprendíveis ou aplicações em visão computacional. A resposta foi classificada como parcialmente correta pois descreve redes neurais em geral mas não responde à pergunta específica.

### Classificação
parcialmente_correta

### Tipo de Erro
Recuperação

### Causa Raiz
A query "redes neurais convolucionais" gerou um embedding semanticamente próximo de "redes neurais" genéricas. O FAISS (IndexFlatL2) retornou os chunks com maior similaridade vetorial, que foram os trechos sobre RNA em geral (apostila UECE pág. 62, score 0.4120) em vez de trechos específicos sobre CNNs. O dataset não possui documento dedicado a CNNs — os documentos cobrem redes neurais de forma geral sem aprofundar arquiteturas convolucionais.

### Evidência
```
chunk_index 0: fonte=02_apostila_inteligencia_artificial_uece.pdf, pagina=62, score=0.4120
conteudo: "A característica mais significante de redes neurais está em sua habilidade de
aproximar qualquer função contínua não linear..."
```
Nenhum dos 5 chunks recuperados menciona convolução, pooling ou filtros — todos tratam de RNA genérica.

### Solução Proposta
Duas abordagens complementares: (1) adicionar ao dataset um documento específico sobre deep learning e CNNs (ex: capítulo 9 do Deep Learning book — Goodfellow et al.); (2) implementar expansão de query no RAGService, onde a LLM reformula a pergunta antes da busca vetorial para incluir termos relacionados ("convolução", "pooling", "filtros").

### Impacto Esperado
Com documento específico de CNNs no dataset, a recuperação passaria a retornar chunks diretamente relevantes, transformando respostas parcialmente corretas em corretas para perguntas sobre arquiteturas específicas de deep learning.

---

## Erro 3: Cobertura Insuficiente do Dataset para Transformers e Atenção

### Pergunta
O que é o mecanismo de atenção e qual sua relação com a arquitetura Transformer?

### Resposta Gerada
O sistema não encontrou nenhum chunk relevante sobre o mecanismo de atenção ou Transformers. Todos os chunks recuperados foram de documentos completamente não relacionados (Ebook IA.pdf — conteúdo jurídico, apostila UECE — robótica industrial). O sistema respondeu inteiramente do conhecimento geral do LLM, sem ancorar a resposta no material do dataset.

### Classificação
incorreta

### Tipo de Erro
Recuperação + Cobertura do Dataset

### Causa Raiz
Esta pergunta obteve os scores mais baixos de toda a avaliação (máximo 0.3000), indicando que não existe nenhum chunk no dataset com similaridade semântica adequada ao tema. O dataset não contém material sobre a arquitetura Transformer nem sobre mecanismos de atenção — os documentos cobrem redes neurais clássicas (perceptron, backpropagation) mas não arquiteturas modernas de NLP. O `Ebook IA.pdf` (conteúdo jurídico) apareceu no top-5 com score 0.2997, evidenciando ausência total de material relevante.

### Evidência
```
score máximo: 0.3000 (menor de todas as 10 perguntas)
chunk_index 0: fonte=Ebook IA.pdf, pagina=195, score=0.2997
chunk_index 3: fonte=02_apostila_inteligencia_artificial_uece.pdf, pagina=2, score=0.2930
```
Scores abaixo de 0.35 indicam recuperação aleatória — o índice FAISS retorna os "menos piores" chunks disponíveis, não chunks genuinamente relevantes.

### Solução Proposta
(1) Adicionar threshold mínimo de 0.40 na ferramenta `buscar_material_rag` — quando nenhum chunk superar esse threshold, o sistema deve informar explicitamente "não tenho material sobre este tema" em vez de gerar resposta do conhecimento geral do LLM, evitando respostas não fundamentadas; (2) expandir o dataset com material sobre arquiteturas modernas de NLP, incluindo o paper original "Attention is All You Need" (Vaswani et al., 2017) disponível gratuitamente no arXiv.

### Impacto Esperado
O threshold evitaria respostas não fundamentadas em pelo menos 2-3 perguntas da avaliação atual. A adição do paper de Transformers ao dataset resolveria diretamente as perguntas 7 e 8, estimando melhora de incorreta para correta nessas questões.
