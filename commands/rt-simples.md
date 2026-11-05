---
description: Simples Nacional na reforma — vale optar por IBS/CBS "por fora" (regime regular) ou ficar no DAS?
argument-hint: "[anexo, RBT12, receita mensal, % vendas B2B, compras mensais com crédito]"
---

Use a skill `reforma-tributaria` para analisar a opção do Simples Nacional pelo regime regular de IBS/CBS.

Dados: $ARGUMENTS

Calcule a faixa e a alíquota efetiva com `scripts/rt_calc.py das` (nunca de memória), rode `scripts/rt_calc.py simples` para 2027 e 2033 com `--anexo`/`--rbt12`, baseie a recomendação na coluna "preço neutro", mostre sensibilidade ao volume de compras com crédito, verifique o Fator R (Anexo III × V) e informe os prazos de opção/cancelamento vigentes (confirme na web se possível).
