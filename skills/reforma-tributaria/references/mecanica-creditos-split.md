# Mecânica do IBS/CBS: fato gerador, base, créditos, split payment, ressarcimento e cashback

## Sumário
1. Fato gerador, momento e local
2. Base de cálculo ("por fora")
3. Contribuintes e responsáveis
4. Não cumulatividade e crédito amplo
5. Vedações: uso e consumo pessoal
6. Extinção do débito e split payment
7. Ressarcimento
8. Cashback (devolução personalizada)
9. Erros conceituais comuns

---

## 1. Fato gerador, momento e local (LC 214)
- **Fato gerador:** operações onerosas com bens (materiais e imateriais, inclusive direitos) e
  serviços. Não onerosas só nos casos expressos (art. 4º §§1º–2º) — ex.: brindes e bonificações
  têm regras próprias (bonificação: cClassTrib 410001).
- **Momento:** fornecimento (art. 10). Fornecimento contínuo: o que ocorrer primeiro entre
  vencimento da parcela e pagamento (art. 10 §3º, LC 227). Pagamento antecipado: §§4º e 7º.
- **Local (destino), art. 11:** bem móvel → local da entrega; imóvel → onde situado; transporte de
  passageiros → início; carga → entrega; residual → domicílio do adquirente.
  Consequência: a alíquota do IBS é a do **estado + município do adquirente/entrega**, não do
  vendedor. Cadastro de clientes com município correto (código IBGE) vira dado fiscal crítico.

## 2. Base de cálculo (art. 12)
**Inclui:** valor da operação, acréscimos, juros, multas, descontos **condicionais**, tributos
cobrados do fornecedor (inclusive IS).
**Exclui:** o próprio IBS e CBS (**cálculo "por fora"**), IPI, descontos **incondicionais**,
certos reembolsos e, **de 2026 a 2032, ICMS, ISS, PIS/Cofins** (inciso V).
Partes relacionadas: valor de mercado (§4º). Arbitramento: art. 13.

```
Base IBS/CBS = valor da operação − descontos incondicionais − ICMS/ISS/PIS/Cofins (transição)
CBS = Base × alíq. CBS × (1 − redução)
IBS = Base × (alíq. IBS UF + alíq. IBS Mun) × (1 − redução)
Total a pagar pelo cliente = Valor + CBS + IBS (+ IPI/IS quando houver)
```
"Por fora" muda a percepção: alíquota nominal de 28% por fora ≈ 21,9% "por dentro"
(`28/128`). Para comparar com a carga atual (ICMS/PIS/Cofins por dentro), converta sempre.

## 3. Contribuintes e responsáveis
- **Contribuinte** (art. 21): fornecedor habitual, importador, adquirente em leilão.
- **Não contribuintes** (art. 26): condomínios, certos fundos, nanoempreendedor, produtor rural
  < R$ 3,6 mi (podem optar pelo regime regular em alguns casos).
- **Plataformas digitais** (art. 22): responsáveis solidárias ou substitutas conforme o
  fornecedor seja/não residente e cadastrado; responsabilidade limitada com split payment (§7º).
- **Responsabilidade do adquirente** quando paga sem split e o fornecedor não recolhe — risco
  real de "crédito que não nasce" (ver §4).

## 4. Não cumulatividade e crédito amplo (arts. 47–56)
- Crédito de **tudo** que foi adquirido com IBS/CBS (bens, serviços, uso e consumo, ativo),
  exceto uso/consumo pessoal (art. 57). Fim da discussão de "insumo" do PIS/Cofins.
- **Condição:** o crédito nasce com a **extinção do débito pelo fornecedor** (pagamento, split,
  recolhimento pelo adquirente) — art. 47. Fornecedor inadimplente = cliente sem crédito.
- Crédito IBS e CBS **separados** (§1º); valor = destacado no documento ou crédito presumido (§2º).
- Compra de optante do Simples (DAS): crédito só do valor efetivamente pago no Simples (§9º).
- Operações imunes, isentas, alíquota zero, diferidas, suspensas → não geram crédito ao
  adquirente, salvo crédito presumido (art. 49).
- Uso: débitos vencidos → do período → futuros, ou ressarcimento (art. 53). **Prazo: 5 anos** (art. 54).
- Intransferível, salvo reorganização societária (art. 55; CST 800).

