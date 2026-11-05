#!/usr/bin/env python3
"""
consultar_cclasstrib.py — Busca CST / cClassTrib do IBS/CBS por código ou palavra-chave.

Uso:
  python consultar_cclasstrib.py "cesta basica"
  python consultar_cclasstrib.py 200 --json
  python consultar_cclasstrib.py restaurante --tabela "Tabela IT 2025.002 v.1.71 - cClassTrib.xlsx"

Sem --tabela usa a referência resumida em ../assets/cclasstrib_referencia.csv (exemplos principais,
NÃO é a tabela completa). Com --tabela, lê a planilha oficial do Informe Técnico 2025.002-RT
(.xlsx via openpyxl, se instalado, ou .csv exportado — UTF-8 ou Windows-1252) e pesquisa em todas
as colunas.
Download da oficial: https://www.nfe.fazenda.gov.br (Informe Técnico 2025.002-RT) ou
https://dfe-portal.svrs.rs.gov.br/CFF/ClassificacaoTributaria

Busca numérica: 3 dígitos = CST; 6 dígitos = cClassTrib; outros números são buscados como texto.
"""
from __future__ import annotations

import argparse
import csv
import io
import json
import sys
import unicodedata
from pathlib import Path

REF = Path(__file__).resolve().parent.parent / "assets" / "cclasstrib_referencia.csv"


def norm(s) -> str:
    s = "" if s is None else str(s)
    return "".join(c for c in unicodedata.normalize("NFKD", s.lower()) if not unicodedata.combining(c))


def eh_coluna_codigo(nome: str) -> str | None:
    n = norm(nome)
    if "class" in n:
        return "cclasstrib"
    if n.startswith("cst") or n in ("codigo cst", "cst-ibs/cbs", "cst ibs/cbs"):
        return "cst"
    return None


def normaliza_codigo(chave: str, valor) -> str:
    """Planilhas gravam '000001' como número 1; restaura os zeros à esquerda."""
    tipo = eh_coluna_codigo(chave)
    if tipo and isinstance(valor, (int, float)) and float(valor).is_integer():
        return str(int(valor)).zfill(6 if tipo == "cclasstrib" else 3)
    return "" if valor is None else str(valor).strip()


def ler_texto(p: Path) -> str:
    bruto = p.read_bytes()
    for enc in ("utf-8-sig", "cp1252"):
        try:
            return bruto.decode(enc)
        except UnicodeDecodeError:
            continue
    return bruto.decode("latin-1")


def ler_csv(p: Path) -> list[dict]:
    texto = ler_texto(p)
    try:
        dialeto = csv.Sniffer().sniff(texto[:4096], delimiters=";,\t")
        delim = dialeto.delimiter
    except csv.Error:
        delim = ";"
    linhas = list(csv.DictReader(io.StringIO(texto), delimiter=delim))
    return [{k: normaliza_codigo(k, v) for k, v in d.items() if k is not None} for d in linhas]


def _linha_e_cabecalho(r) -> bool:
    celulas = [c for c in r if c not in (None, "")]
    if len(celulas) < 2:
        return False
    tipos = {eh_coluna_codigo(str(c)) for c in celulas}
    return "cclasstrib" in tipos


def ler_xlsx(p: Path) -> list[dict]:
    try:
        import openpyxl  # type: ignore
    except ImportError:
        sys.exit("Para ler .xlsx instale openpyxl (pip install openpyxl) ou exporte a planilha para CSV.")
    wb = openpyxl.load_workbook(p, read_only=True, data_only=True)
    linhas: list[dict] = []
    try:
        for ws in wb.worksheets:
            cab = None
            for r in ws.iter_rows(values_only=True):
                if cab is None:
                    if r and _linha_e_cabecalho(r):
                        cab = [str(c).strip() if c is not None else f"col{i}" for i, c in enumerate(r)]
                    continue
                if any(c is not None for c in r):
                    d = {cab[i]: normaliza_codigo(cab[i], v) for i, v in enumerate(r) if i < len(cab)}
                    d["_aba"] = ws.title
                    linhas.append(d)
    finally:
        wb.close()
    return linhas


def buscar(dados: list[dict], termo: str) -> list[dict]:
    t = norm(termo).strip()
    if t.isdigit() and len(t) in (3, 6):
        alvo = "cst" if len(t) == 3 else "cclasstrib"
        return [d for d in dados
                if any(eh_coluna_codigo(k) in ("cst", "cclasstrib") and norm(v).startswith(t)
                       for k, v in d.items() if (alvo == "cst" or eh_coluna_codigo(k) == "cclasstrib"))]
    palavras = t.split()
    return [d for d in dados if all(p in norm(" ".join(map(str, d.values()))) for p in palavras)]


def main(argv=None) -> int:
    for s in (sys.stdout, sys.stderr):
        if hasattr(s, "reconfigure"):
            s.reconfigure(encoding="utf-8")
    ap = argparse.ArgumentParser(description="Consulta CST/cClassTrib do IBS/CBS")
    ap.add_argument("termo", help="código (CST com 3 dígitos, cClassTrib com 6) ou palavra-chave")
    ap.add_argument("--tabela", help="planilha oficial .xlsx ou .csv")
    ap.add_argument("--limite", type=int, default=30)
    ap.add_argument("--json", action="store_true")
    a = ap.parse_args(argv)
    if not a.termo.strip():
        ap.error("informe um termo de busca")

    p = Path(a.tabela) if a.tabela else REF
    if not p.exists():
        sys.exit(f"Arquivo não encontrado: {p}")
    dados = ler_xlsx(p) if p.suffix.lower() in (".xlsx", ".xlsm") else ler_csv(p)
    fonte = f"tabela oficial {p.name}" if a.tabela else "referência resumida da skill (confira na tabela oficial)"

    achados = buscar(dados, a.termo)
    total = len(achados)
    achados = achados[: a.limite]

    if a.json:
        print(json.dumps({"fonte": fonte, "total": total, "resultados": achados}, ensure_ascii=False, indent=2))
        return 0
    extra = f" (mostrando {len(achados)})" if total > len(achados) else ""
    print(f"# Consulta: {a.termo!r} — {total} resultado(s){extra} — fonte: {fonte}\n")
    if not achados:
        print("Nenhum resultado. Tente outro termo, o código do CST (3 dígitos) ou do cClassTrib (6 dígitos), "
              "ou use --tabela com a planilha oficial.")
        return 0
    for d in achados:
        if not a.tabela:
            red = f" | redução {d['reducao_pct']}%" if d.get("reducao_pct") else ""
            obs = f" | {d['observacao']}" if d.get("observacao") else ""
            print(f"- **{d['cclasstrib']}** (CST {d['cst']} – {d['descricao_cst']}): {d['descricao']}{red} | {d['base_legal']}{obs}")
        else:
            campos = [f"{k}: {v}" for k, v in d.items() if v and not k.startswith("_")][:12]
            print("- " + " | ".join(campos))
    return 0


if __name__ == "__main__":
    sys.exit(main())
