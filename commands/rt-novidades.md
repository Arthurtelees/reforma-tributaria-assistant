---
description: Verifica novidades oficiais da Reforma Tributária desde a data-base da skill e propõe atualizar os parâmetros
argument-hint: "[opcional: tema, ex. alíquota CBS, split payment, NF-e]"
---

Use a skill `reforma-tributaria`. Leia `assets/parametros.json` (campo `data_base`) e `references/fontes-oficiais.md` (lista de pendências).

Com WebSearch/WebFetch, procure em fontes oficiais (Planalto/DOU, CGIBS, Receita Federal, Portal NF-e, Senado) o que mudou desde a data-base, com foco em: $ARGUMENTS (se vazio, todas as pendências listadas).

Entregue: (1) lista do que mudou, com data, norma e link; (2) pendências que continuam abertas; (3) a alteração proposta em `assets/parametros.json` e nas referências afetadas, mostrando o diff — **só aplique após confirmação do usuário**.