## 5. Vedações: uso e consumo pessoal (art. 57)
Sem crédito: joias, pedras e metais preciosos; obras de arte e antiguidades; bebidas
alcoólicas; fumígenos; armas e munições; bens e serviços recreativos, esportivos e estéticos;
fornecimentos gratuitos/abaixo do mercado a sócios, administradores, empregados e parentes até
3º grau. **Exceções (§3º):** uniformes, EPI, saúde do empregado, itens de uso predominante na
atividade. LC 227 alterou o art. 57 — confira a redação vigente antes de parecer.

## 6. Extinção do débito e split payment (arts. 27, 31–36)
Formas de extinção: compensação com créditos; pagamento pelo contribuinte; **split payment**;
recolhimento pelo adquirente; pagamento pelo responsável.

**Split payment (pagamento cindido):** no momento da liquidação financeira (cartão, Pix,
boleto, TED), o prestador de serviço de pagamento separa o IBS/CBS e envia direto ao fisco.
- **Modelo padrão** (art. 32): consulta à plataforma, desconta débito já compensado com créditos.
- **Modelo simplificado** (art. 33): percentual pré-fixado (pensado para varejo/B2C).
- Recolhimento pelo adquirente (art. 36): adquirente do regime regular quando o meio de
  pagamento não segrega.
- Cronograma: testes técnicos com PSPs desde 15/10/2026; 2027 implantação gradual (adesão
  facultativa no B2B a partir do 2º semestre ⚠️); obrigatoriedade provável em 2028 ⚠️.

**Impacto de caixa:** hoje a empresa vende, recebe e paga ICMS/PIS/Cofins no mês seguinte
(financiamento implícito de ~30–50 dias). Com split, o tributo **não entra no caixa**. Projete:
`perda de capital de giro ≈ (débito médio mensal − créditos) × prazo médio de recolhimento atual`.

## 7. Ressarcimento (arts. 39–40)
| Situação | Prazo |
|---|---|
| Participante de programa de conformidade **e** pedido enquadrado no art. 40 | 30 dias |
| Pedido enquadrado no art. 40: (I) créditos de ativo imobilizado; ou (II) valor ≤ 150% da **média mensal da diferença entre créditos e débitos** dos 24 meses anteriores (sem imobilizado) | 60 dias |
| Demais | 180 dias |
Sem decisão no prazo: ressarcimento em 15 dias (§4º). Fiscalização suspende o prazo (máx. 360
dias; §§5º–7º). Selic a partir do 2º mês (§9º). Prazos suspensos por até 5 anos para quem migra
ao Simples/MEI (§10). Isto é muito melhor que o acúmulo crônico de saldo credor de ICMS hoje.

## 8. Cashback — devolução personalizada (arts. 112–124)
- **Quem:** famílias no CadÚnico com renda per capita ≤ ½ salário mínimo, CPF regular,
  residentes. Inclusão automática.
- **Quanto (art. 118):**
  - botijão GLP até 13 kg, energia elétrica, água, esgoto, gás canalizado e telecom:
    **100% da CBS e 20% do IBS**;
  - demais: **20% da CBS e 20% do IBS**.
  - Entes podem ampliar por lei (exceto os 100% da CBS, que são fixos).
- **Como:** na própria fatura (utilidades) ou crédito posterior; limitado ao ônus suportado.
- **Início:** CBS jan/2027; IBS jan/2029.
- **Dica para PF:** sempre informe o **CPF na nota** — é assim que o consumo é identificado.

## 9. Erros conceituais comuns (corrija quando aparecerem)
- "IVA de 28% vai aumentar tudo em 28%" — não: substitui PIS/Cofins/IPI/ICMS/ISS, é por fora e
  gera crédito integral nas etapas anteriores. O efeito real depende do setor.
- "Serviços vão pagar menos" — em geral **pagam mais** (hoje ISS 2–5% + PIS/Cofins cumulativo 3,65%
  vs IVA ~28%), exceto quando o cliente é contribuinte e toma crédito.
- "Crédito é automático" — depende do pagamento pelo fornecedor (art. 47).
- "Simples não muda nada" — muda para quem vende B2B (crédito do cliente).
- "2026 já é para pagar" — 2026 é teste, com dispensa condicionada ao cumprimento das
  obrigações acessórias.
