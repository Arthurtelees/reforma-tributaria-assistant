<div align="center">

# 🇧🇷 Reforma Tributária Assistant

**O copiloto da Reforma Tributária do consumo dentro do Claude Code.**
IBS · CBS · Imposto Seletivo · transição 2026–2033 · NF-e/cClassTrib · Simples Nacional · split payment · precificação

[![testes](https://github.com/Arthurtelees/reforma-tributaria-assistant/actions/workflows/testes.yml/badge.svg)](https://github.com/Arthurtelees/reforma-tributaria-assistant/actions/workflows/testes.yml)
![License: MIT](https://img.shields.io/badge/license-MIT-green.svg)
![Claude Code](https://img.shields.io/badge/Claude%20Code-plugin%20%2B%20skill-orange)
![Base legal](https://img.shields.io/badge/base-LC%20214%20%C2%B7%20LC%20227%20%C2%B7%20LC%20238-blue)
![Atualizado](https://img.shields.io/badge/data--base-05%2F11%2F2026-informational)
![Python](https://img.shields.io/badge/python-3.9%2B-blue)

</div>

---

A reforma tributária substitui PIS, Cofins, IPI, ICMS e ISS por um **IVA dual** (CBS federal + IBS
estadual/municipal) e cria o **Imposto Seletivo**. São mais de 500 artigos de lei complementar,
dois regulamentos, dezenas de notas técnicas e uma transição que vai de 2026 a 2033.

Este plugin transforma o Claude Code em um especialista que **explica, calcula, valida e planeja**
— para o **departamento contábil e fiscal**, para o **escritório de contabilidade** com uma
carteira de clientes e para a **pessoa física** que quer entender o que muda no próprio bolso.

> **Por que confiar nos números?** A base de conhecimento foi auditada contra fontes oficiais
> (Planalto, CGIBS, Receita Federal, Portal NF-e, Senado), os cálculos são feitos por scripts
> testados (46 testes automatizados) e a skill foi avaliada em casos reais com e sem ela — veja
> [Qualidade](#-qualidade).

## ✨ O que faz

| Para quem | Exemplos |
|---|---|
| 🧾 **Contador / fiscal** | Classificar NCM/NBS em CST + cClassTrib · auditar lotes de XML de NF-e no grupo `IBSCBS` · regras de crédito, base e destino com artigo de lei · prazos do Ato Conjunto RFB/CGIBS 4/2026 |
| 🏢 **Empresa** | Carga 2026–2033 por produto · preço que mantém a margem · perda de margem se o preço não subir · efeito do split payment no caixa · revisão de contratos · diagnóstico com plano de ação |
| 📊 **Escritório contábil** | Priorizar a carteira por risco · Simples "dentro do DAS" × regime regular com números · diagnósticos padronizados por cliente |
| 👤 **Pessoa física** | O que fica mais caro ou mais barato · cashback · aluguel e venda de imóveis · herança e doação (ITCMD) · autônomo, MEI e nanoempreendedor |

## 🚀 Instalação

### Claude Code (recomendado — plugin com skill + comandos)

```
/plugin marketplace add Arthurtelees/reforma-tributaria-assistant
/plugin install reforma-tributaria@reforma-tributaria-marketplace
```

### Só a skill (cópia manual)

```bash
git clone https://github.com/Arthurtelees/reforma-tributaria-assistant.git
cp -r reforma-tributaria-assistant/skills/reforma-tributaria ~/.claude/skills/
```

Windows (PowerShell): `Copy-Item -Recurse reforma-tributaria-assistant\skills\reforma-tributaria $env:USERPROFILE\.claude\skills\`

### Claude.ai / Claude Desktop

Baixe o `reforma-tributaria.skill` na página de [Releases](https://github.com/Arthurtelees/reforma-tributaria-assistant/releases)
e envie em **Configurações → Capabilities → Skills**.

## 🗓️ Como usar no dia a dia

A skill é ativada **sozinha** quando você fala de reforma tributária — basta conversar. Os
comandos abaixo são atalhos para as tarefas mais frequentes.

| Comando | Quando usar | Exemplo |
|---|---|---|
| `/rt-diagnostico` | Cliente novo, reunião de planejamento, relatório para a diretoria | `/rt-diagnostico indústria de embalagens, Lucro Real, SP, fatura R$ 2 mi/mês, 90% B2B, ICMS 18%` |
| `/rt-simples` | Decidir a opção semestral do Simples (DAS × regime regular) | `/rt-simples anexo III, RBT12 1,2 mi, receita 100 mil/mês, 85% B2B, compras 30 mil/mês` |
| `/rt-validar-nfe` | Fechamento do mês, homologação do ERP, depois de mudar o cadastro | `/rt-validar-nfe ./xml/outubro` |
| `/rt-classificar` | Cadastro de produtos/serviços, parametrização do ERP | `/rt-classificar ./cadastro-produtos.csv` |
| `/rt-novidades` | Toda semana (ou quando sair notícia) — atualiza alíquotas e prazos | `/rt-novidades alíquota CBS 2027` |

**Rotina sugerida para um departamento contábil**

- **Diariamente:** pergunte em linguagem natural ("qual cClassTrib para venda de pão de forma?",
  "nota de devolução precisa de IBS/CBS?").
- **No fechamento mensal:** `/rt-validar-nfe` na pasta de XMLs do mês; corrija o cadastro de onde
  vierem os erros repetidos.
- **Semanalmente:** `/rt-novidades` — a skill confere as fontes oficiais e propõe a atualização de
  `parametros.json` (só aplica com sua confirmação).
- **Por cliente, uma vez por semestre:** `/rt-diagnostico` e, para optantes do Simples, `/rt-simples`
  antes de cada janela de opção (setembro e março).

**Para a pessoa física:** pergunte do seu jeito — "tenho 4 apartamentos alugados, vou pagar IBS?",
"o que muda no preço do supermercado?", "vale doar o imóvel aos meus filhos agora?".

## 🧰 Ferramentas incluídas (Python, só biblioteca padrão)

Os scripts ficam em `skills/reforma-tributaria/scripts/` e também funcionam direto no terminal.
**Percentuais são sempre em %** (`18` = 18%, `0.9` = 0,9%). `--json` em qualquer posição.

| Script / modo | O que faz |
|---|---|
| `rt_calc.py cronograma` | Alíquotas e regras ano a ano, em 4 cenários |
| `rt_calc.py operacao` | IBS/CBS/IS de uma operação, com reduções |
| `rt_calc.py transicao` | Carga 2026–2033 mantendo a margem, perda de margem com preço fixo, créditos de compras |
| `rt_calc.py das` | Faixa, alíquota efetiva e partilha do DAS pelas tabelas oficiais da LC 123 |
| `rt_calc.py simples` | DAS × regime regular (repasse total e **preço neutro**) |
| `rt_calc.py imovel` | Locação e venda (redutores, reduções, teste de PF contribuinte) |
| `rt_calc.py cashback` / `converter` | Devolução estimada; alíquota por dentro ⇄ por fora |
| `validar_nfe.py` | Auditoria de lotes de NF-e/NFC-e: grupo IBSCBS, CST×cClassTrib, recálculo com `gRed`/`gDif`, totais, chave de acesso; CSV e código de saída para CI |
| `consultar_cclasstrib.py` | Busca CST/cClassTrib (referência embutida ou planilha oficial do IT 2025.002-RT) |

```bash
python skills/reforma-tributaria/scripts/rt_calc.py transicao --valor 80000 --iss 2 --pis-cofins 3.65 --reducao 60
```

```
| Ano  | Receita líquida (preço fixo) | Variação vs hoje |
| 2026 | R$ 75.480,00                 | R$ 0,00          |
| 2027 | R$ 75.074,49                 | R$ -405,51       |
| 2033 | R$ 71.428,57                 | R$ -4.051,43     |
```
*(Clínica de saúde no Lucro Presumido, R$ 80 mil/mês, pacientes PF, cenário de 30%.)*

## 🗂️ Estrutura

```
reforma-tributaria-assistant/
├── .claude-plugin/          # manifesto do plugin e do marketplace
├── commands/                # /rt-diagnostico, /rt-simples, /rt-validar-nfe, /rt-classificar, /rt-novidades
├── skills/reforma-tributaria/
│   ├── SKILL.md             # fluxo, formatos de saída, princípios
│   ├── references/          # 12 arquivos de conhecimento carregados sob demanda
│   ├── scripts/             # rt_calc.py, validar_nfe.py, consultar_cclasstrib.py
│   ├── assets/              # parametros.json, simples_anexos.json, cclasstrib_referencia.csv, modelo-diagnostico.md
│   └── evals/               # casos de avaliação (formato claude plugin eval)
├── tests/                   # 46 testes automatizados
└── examples/                # XMLs de exemplo
```

## ✅ Qualidade

- **Auditoria tributária** de toda a base contra fontes oficiais — itens incertos ficam marcados com ⚠️.
- **Revisão de código** e 46 testes (cálculos, validador, consulta), rodando em Linux e Windows, Python 3.9–3.13.
- **Avaliação de comportamento** em 3 casos reais (decisão do Simples, auditoria de XML, diagnóstico de clínica), com e sem a skill.
  - Iteração 2: **100%** dos critérios com a skill × 94% sem ela.
  - Sem a skill, o modelo errou a alíquota do DAS nas duas rodadas e errou prazos do Simples na primeira.

## 🔄 Mantendo atualizado

A reforma ainda está em movimento. Pendências na data-base (05/11/2026):

- **Alíquota da CBS de 2027:** o TCU calculou 11,3% (aplicável 11,2%) e falta a resolução do Senado.
- **Alíquota de referência do IBS:** ainda não fixada.
- **Imposto Seletivo:** depende da conversão da MP 1.399/2026 em lei.
- **Split payment:** cronograma obrigatório não definido.
- **NF-e:** datas de rejeição ainda não fixadas.

Os scripts **avisam** quando os parâmetros têm mais de 90 dias. Para atualizar, rode
`/rt-novidades` ou edite `skills/reforma-tributaria/assets/parametros.json`.

Contribuições são bem-vindas — veja [CONTRIBUTING.md](CONTRIBUTING.md). Toda mudança de número
precisa de fonte oficial.

## ⚖️ Aviso

Ferramenta de apoio. Não substitui parecer de contador ou advogado tributarista responsável.
As simulações usam alíquotas de referência ainda estimadas e normas sujeitas a alteração.
Confirme na fonte oficial antes de decisões de alto valor.

## 📄 Licença

MIT
