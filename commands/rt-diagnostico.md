---
description: Diagnóstico de impacto da Reforma Tributária para uma empresa (carga 2026–2033, créditos, caixa, preço, plano de ação)
argument-hint: "[descrição da empresa: regime, setor, UF, faturamento, % B2B, alíquotas atuais]"
---

Use a skill `reforma-tributaria` para elaborar um diagnóstico de impacto da Reforma Tributária para a empresa descrita abaixo.

Empresa: $ARGUMENTS

Siga o fluxo da skill: identifique regime, setor e regime diferenciado/específico aplicável; colete só o que faltar (se faltar algo, assuma e declare a premissa); rode `scripts/rt_calc.py transicao` (e `das`/`simples` se for do Simples ou se o Simples for alternativa); preencha `assets/modelo-diagnostico.md` e salve como `diagnostico-<nome-da-empresa>.md` no diretório atual. Termine com o plano de ação com datas.
