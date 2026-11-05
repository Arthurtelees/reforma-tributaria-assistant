---
description: Classifica produtos/serviços (NCM/NBS) em CST e cClassTrib do IBS/CBS com redução e base legal
argument-hint: "[lista de itens com NCM/NBS, ou caminho de CSV/planilha do cadastro]"
---

Use a skill `reforma-tributaria` para classificar no IBS/CBS os itens: $ARGUMENTS

Para cada item: verifique os Anexos da LC 214 (cesta básica, 60%, 30%, alíquota zero) e regimes específicos; consulte `scripts/consultar_cclasstrib.py` (se o usuário tiver a planilha oficial do Informe Técnico 2025.002-RT, use `--tabela`). Entregue uma tabela item × NCM/NBS × CST × cClassTrib × redução × base legal × observação, marque o que precisa de conferência na tabela oficial e, se recebeu arquivo, salve o resultado como CSV ao lado dele.
