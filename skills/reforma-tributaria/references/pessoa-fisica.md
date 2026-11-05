# Reforma Tributária para pessoa física

Use linguagem simples, exemplos em reais e evite siglas sem explicação. A pessoa quer saber:
"o que muda no meu bolso?", "tenho que fazer algo?", "quando?".

## 1. Como consumidor
- Os preços passam a mostrar o imposto **separado** ("por fora") — a nota vai trazer CBS e IBS.
  Isso não significa automaticamente preço maior; o imposto antes estava escondido no preço.
- Tende a **ficar mais barato** ou estável: cesta básica (alíquota zero), medicamentos da
  lista (zero), hortifrúti e ovos (zero), alimentos do Anexo VII, saúde e educação (−60%),
  bens industrializados em geral (fim do efeito cascata).
- Tende a **ficar mais caro**: serviços em geral (academia, salão, streaming, conserto,
  serviços digitais), cigarros, bebidas alcoólicas e açucaradas, veículos (Imposto Seletivo),
  apostas.
- **Cashback:** famílias do CadÚnico com renda per capita ≤ ½ salário mínimo recebem de volta
  100% da CBS e 20% do IBS na conta de luz, água, esgoto, gás e telecom/botijão; 20%+20% no
  resto. CBS desde 2027, IBS desde 2029. **Peça CPF na nota.**

## 2. Como prestador de serviço autônomo / profissional liberal
- **Nanoempreendedor:** receita abaixo de 50% do limite do MEI e não é MEI → não paga IBS/CBS.
  Limite do MEI (LC 238/2026): R$ 81 mil em 2026, **R$ 110 mil em 2027**, **R$ 140 mil em 2028** →
  corte de ≈ R$ 40,5 mil / R$ 55 mil / R$ 70 mil. Motorista/entregador de app: conta só 25% do que recebe.
- **MEI:** IBS/CBS em valor fixo no DAS-SIMEI.
- **Profissional regulamentado (advogado, contador, engenheiro, arquiteto, administrador...)
  como PF:** se for contribuinte, redução de 30% da alíquota. Atendimento a PJ do regime
  regular: o cliente toma crédito → o imposto pesa menos na negociação.
- Profissional de saúde: serviços do Anexo III com redução de 60%.
- Avaliar com contador: PF × PJ × Simples × regime regular — a resposta muda com a reforma.

## 3. Como locador ou vendedor de imóveis
**Locação:** só vira contribuinte se, no ano anterior, recebeu **mais de R$ 240 mil** de aluguel
**e** tinha **mais de 3 imóveis** locados — ou se, no próprio ano, passar de R$ 240 mil em mais de
20% (≈ R$ 288 mil). O limite é corrigido pelo IPCA. Se for:
- alíquota com redução de 70%;
- redutor social de R$ 600 por imóvel residencial/mês (abatido da base);
- aluguel por temporada (até 90 dias) segue a regra de hotelaria (redução de 40%).
- Ex.: 5 imóveis a R$ 5.000 = R$ 300 mil/ano. Por imóvel: (5.000 − 600) × 28% × 30% ≈ R$ 369,60/mês.
  Ainda há IR. Simule com `rt_calc.py imovel`.

**Venda:** PF vira contribuinte se, no ano anterior, vendeu **mais de 3 imóveis distintos** ou
**mais de 1 imóvel construído por ela mesma** nos últimos 5 anos (LC 214, art. 251). Redutor de ajuste (custo de aquisição
atualizado) e redutor social (R$ 100 mil por imóvel residencial novo; R$ 30 mil por lote).
**Ação já:** guarde escrituras, recibos de obra e reformas — documentam o redutor de ajuste.

**Holding patrimonial:** a reforma muda a conta (IBS/CBS na locação pela PJ com redução de 70%,
mas sem o limite de R$ 240 mil/3 imóveis da PF). Reavalie estruturas existentes com números.

## 4. Herança e doação — ITCMD (LC 227/2026)
- **Progressividade obrigatória** em todos os estados (alíquotas crescentes pelo valor,
  teto atual de 8% — Resolução do Senado 9/1992).
- Doações sucessivas entre as mesmas pessoas são **somadas** para definir a faixa.
- **PGBL/VGBL** de natureza securitária, seguro de vida e pecúlio pagos a **beneficiário designado**:
  **sem ITCMD** (STF Tema 1.214). Sem beneficiário, o saldo entra no inventário.
- Bens e estruturas no exterior (inclusive **trusts**: revogável tributado na distribuição,
  irrevogável na instituição) passam a ter regra nacional.
- Fato gerador causa mortis na data do óbito.
- Efeitos dependem de **lei estadual**, observando anterioridade anual e noventena —
  expectativa de mudança nas leis estaduais em 2026/2027.
- **Ação:** quem planeja doar em vida deve avaliar com advogado/contador se antecipa doações
  antes da lei estadual progressiva entrar em vigor, considerando o estado de domicílio.

**ITBI:** base de cálculo pelo valor de mercado/transação; vetada a cobrança antecipada na
escritura — fato gerador no registro (STF Tema 1.124).

## 5. Perguntas frequentes (respostas curtas)
- *"Vou pagar imposto no Pix?"* — Não existe imposto sobre Pix. O split payment só separa o
  imposto de **vendas de empresas** contribuintes na hora do pagamento.
- *"Meu aluguel vai subir?"* — Só se o locador for contribuinte (PJ ou PF acima dos limites) e
  repassar. Contratos com PF pequena não mudam.
- *"Quando começa?"* — 2026 é teste; 2027 muda o federal; 2029–2032 transição estadual/municipal;
  2033 completo.
- *"Preciso declarar algo?"* — PF comum não. Locador/vendedor acima dos limites passa a ter
  obrigações; procure um contador.
