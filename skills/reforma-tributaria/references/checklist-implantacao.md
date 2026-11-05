# Checklist de implantação e diagnóstico (empresas e escritórios contábeis)

Use este arquivo para montar **plano de ação**, **diagnóstico de impacto** ou **checklist de
prontidão**. Adapte prioridades ao porte, regime e setor. Datas de referência: nov/2026.

## Fase 0 — Urgente (até 31/12/2026)
- [ ] Emitir DF-e com grupo IBS/CBS conforme o cronograma do Ato Conjunto 4/2026 (dispensa de
      recolhimento em 2026 depende disso).
- [ ] Monitorar comunicações do **PNCT**, corrigir inconsistências até 31/12/2026, designar
      contador responsável.
- [ ] Simples Nacional: confirmar decisão para 1º semestre/2027 (cancelamento da opção pelo
      regime regular até 20/12/2026 ⚠️).
- [ ] Fechar e documentar créditos de PIS/Cofins (último ano de apuração).
- [ ] DeRE (setores obrigados): eventos mensais desde out/2026.
- [ ] Atualizar cClassTrib para a tabela vigente (IT 2025.002-RT v1.71).
- [ ] NF-e: aplicar NT 2025.002 v1.52/1.53 (monofasia em produção 16/11/2026).

## Fase 1 — Cadastros e sistemas
- [ ] Saneamento de NCM e NBS de todo o cadastro de itens.
- [ ] Mapear NCM/NBS → CST + cClassTrib + base legal + vigência (ver `documentos-fiscais.md`).
- [ ] Cadastro de clientes: município (código IBGE) correto — IBS é do **destino**.
- [ ] Cadastro de fornecedores: regime (Simples DAS / Simples regime regular / normal / não
      contribuinte / produtor rural) — define o crédito.
- [ ] Motor de cálculo: base sem ICMS/ISS/PIS/Cofins; redução na alíquota; arredondamento;
      validação contra a calculadora oficial RFB (API).
- [ ] ERP: notas de débito e crédito, `vItem`, `vNFTot`, devoluções referenciadas.
- [ ] Integração com apuração assistida (APIs CBS/IBS).
- [ ] Testes em homologação (onde a Rejeição 1115 já é aplicada).

## Fase 2 — Impacto financeiro
- [ ] **Diagnóstico de carga**: carga atual × carga 2027 × 2029–2032 × 2033 por linha de
      produto/serviço (use `rt_calc.py transicao`).
- [ ] **Precificação**: novo preço "por fora" que mantém a margem (use `rt_calc.py preco`).
- [ ] **Fluxo de caixa**: efeito do split payment no capital de giro.
- [ ] **Créditos**: mapear despesas hoje sem crédito que passam a gerar (energia, serviços,
      uso e consumo, ativo) — ganho relevante para serviços e indústria.
- [ ] Saldo credor de ICMS: inventário e estratégia de monetização até 2032.
- [ ] Benefícios fiscais de ICMS: perda de valor 2029–2032 e Fundo de Compensação.

## Fase 3 — Comercial, contratos e cadeia
- [ ] Revisar contratos de longo prazo (cláusulas em `transicao-saldos-contratos.md`).
- [ ] Renegociar com fornecedores do Simples (crédito reduzido) ou exigir opção pelo regime regular.
- [ ] Comunicar clientes B2B sobre o crédito que passarão a ter (argumento comercial).
- [ ] Revisar estrutura logística/societária baseada em benefícios de ICMS (guerra fiscal
      perde sentido com o princípio do destino).

## Fase 4 — Governança
- [ ] Responsável pela reforma (comitê fiscal + TI + financeiro + comercial).
- [ ] Rotina de monitoramento de NTs, Informes Técnicos, atos conjuntos e resoluções.
- [ ] Trilha de auditoria XML × ERP × apuração assistida.
- [ ] Treinamento de faturamento, compras e comercial.

## Roteiro para escritório de contabilidade (carteira de clientes)
1. **Segmentar a carteira** por regime (Simples, Presumido, Real), setor e perfil (B2B/B2C).
2. **Priorizar** clientes: (a) Simples com vendas B2B relevantes (decisão semestral);
   (b) prestadores de serviço do Lucro Presumido (maior aumento de carga);
   (c) setores com regime específico (imóveis, saúde, restaurantes, financeiro);
   (d) exportadores com saldo credor.
3. Produzir para cada cliente: diagnóstico de 1 página + recomendação de regime + plano de
   ação com datas (use `assets/modelo-diagnostico.md`).
4. Rever honorários/escopo: apuração assistida, DeRE, conferência de créditos e split são novos serviços.

## Perguntas para entrevistar o cliente (coleta de dados)
1. CNPJ, regime tributário atual, CNAE principal e secundários, UF/município.
2. Faturamento 12 meses; % vendas para PJ contribuintes × consumidor final × governo × exterior.
3. Principais produtos/serviços com NCM/NBS e preço médio.
4. Alíquotas atuais efetivas: ICMS, ISS, PIS/Cofins (cumulativo/não cumulativo), IPI.
5. Principais custos e despesas; % adquirido de fornecedores do Simples.
6. Benefícios fiscais vigentes; saldo credor de ICMS; créditos de PIS/Cofins acumulados.
7. Prazo médio de recebimento e de recolhimento de tributos.
8. Contratos de longo prazo relevantes.
9. ERP utilizado e emissor de NF-e/NFS-e.
