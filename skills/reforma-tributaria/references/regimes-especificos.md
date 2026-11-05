# Regimes específicos (LC 214/2025, Título V e seguintes)

> Regimes específicos têm base de cálculo, alíquota e regras de crédito próprias e **prevalecem**
> sobre a regra geral. Números de artigos acima do art. 234 ⚠️ podem ter sido deslocados pela
> LC 227/2026 — confira no texto compilado antes de citar em parecer.

## Sumário
1. Combustíveis
2. Serviços financeiros
3. Planos de saúde
4. Concursos de prognósticos e apostas
5. Bens imóveis
6. Cooperativas
7. Bares, restaurantes, hotelaria, parques, turismo
8. SAF (futebol), transporte, missões diplomáticas

---

## 1. Combustíveis (arts. 172–180)
- **Monofásico** e **ad rem** (R$ por unidade), alíquota uniforme no país. Adquirente em regra
  não toma crédito (exceções para uso como insumo — conferir).
- Art. 174: CBS de 2027 limitada à carga federal extinta; IBS cresce 10% (2029), 20% (2030),
  30% (2031), 40% (2032), pleno em 2033.
- Biocombustíveis: 40% a 90% da alíquota do fóssil comparável (art. 175). LC 235/2026 (§12 do
  art. 174): reduções no fóssil devem preservar o diferencial do biocombustível.
- NF-e: CST 620 (monofásica), grupos `gMonoPadrao`, `gMonoReten`, `gMonoRet`, `gMonoDif`
  (produção prevista para 16/11/2026 pela NT 2025.002 v1.52 ⚠️).

## 2. Serviços financeiros (arts. 181–233)
- Base: spread e receitas com deduções (custo de captação, PDD, etc.).
- Alíquota conjunta IBS+CBS (art. 233, redação LC 227):

| Ano | Alíquota |
|---|---|
| 2027–2028 | 10,85% |
| 2029 | 11,00% |
| 2030 | 11,15% |
| 2031 | 11,30% |
| 2032 | 11,50% |
| 2033+ | 12,50% |

- Tomador contribuinte (PJ no regime regular) pode ter crédito em certas operações.
- Obrigação acessória: **DeRE** (Declaração de Regimes Específicos) — CST 820.

## 3. Planos de saúde (art. 234 e seguintes)
- Base: receitas menos indenizações/despesas assistenciais. Redução de 60% (art. 237).
- Adquirente, em regra, sem crédito; exceção para plano empresarial a empregados ⚠️.
- Planos de saúde animal: redução de 30% ⚠️. Obrigação: DeRE (cClassTrib 820001 / 011002).

## 4. Concursos de prognósticos e apostas
- Base: arrecadação − prêmios − destinações legais. DeRE.
- Também sujeitos ao **Imposto Seletivo** (inclui fantasy sport) — 0,5% pela MP 1.399/2026.

## 5. Bens imóveis (arts. 251–270)
**Quem é contribuinte:**
- PJ que opera com imóveis (incorporação, loteamento, locação, administração, intermediação).
- **PF na locação** (art. 251): no ano anterior, **receita de aluguel > R$ 240 mil E mais de 3 imóveis
  distintos** locados (§1º, I); ou, **no próprio ano**, receita que exceda o limite em mais de 20%
  (≈ R$ 288 mil — §2º, II; há divergência se também exige > 3 imóveis). O limite é **atualizado
  mensalmente pelo IPCA** (§5º).
- **PF na alienação** (art. 251): no ano anterior, alienou/cedeu **mais de 3 imóveis distintos**
  (§1º, II) **ou** alienou **mais de 1 imóvel construído por ela mesma** nos 5 anos anteriores
  (§1º, III); vira contribuinte já no próprio ano se exceder esses limites (§2º, I).
- **Locação por temporada de até 90 dias**: segue o regime de **hotelaria** (redução de 40%).

**Reduções (art. 261):** 50% na alienação e operações em geral; **70%** na locação, cessão
onerosa e arrendamento.

**Redutor de ajuste (arts. 257–258):** abate da base o valor de aquisição atualizado (ou valor
de referência) do imóvel detido em 31/12/2026, mais custos. Guarde documentação de custo
**agora** — é o que reduz o imposto na venda futura.

**Redutor social:**
- alienação (art. 259): R$ 100 mil por imóvel residencial novo; R$ 30 mil por lote residencial
  (uma vez, IPCA);
- locação residencial (art. 260): **R$ 600 por imóvel residencial/mês** (confirmado).

**Fórmula simplificada (locação residencial por contribuinte):**
`IBS/CBS = (aluguel − redutor social) × alíquota de referência × (1 − 70%)`.
Ex.: aluguel R$ 3.000, alíq. ref. 28% → (3.000 − 600) × 28% × 30% = R$ 201,60/mês.
Use `scripts/rt_calc.py imovel` para simular.

**Regime transitório de locação (CST 221, art. 487):** alíquota total de **3,65% sobre a receita
bruta** para contratos por prazo determinado celebrados até a publicação da LC 214 (jan/2025),
com registro em cartório ou disponibilização à RFB/CGIBS **até 31/12/2025** (prazo encerrado). Não
acumula com o redutor social do art. 260. A LC 227 incluiu um §12 ⚠️ (conteúdo a verificar).

## 6. Cooperativas (arts. 271–272)
- Opção por alíquota zero no ato cooperativo (cooperado ↔ cooperativa).
- Transferência de créditos ao associado (CST 800002). Adesão por ato conjunto RFB/CGIBS.

## 7. Bares, restaurantes, hotelaria, parques e turismo
| Setor | Redução | Crédito ao adquirente |
|---|---|---|
| Bares e restaurantes (arts. 273–276) | 40% | não |
| Hotelaria, parques de diversão/temáticos (arts. 277–283) | 40% | não |
| Agências de turismo (arts. 289–290) | 40% sobre receita própria | conforme regra |

Para restaurante: base inclui gorjeta? A LC exclui gorjeta até limite ⚠️ — verificar antes de
afirmar. Fornecimento de alimentação a empregados por empresa: verificar crédito específico.

## 8. Outros
- **SAF / Tributação Específica do Futebol (Lei 14.193/2021, art. 31):** 5% nos 5 primeiros
  anos (federais) e depois 8,5% (4% federais + 1,5% CBS + 3% IBS) ⚠️ — LC 227 alterou; conferir.
- **Transporte coletivo** intermunicipal/interestadual e aviação regional: redução de 40% ⚠️.
- **Missões diplomáticas e organismos internacionais:** imunidade/isenção operada por
  reembolso ⚠️.
- **Sociedades cooperativas, entidades imunes (templos, partidos, sindicatos, entidades de
  educação/assistência sem fins lucrativos):** imunidade constitucional (CF art. 149-B c/c
  150, VI) — CST 410.
