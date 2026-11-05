# Documentos fiscais eletrônicos, CST e cClassTrib

> Datas e versões de NT mudam por comunicado. Sempre confira o Portal NF-e
> (https://www.nfe.fazenda.gov.br → Notas Técnicas / Avisos) e o Portal DF-e SVRS
> (https://dfe-portal.svrs.rs.gov.br) antes de afirmar uma data.

## Sumário
1. Cronograma de obrigatoriedade (Ato Conjunto RFB/CGIBS 4/2026)
2. NF-e/NFC-e — NT 2025.002-RTC
3. Estrutura XML do grupo IBSCBS
4. CST e cClassTrib
5. NFS-e Padrão Nacional e demais DF-e
6. DeRE, apuração assistida e calculadora oficial
7. Erros frequentes na emissão

---

## 1. Cronograma de obrigatoriedade (fatos geradores a partir de)

| Data | Documentos |
|---|---|
| **03/08/2026** | NF-e (55), NFC-e (65), CT-e (57), CT-e OS (67), MDF-e (58), GTV-e (64), NF3e (66), DC-e (99), NFS-e Via, BP-e (63) em geral |
| **01/10/2026** | NFS-e (LC 116 em geral, exceto subitens 1.03, 1.05, 1.09 e 16.01), NFCom (62), DIR, DeRE – eventos de tabela |
| **15/11/2026** | DeRE – eventos periódicos mensais (1ª entrega: competência outubro/2026) |
| **01/12/2026** | NFS-e de plataformas digitais (art. 22), streaming/software (1.03, 1.05, 1.09), transporte municipal (16.01), bens imateriais, condomínios, locações; BP-e semiurbano/metropolitano/aéreo; NFGas (76), NFAg (75), NF-e ABI (77); **NF-e de não contribuintes de ICMS** |
| **01/01/2027** | **Simples Nacional (todos os DF-e)**; NF-e com operações monofásicas; Duimp na importação; demais eventos DeRE |

Fonte oficial: https://www.cgibs.gov.br/upload/arquivos/202607/31091735-20260730-16h30-ato-conjunto-rfb-cgibs-na-c2-ba-4-260731-090909.pdf

**Rejeição automática ainda suspensa:** o Ato Técnico Conjunto 1/2026 deixou a regra UB12-10
(Rejeição 1115 – "Grupo IBSCBS não informado") como "implementação futura" em produção.
NF-e sem o grupo ainda é autorizada, **mas a obrigação existe** e gera comunicações do PNCT.
Quando o grupo é informado, as validações de cálculo **já são aplicadas em produção**.

## 2. NF-e/NFC-e — NT 2025.002-RTC
Versões: 1.30/1.33 (2025) → 1.40 → 1.50 (monofasia) → 1.51 (04/08/2026) → **1.52** (01/10/2026;
homologação 26/10, produção **16/11/2026**: nova monofasia `gMonoPadrao/gMonoReten/gMonoRet/gMonoDif`,
regra VC02-50) → **1.53** (30/10/2026: reescreve VC02-14; `refNFe` no cabeçalho ou item).
Novidades relevantes: `vItem` por item (Rej. 1137 quando há `gIBSCBS`, data ⚠️), total `vNFTot`,
**nota de débito** (`finNFe`=… `tpNFDebito` 06 pagamento antecipado, 07 perda em estoque) e
**nota de crédito** (`tpNFCredito` 04 redução de valores) ⚠️ códigos em evolução.

## 3. Estrutura XML do grupo IBSCBS (por item, `det/imposto`)

```xml
<IBSCBS>
  <CST>000</CST>
  <cClassTrib>000001</cClassTrib>
  <gIBSCBS>
    <vBC>1000.00</vBC>
    <gIBSUF><pIBSUF>0.1000</pIBSUF><vIBSUF>1.00</vIBSUF></gIBSUF>
    <gIBSMun><pIBSMun>0.0000</pIBSMun><vIBSMun>0.00</vIBSMun></gIBSMun>
    <vIBS>1.00</vIBS>
    <gCBS><pCBS>0.9000</pCBS><vCBS>9.00</vCBS></gCBS>
  </gIBSCBS>
</IBSCBS>
```
- Percentuais em formato "0.9000" = 0,9%. 2026: CBS 0,9%, IBS UF 0,1%, IBS Mun 0%.
- Subgrupos condicionais: `gRed` (`pRedAliq`, `pAliqEfet`) dentro de gIBSUF/gIBSMun/gCBS;
  `gDif` (diferimento); `gDevTrib` (devolução de tributos/cashback); `gTribRegular`;
  `gCredPres`; `gCompraGov`; grupos de monofasia.
- Imposto Seletivo: grupo `IS` próprio (CSTIS, cClassTribIS, vBCIS, pIS, vIS).
- Totais: `ICMSTot` + `IBSCBSTot` (com `gIBS`, `gCBS`) + `ISTot`; `vNFTot`.
- ⚠️ Nomes de subgrupos: confirme contra o XSD do pacote de schemas vigente.
- Use `scripts/validar_nfe.py` para checar XMLs.

## 4. CST e cClassTrib
**Tabela oficial:** Informe Técnico **2025.002-RT** (versão 1.71 vigente em nov/2026; v1.70 trouxe
9 códigos novos, implantação até 16/10/2026).
- Download (Portal NF-e): https://www.nfe.fazenda.gov.br/portal/exibirArquivo.aspx?conteudo=Lt6DZCZap0g=
- Consulta online (Conformidade Fácil/SVRS): https://dfe-portal.svrs.rs.gov.br/CFF/ClassificacaoTributaria

**Estrutura:** `cClassTrib` = 6 dígitos = **CST (3) + sequencial (3)**. A planilha traz, para
cada código: base legal (artigo LC 214, RCBS, RIBS), `pRedIBS`, `pRedCBS`, indicadores de
grupos obrigatórios (`ind_gTribRegular`, `ind_gCredPresOper`, `ind_gMono*`, `ind_gEstornoCred`),
vigência (`dIniVig`/`dFimVig`) e em quais DF-e o código é aceito.

| CST | Descrição | Exemplos de cClassTrib |
|---|---|---|
| 000 | Tributação integral | 000001 operações tributadas integralmente |
| 010 | Alíquotas uniformes | 010001 FGTS (operações não realizadas pela Caixa) |
| 011 | Alíquotas uniformes reduzidas | 011001 assistência funerária; 011002 planos de saúde; 011004 prognósticos |
| 200 | Alíquota reduzida (inclui zero) | 200003 Cesta Básica (zero); 200009 medicamentos Anexo XIV (zero); 200014 hortícolas/frutas/ovos (zero); 200028 educação (−60%); 200029 saúde (−60%); 200034 alimentos Anexo VII (−60%); 200047 bares e restaurantes (−40%); 200052 profissões intelectuais (−30%) |
| 220 | Alíquota fixa | 220001–220003 (encerrados na v1.60) |
| 221 | Alíquota fixa proporcional | 221001 locação de imóvel sobre receita bruta |
| 222 | Redução de base de cálculo | — |
| 400 | Isenção | 400001 transporte público coletivo |
| 410 | Imunidade e não incidência | 410001 bonificações; 410002 transferências entre estabelecimentos; 410003 doações; 410004 exportações; 410008 livros e papel; 410014 produtor rural não contribuinte |
| 510 | Diferimento | 510001 energia elétrica |
| 515 | Diferimento com redução | — |
| 550 | Suspensão | 550001 exportação (comercial exportadora); 550008–550013 Repetro; 550014 ZPE; 550016 Reidi |
| 620 | Tributação monofásica | 620001 combustíveis; 620002/620003 retenção |
| 800 | Transferência de crédito | 800001 fusão/cisão/incorporação; 800002 cooperado→cooperativa |
| 810 | Ajuste de IBS na ZFM | 810001 crédito presumido ZFM |
| 811 | Ajustes | — |
| 820 | Tributação em documento/declaração específica | 820001 planos de saúde (DeRE); 820005 alienação de imóveis |
| 830 | Exclusão de base de cálculo | — |

> ⚠️ Os exemplos vêm de fontes secundárias. **Sempre confira o cClassTrib exato na tabela
> oficial vigente** antes de parametrizar ERP. O antigo CST 210 (redutor de base imobiliário)
> não aparece na contagem da v1.71 — verificar.

**Mapeamento NCM/NBS → CST/cClassTrib (método):**
1. Partir do NCM (bens) ou NBS (serviços) correto.
2. Verificar Anexos da LC 214 (I, II–XV) e regimes específicos.
3. Considerar destinatário (órgão público → `gCompraGov`; imune; produtor rural), CFOP e
   finalidade (bonificação, transferência, devolução, exportação).
4. Escolher o cClassTrib e conferir os indicadores de grupo exigidos.
5. Gravar no cadastro: CST, cClassTrib, base legal, versão da tabela, data de vigência.
6. Revisar a cada nova versão do Informe Técnico.

## 5. NFS-e Padrão Nacional e demais DF-e
- Municípios obrigados a aderir ao padrão nacional ou compartilhar dados com o Ambiente de
  Dados Nacional desde **01/01/2026** (LC 214 art. 62 §1º). Ainda há municípios em transição.
- Grupo IBS/CBS na NFS-e: NTs CGNFS-e 008 e 009. Ausência não rejeita, mas é desconformidade.
- Serviço é classificado pela **NBS** + código de tributação nacional; a NBS define o cClassTrib.
- ME/EPP do Simples: obrigação de usar Emissor Nacional por Resolução CGSN ⚠️ (189 ou 191/2026).
- CT-e, CT-e OS, BP-e, NFCom, NF3e, NFAg, NFGas, NF-e ABI, DC-e, GTV-e, DIR, Duimp: todos com
  grupo IBS/CBS por NTs próprias (Portal DF-e SVRS).

## 6. DeRE, apuração assistida e calculadora oficial
- **DeRE** (Declaração de Regimes Específicos): serviços financeiros, planos de saúde,
  funerários, saúde animal, prognósticos. Eventos mensais até o dia 15 do mês seguinte
  (1ª: out/2026). Manual 1.1.0 (CGIBS).
- **Apuração assistida** (LC 214 art. 46): o fisco monta débitos e créditos a partir dos DF-e; o
  contribuinte confere e ajusta. APIs da CBS: débitos/créditos (out/2026), pagamentos
  (nov/2026). API do IBS em teste. Efeito financeiro a partir de 2027.
- **SPED/EFD:** sem alteração oficial para IBS/CBS identificada; EFD-Contribuições segue para
  PIS/Cofins até a extinção ⚠️.
- **Calculadora oficial RFB** (web, offline e API REST para ERPs):
  https://piloto-cbs.tributos.gov.br/servico/calculadora-consumo/calculadora — use-a para
  conferir os cálculos da skill quando houver dúvida.

## 7. Erros frequentes na emissão
1. CST incompatível com o cClassTrib (os 3 primeiros dígitos devem coincidir).
2. Redução aplicada na base em vez da alíquota (`gRed` mal preenchido).
3. `vBC` incluindo ICMS/PIS/Cofins (devem ser excluídos na transição).
4. Alíquota de IBS do município/UF do **emitente** em vez do destino.
5. Arredondamento por item vs total — somatório dos itens deve bater com `IBSCBSTot`.
6. Bonificação/brinde tratados como venda (ou o contrário).
7. Devolução sem referenciar o documento original (`refNFe`/`DFeReferenciado`).
8. cClassTrib com vigência encerrada (`dFimVig`).
