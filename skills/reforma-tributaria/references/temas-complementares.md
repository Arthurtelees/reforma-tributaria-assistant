# Temas complementares (o que o contador pergunta depois do básico)

> Pontos de operação do dia a dia. Vários dependem de regulamentação fina ou têm leituras em
> disputa — quando houver ⚠️, repasse a ressalva e, com acesso à web, confirme no texto vigente
> (LC 214 compilada, RCBS — Decreto 12.955/2026, RIBS — Res. CGIBS 6/2026).

## Sumário
1. Devolução, cancelamento, notas de débito e crédito
2. Compras governamentais
3. IBS/CBS na base do ICMS/ISS durante a transição (controvérsia)
4. Aquisições de pessoa física e de não contribuintes (créditos presumidos)
5. Simples Nacional: migração entre DAS e regime regular
6. Importação de bens e serviços
7. Uso e consumo: como sustentar o crédito
8. Atualização monetária de limites

---

## 1. Devolução, cancelamento, notas de débito e crédito
- **Devolução** de bens/serviços: o fornecedor **estorna o débito** e o adquirente **estorna o
  crédito** correspondente (LC 214 art. 47 §8º, redação LC 227 ⚠️ conferir redação). A NF-e de
  devolução deve **referenciar o documento original** (`refNFe`/`DFeReferenciado` por item).
- Devolução vinda de adquirente **fora do regime regular** (consumidor final): o fornecedor estorna
  o débito; não há crédito a estornar do outro lado.
- **Cancelamento** dentro do prazo: anula débito e crédito; fora do prazo, use os novos tipos de
  **nota de crédito** (`finNFe` / `tpNFCredito`, ex.: 04 redução de valores) e **nota de débito**
  (`tpNFDebito`, ex.: 06 pagamento antecipado, 07 perda em estoque) — NT 2025.002-RTC ⚠️ códigos em evolução.
- **Carta de correção não serve** para alterar valores de tributo.
- Descontos incondicionais concedidos depois da emissão: nota de crédito, não "desconto informal".

## 2. Compras governamentais (LC 214 arts. 370–372 ⚠️ numeração)
- Nas aquisições por União, estados, DF, municípios, autarquias e fundações, as alíquotas de IBS/CBS
  são **reduzidas por um redutor** e a receita é destinada ao ente comprador.
- CBS 2027: redutor calculado pelo TCU de **44,16%** (pendente de confirmação pelo Senado).
- NF-e: grupo `gCompraGov` (ente, percentual de redução). Revise contratos administrativos
  (reequilíbrio — arts. 373–377) e a precificação de licitações a partir de 2027.

## 3. IBS/CBS na base do ICMS/ISS durante a transição ⚠️ controvérsia
- A base do **IBS/CBS exclui** ICMS, ISS e PIS/Cofins de 2026 a 2032 (LC 214 art. 12 §2º, V) — isso
  está pacificado no texto.
- O inverso — **IBS/CBS integrarem a base do ICMS** — é disputado: SEFAZ-SP (Respostas à Consulta
  32.303/2025 e 32.931) entende que **não integram em 2026** e **integram a partir de 2027**; SEFAZ-PE
  entende que integram já em 2026; há liminares. Antes de parametrizar o ICMS no ERP, confira a
  posição do **estado do emitente** e o andamento judicial.

## 4. Aquisições de pessoa física e de não contribuintes
O adquirente contribuinte do regime regular pode ter **crédito presumido** quando compra de:
- **produtor rural não contribuinte** (receita < R$ 3,6 mi — art. 168): percentuais fixados
  **anualmente** por ato conjunto RFB/CGIBS, podendo variar por produto/receita (§6º, LC 227);
- **transportador autônomo de carga PF** (art. 169);
- **resíduos sólidos e recicláveis** de PF/cooperativas (art. 170): IBS 1,3% (2029) … 13% (2033+), CBS 7%;
- **bens móveis usados** de PF para revenda (art. 171).
Sem regra específica, compra de PF **não gera crédito**. Mapear fornecedores PF/não contribuintes
é parte do diagnóstico de créditos. ⚠️ Percentuais vigentes para 2027 dependem do ato anual.

## 5. Simples Nacional: migração entre DAS e regime regular
- Opção semestral; quem recebeu **ressarcimento** no ano corrente ou anterior não pode voltar ao
  DAS (art. 41 §5º).
- Ao migrar para o Simples/MEI, os **prazos de ressarcimento ficam suspensos por até 5 anos**
  (art. 39 §10) — use os créditos antes de migrar.
- Tratamento de **créditos sobre estoque** na entrada/saída do regime regular ⚠️ depende de
  regulamentação — confirme no RCBS/RIBS antes de orientar.
- Sublimite estadual (R$ 3,6 mi) continua valendo para o IBS.

## 6. Importação
- **Bens:** IBS/CBS no **desembaraço aduaneiro**; base = valor aduaneiro + II + demais tributos e
  encargos (exceto o próprio IBS/CBS) ⚠️ conferir composição; crédito ao importador contribuinte.
  A partir de **01/01/2027** a **Duimp** substitui a NF-e de importação (Ato Conjunto 4/2026).
- **Serviços e bens imateriais do exterior** (ex.: nuvem, SaaS, licenças): devidos pelo
  **adquirente** contribuinte (que toma o crédito) ou pela **plataforma** quando houver; para o
  adquirente do regime regular, o efeito líquido tende a zero, mas a obrigação existe.

## 7. Uso e consumo: como sustentar o crédito
- O crédito é amplo, mas **vedado para uso e consumo pessoal** (art. 57, alterado pela LC 227).
- Boa prática: política interna de despesas, centro de custo vinculado à atividade, documento em
  nome da PJ, e registro da finalidade para itens "de fronteira" (veículos, celulares, viagens,
  alimentação, uniformes, EPI, saúde do empregado — estes últimos permitidos pelo §3º).

## 8. Atualização monetária de limites
Vários limites são corrigidos pelo IPCA: R$ 240 mil da locação PF (mensal — art. 251 §5º),
redutores sociais de imóveis (art. 259 §3º), R$ 3,6 mi do produtor rural (art. 167). Os scripts usam
valores nominais de `assets/parametros.json` — avise o usuário quando ele estiver perto do limite.
