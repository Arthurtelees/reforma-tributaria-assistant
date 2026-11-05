# Como contribuir

A reforma tributária muda toda semana. Contribuições que mantêm a skill correta são as mais valiosas.

## Regras de ouro
1. **Toda mudança de número, prazo ou artigo precisa de fonte oficial** (Planalto/DOU, CGIBS, Receita Federal, Portal NF-e, Senado). Cite a URL e a data da consulta no PR.
2. Alíquotas e cronograma ficam **só** em `skills/reforma-tributaria/assets/parametros.json`; tabelas do Simples em `assets/simples_anexos.json`. Não espalhe números pelo código.
3. Itens incertos recebem ⚠️ na referência, com o motivo.
4. Atualize `data_base` em `parametros.json` e registre no `CHANGELOG.md`.

## Rodando os testes
```bash
python -m unittest discover -s tests -v
```
Os scripts usam só a biblioteca padrão (Python 3.9+).

## Testes de comportamento da skill (opcional)
Os casos em `skills/reforma-tributaria/evals/` seguem o formato do `claude plugin eval`:
```bash
cd skills/reforma-tributaria && claude plugin eval . --allow-tools Write,Edit,Bash --scaffold
```
