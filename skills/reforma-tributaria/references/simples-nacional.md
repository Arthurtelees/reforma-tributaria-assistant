# Simples Nacional e MEI na Reforma Tributária

## 1. As duas opções a partir de 2027

| | **IBS/CBS dentro do DAS** (padrão) | **IBS/CBS "por fora" — regime regular** (art. 41, §3º) |
|---|---|---|
| Recolhimento | Parcela de IBS/CBS embutida na alíquota da faixa do Anexo | Apuração pelo regime regular (alíquotas cheias, débito − crédito); demais tributos seguem no DAS |
| Crédito que gera ao cliente | Apenas o valor de IBS/CBS **efetivamente pago** no DAS (pequeno) | **Crédito pleno** do IBS/CBS destacado |
| Crédito que a empresa toma nas compras | Não toma | Toma crédito amplo |
| Complexidade | Baixa | Alta (apuração, split payment, obrigações) |
| Melhor para | Vendas a consumidor final (B2C), margem alta, poucos insumos tributados | Vendas a empresas do regime regular (B2B), muitos insumos tributados |

Optar pelo regime regular **não** exclui a empresa do Simples. Sublimite de R$ 3,6 milhões
segue valendo para IBS. Quem recebeu ressarcimento no ano corrente ou anterior não pode deixar
o regime regular (art. 41, §5º).

## 2. Prazos (atenção — mudam por Resolução CGSN)
- 2026: optantes **não** participam da fase-teste (0,9%/0,1%) — art. 348, III, "c".
- Opção para o **1º semestre de 2027**: janela 01/09 a 30/10/2026 (Res. CGSN 186/2026,
  prorrogada pela Res. CGSN 194/2026). **Cancelamento: 03/11 a 20/12/2026** (irretratável).
- Opção para o **2º semestre de 2027**: **01 a 31/03/2027**, efeitos a partir de 01/07/2027.
- Opção é **semestral**. Simples Nacional emite DF-e com grupo IBS/CBS a partir de 01/01/2027
  (Ato Conjunto RFB/CGIBS 4/2026, §1º).
- Manual oficial: https://www8.receita.fazenda.gov.br/SimplesNacional/Arquivos/manual/Manual%20op%C3%A7%C3%A3o%20regime%20regular%20IBS%20e%20CBS%20no%20Simples%20Nacional.pdf

## 3. Como decidir (roteiro de análise)
Colete: faturamento 12 meses, anexo/faixa, % das vendas para PJ do regime regular, compras
tributadas (insumos, mercadorias, serviços) com crédito possível, margem, poder de preço.

1. Calcule a alíquota efetiva e a partilha do DAS com `scripts/rt_calc.py das --anexo X --rbt12 Y`
   (tabelas oficiais da LC 123 em `assets/simples_anexos.json` — não use valores de memória) e depois
   o custo de cada opção com `scripts/rt_calc.py simples --anexo X --rbt12 Y ...` para 2027 e 2033.
2. Calcule o **valor do crédito que o cliente B2B deixa de ter** no DAS — esse é o "desconto"
   que o cliente vai exigir para continuar comprando de você.
3. Compare: `custo extra do regime regular` vs `perda de competitividade (crédito do cliente)`.
4. Considere caixa: no regime regular o split payment retém o tributo na liquidação.
5. Reavalie a cada semestre.

**Regra de bolso:** se > 50–60% da receita é B2B para empresas do regime regular e há muitos
insumos com crédito, o regime regular tende a vencer; se é B2C, o DAS tende a vencer. Sempre
rode números — a regra de bolso falha com margens extremas.

## 4. MEI
Recolhe IBS/CBS em valor fixo no DAS-SIMEI; **não pode** optar pelo regime regular (a opção não se
aplica ao SIMEI). **LC 238/2026** (DOU 21/10/2026): limite do MEI sobe para R$ 110 mil em 2027 e
R$ 140 mil em 2028, com até 2 empregados — reavalie clientes que hoje estão no Simples por pouco.
Nanoempreendedor (receita < 50% do limite MEI, PF não MEI) não é contribuinte.

## 5. Impacto para quem compra de optantes do Simples
Empresa do regime regular que compra de fornecedor no DAS terá crédito reduzido. Ação:
mapear fornecedores Simples na base de compras, simular perda de crédito e negociar preço ou
pedir que o fornecedor opte pelo regime regular.
