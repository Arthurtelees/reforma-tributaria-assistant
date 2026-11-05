# Changelog

## [1.1.0] — 2026-11-05
Revisão completa (auditoria tributária + revisão de código) e testes de comportamento em 2 iterações.

### Corrigido
- **Percentuais na CLI agora são sempre em %** (`0.9` = 0,9%). Antes, valores ≤ 1 eram lidos como fração (0,9 virava 90%).
- **Simples Nacional**: faixa, alíquota efetiva e partilha do DAS agora vêm das tabelas oficiais da LC 123 (`assets/simples_anexos.json`) — o modelo errava a faixa quando calculava de memória.
- Limite do MEI atualizado pela **LC 238/2026** (R$ 110 mil em 2027, R$ 140 mil em 2028) e corte do nanoempreendedor.
- Regras de PF contribuinte em locação (regra dos 20% no próprio ano; IPCA) e alienação de imóveis (art. 251).
- Condições das profissões intelectuais (art. 127 §1º), prazos de ressarcimento (arts. 39–40), Imposto Seletivo sobre minerais (MP 1.399/2026), LC 225/2026, regime transitório de locação (art. 487).
- Validador de NF-e: lotes com várias notas, tolerância de totais ao centavo, `gDif`/`gDevTrib`, arquivos ilegíveis contados como erro, chave de acesso (DV, AAMM, nNF, cNF), código de saída 1 com erros.
- Consulta de cClassTrib: cabeçalho da planilha oficial, códigos numéricos, CSV em Windows-1252.
- Arredondamento comercial (meio para cima) com totais iguais à soma das parcelas.

### Adicionado
- Comandos `/rt-diagnostico`, `/rt-simples`, `/rt-validar-nfe`, `/rt-classificar`, `/rt-novidades`.
- `rt_calc.py das`; modo **preço neutro** no `simples`; perda de margem com preço fixo no `transicao`.
- Aviso automático quando os parâmetros têm mais de 90 dias.
- Referência `temas-complementares.md` (devoluções, compras governamentais, IBS/CBS na base do ICMS, créditos presumidos, importação…).
- 46 testes automatizados + CI (Linux/Windows, Python 3.9–3.13); casos de avaliação em `skills/reforma-tributaria/evals/`.

## [1.0.0] — 2026-11-05
- Primeira versão.
