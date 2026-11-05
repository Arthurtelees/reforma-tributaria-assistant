---
description: Audita XMLs de NF-e/NFC-e no grupo IBS/CBS (CST, cClassTrib, cálculos, totais, chave) e explica como corrigir
argument-hint: "[arquivo.xml | pasta com XMLs]"
---

Use a skill `reforma-tributaria` para auditar os XMLs em: $ARGUMENTS

1. Rode `scripts/validar_nfe.py` (use `--pasta` se for diretório) com `--csv problemas-ibscbs.csv`.
2. Para cada problema, explique em linguagem de faturamento/ERP o que está errado, a regra (NT 2025.002-RTC, LC 214, Ato Conjunto RFB/CGIBS 4/2026) e a correção concreta (valor ou tag correta).
3. Agrupe problemas repetidos (provável erro de cadastro/parametrização) e diga qual cadastro corrigir no ERP.
4. Lembre o prazo de regularização do PNCT quando aplicável.
