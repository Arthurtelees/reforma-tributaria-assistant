#!/usr/bin/env python3
"""
validar_nfe.py — Auditoria do grupo IBS/CBS (NT 2025.002-RTC) em XMLs de NF-e/NFC-e.

Uso:
  python validar_nfe.py nota.xml [outra.xml ...] [--pasta DIR] [--ano 2026] [--json] [--csv saida.csv]

Cada nota (infNFe) é validada separadamente — um arquivo de lote (enviNFe) com várias notas gera
um resultado por nota. Verifica:
  - chave de acesso: 44 dígitos, DV módulo 11, AAMM = mês de emissão, nNF da chave = nNF, cNF ≠ nNF
  - por item: presença do grupo IBSCBS; CST (3 dígitos) e cClassTrib (6 dígitos, começando pelo CST);
    recálculo de vIBSUF, vIBSMun e vCBS = vBC × alíquota (efetiva, se houver gRed), descontando
    diferimento (gDif/vDif) e devolução (gDevTrib/vDevTrib); vIBS = vIBSUF + vIBSMun;
    alíquotas de teste em 2026 (CBS 0,9%, IBS UF 0,1%, IBS Mun 0%)
  - totais: IBSCBSTot (vBCIBSCBS, gIBSUF/vIBSUF, gIBSMun/vIBSMun, gIBS/vIBS, gCBS/vCBS) = soma dos itens, ao centavo
Severidades: ERRO (corrigir), ALERTA (verificar), INFO (observação).
Código de saída: 1 se houver ERRO, 0 caso contrário (útil em CI e rotinas em lote).

Não substitui a validação de schema (XSD) nem as regras da SEFAZ. Itens monofásicos (CST 620 /
gIBSCBSMono) não têm os valores recalculados — o script avisa. Somente biblioteca padrão; lê por
nome local das tags (com ou sem namespace; nfeProc, NFe ou enviNFe).
"""
from __future__ import annotations

import argparse
import csv
import json
import sys
import xml.etree.ElementTree as ET
from pathlib import Path

TOL_ITEM = 0.01   # arredondamento por item (R$)
TOL_TOTAL = 0.01  # totais devem bater ao centavo com a soma dos itens já arredondados
CST_SEM_VALOR = {"400", "410", "510", "550", "620", "800", "810", "811", "820", "830"}
ALIQ_2026 = {"pCBS": 0.9, "pIBSUF": 0.1, "pIBSMun": 0.0}


# ------------------------------------------------------------------ helpers de XML
def ln(tag: str) -> str:
    return tag.rsplit("}", 1)[-1]


def acha(el, nome):
    if el is None:
        return None
    for e in el.iter():
        if ln(e.tag) == nome:
            return e
    return None


def filho(el, nome):
    if el is None:
        return None
    for e in list(el):
        if ln(e.tag) == nome:
            return e
    return None


class Coletor:
    """Acumula problemas de uma nota."""

    def __init__(self):
        self.itens: list[tuple[str, str, str]] = []

    def add(self, local: str, sev: str, msg: str) -> None:
        self.itens.append((local, sev, msg))

    def tem_erro(self, local: str) -> bool:
        return any(l == local and s == "ERRO" for l, s, _ in self.itens)


def num(el, nome, col: Coletor | None = None, local: str = "") -> float | None:
    e = filho(el, nome) if el is not None and filho(el, nome) is not None else acha(el, nome)
    if e is None or e.text is None:
        return None
    try:
        return float(e.text.strip())
    except ValueError:
        if col is not None:
            col.add(local, "ERRO", f"{nome} com valor não numérico: {e.text.strip()!r} (use ponto decimal)")
        return None


def txt(el, nome) -> str | None:
    e = acha(el, nome)
    return e.text.strip() if e is not None and e.text else None


# ------------------------------------------------------------------ chave de acesso
def dv_mod11(base43: str) -> int:
    pesos, soma = [2, 3, 4, 5, 6, 7, 8, 9], 0
    for i, d in enumerate(reversed(base43)):
        soma += int(d) * pesos[i % 8]
    r = soma % 11
    return 0 if r < 2 else 11 - r


def checar_chave(chave: str, dh: str, nnf: str | None, col: Coletor) -> None:
    if not chave:
        col.add("chave", "ALERTA", "Chave de acesso (atributo Id de infNFe) ausente")
        return
    if len(chave) != 44 or not chave.isdigit():
        col.add("chave", "ERRO", f"Chave de acesso com formato inválido ({len(chave)} caracteres)")
        return
    dv = dv_mod11(chave[:43])
    if dv != int(chave[43]):
        col.add("chave", "ERRO", f"Dígito verificador da chave {chave[43]} ≠ calculado {dv} (módulo 11)")
    if len(dh) >= 7 and chave[2:6] != dh[2:4] + dh[5:7]:
        col.add("chave", "ERRO", f"AAMM da chave ({chave[2:6]}) não corresponde à data de emissão ({dh[:7]})")
    nnf_chave, cnf = chave[25:34], chave[35:43]
    if nnf and nnf.isdigit() and int(nnf) != int(nnf_chave):
        col.add("chave", "ERRO", f"nNF da chave ({int(nnf_chave)}) ≠ nNF da nota ({int(nnf)})")
    if cnf.lstrip("0") and int(cnf) == int(nnf_chave):
        col.add("chave", "ALERTA", "Código numérico (cNF) igual ao número da nota — costuma gerar rejeição na SEFAZ")


# ------------------------------------------------------------------ tributo por item
def checar_tributo(grupo, p_tag, v_tag, vbc, item_id, col: Coletor, ano) -> float:
    """grupo = gIBSUF / gIBSMun / gCBS. Devolve o valor informado (v_tag)."""
    if grupo is None:
        return 0.0
    p = num(grupo, p_tag, col, item_id)
    v = num(grupo, v_tag, col, item_id) or 0.0
    gred = filho(grupo, "gRed")
    p_ef = num(gred, "pAliqEfet", col, item_id) if gred is not None else None
    aliq = p_ef if p_ef is not None else p
    if gred is not None and p is not None and p_ef is not None:
        pred = num(gred, "pRedAliq", col, item_id)
        if pred is not None:
            esperado = p * (1 - pred / 100)
            if abs(esperado - p_ef) > 0.00005:
                col.add(item_id, "ERRO", f"{p_tag}: pAliqEfet {p_ef} ≠ {p_tag} {p} × (1 − pRedAliq {pred}%) = {esperado:.4f}")
    v_dif = num(filho(grupo, "gDif"), "vDif", col, item_id) or 0.0
    v_dev = num(filho(grupo, "gDevTrib"), "vDevTrib", col, item_id) or 0.0
    if aliq is not None and vbc is not None:
        bruto = round(vbc * aliq / 100 + 1e-9, 2)
        calc = round(bruto - v_dif - v_dev, 2)
        if abs(calc - v) > TOL_ITEM + 1e-9:
            extra = f" − vDif {v_dif:.2f}" if v_dif else ""
            extra += f" − vDevTrib {v_dev:.2f}" if v_dev else ""
            col.add(item_id, "ERRO", f"{v_tag} informado {v:.2f} ≠ calculado {calc:.2f} (vBC {vbc:.2f} × {aliq}%{extra})")
    if ano == 2026 and p is not None and gred is None and p_tag in ALIQ_2026 and abs(p - ALIQ_2026[p_tag]) > 1e-6:
        col.add(item_id, "ALERTA", f"{p_tag} = {p}% — em 2026 a alíquota de teste esperada é {ALIQ_2026[p_tag]}%")
    return v


# ------------------------------------------------------------------ nota
def validar_nota(inf, raiz, caminho: Path, ano_cli: int | None) -> dict:
    col = Coletor()
    chave = (inf.get("Id") or "").replace("NFe", "")
    ide = acha(inf, "ide")
    dh = txt(ide, "dhEmi") or ""
    ano = ano_cli
    if ano is None and len(dh) >= 4 and dh[:4].isdigit():
        ano = int(dh[:4])
    mod = txt(ide, "mod")
    crt = txt(acha(inf, "emit"), "CRT")
    checar_chave(chave, dh, txt(ide, "nNF"), col)

    dets = [e for e in inf.iter() if ln(e.tag) == "det"]
    soma = {"vBC": 0.0, "vIBSUF": 0.0, "vIBSMun": 0.0, "vCBS": 0.0}
    tem_grupo = False
    itens_ok = 0
    for det in dets:
        item_id = f"item {det.get('nItem', '?')}"
        imp = filho(det, "imposto")
        grupo = filho(imp, "IBSCBS") if imp is not None else None
        if grupo is None:
            sev = "ALERTA" if crt in {"1", "2", "4"} and (ano or 0) < 2027 else "ERRO"
            col.add(item_id, sev, "Grupo IBSCBS ausente (obrigatório conforme Ato Conjunto RFB/CGIBS 4/2026; "
                                  "Rejeição 1115 / UB12-10 quando ativada)")
            continue
        tem_grupo = True
        cst, cct = txt(grupo, "CST"), txt(grupo, "cClassTrib")
        if not cst or len(cst) != 3 or not cst.isdigit():
            col.add(item_id, "ERRO", f"CST inválido: {cst!r}")
        if not cct or len(cct) != 6 or not cct.isdigit():
            col.add(item_id, "ERRO", f"cClassTrib inválido: {cct!r}")
        elif cst and not cct.startswith(cst):
            col.add(item_id, "ERRO", f"cClassTrib {cct} não corresponde ao CST {cst} (3 primeiros dígitos)")
        if acha(grupo, "gIBSCBSMono") is not None or cst == "620":
            col.add(item_id, "INFO", "Item monofásico (CST 620): valores não recalculados por este script — conferir gIBSCBSMono")

        g = filho(grupo, "gIBSCBS")
        if g is None:
            if cst and cst not in CST_SEM_VALOR:
                col.add(item_id, "ALERTA", f"CST {cst} sem subgrupo gIBSCBS (verificar se o cClassTrib dispensa valores)")
            if not col.tem_erro(item_id):
                itens_ok += 1
            continue
        vbc = num(g, "vBC", col, item_id)
        if vbc is None:
            col.add(item_id, "ERRO", "vBC ausente em gIBSCBS")
        else:
            soma["vBC"] += vbc
        # heurística de base: na transição ICMS/ISS/PIS/Cofins saem da base (LC 214 art. 12 §2º);
        # confirmada a vigência desde 01/01/2026 (auditoria nov/2026).
        prod = filho(det, "prod")
        vprod = num(prod, "vProd") if prod is not None else None
        vicms = num(filho(imp, "ICMS"), "vICMS") if filho(imp, "ICMS") is not None else None
        if vbc is not None and vprod and vicms and vicms > 0.01 and abs(vbc - vprod) <= TOL_ITEM:
            col.add(item_id, "ALERTA", f"vBC ({vbc:.2f}) = vProd com ICMS destacado ({vicms:.2f}). De 2026 a 2032 ICMS, ISS e "
                                     "PIS/Cofins saem da base do IBS/CBS (LC 214 art. 12 §2º, V) — confira o cálculo da base no ERP.")

        soma["vIBSUF"] += checar_tributo(filho(g, "gIBSUF"), "pIBSUF", "vIBSUF", vbc, item_id, col, ano)
        soma["vIBSMun"] += checar_tributo(filho(g, "gIBSMun"), "pIBSMun", "vIBSMun", vbc, item_id, col, ano)
        v_cbs = checar_tributo(filho(g, "gCBS"), "pCBS", "vCBS", vbc, item_id, col, ano)
        soma["vCBS"] += v_cbs
        v_ibs = num(filho(g, "vIBS"), "vIBS", col, item_id) if filho(g, "vIBS") is not None else None
        uf_i = num(filho(g, "gIBSUF"), "vIBSUF") or 0.0
        mun_i = num(filho(g, "gIBSMun"), "vIBSMun") or 0.0
        if v_ibs is not None and abs(v_ibs - (uf_i + mun_i)) > TOL_ITEM:
            col.add(item_id, "ERRO", f"vIBS {v_ibs:.2f} ≠ vIBSUF + vIBSMun = {uf_i + mun_i:.2f}")
        if not col.tem_erro(item_id):
            itens_ok += 1

    tot = acha(inf, "IBSCBSTot")
    if tot is not None:
        def comparar(rotulo, informado, esperado):
            if informado is not None and abs(informado - esperado) > TOL_TOTAL:
                col.add("total", "ERRO", f"{rotulo} {informado:.2f} ≠ soma dos itens {esperado:.2f}")
        comparar("IBSCBSTot/vBCIBSCBS", num(tot, "vBCIBSCBS", col, "total"), soma["vBC"])
        g_ibs = filho(tot, "gIBS")
        comparar("IBSCBSTot/gIBS/gIBSUF/vIBSUF", num(acha(g_ibs, "gIBSUF"), "vIBSUF", col, "total") if acha(g_ibs, "gIBSUF") is not None else None, soma["vIBSUF"])
        comparar("IBSCBSTot/gIBS/gIBSMun/vIBSMun", num(acha(g_ibs, "gIBSMun"), "vIBSMun", col, "total") if acha(g_ibs, "gIBSMun") is not None else None, soma["vIBSMun"])
        comparar("IBSCBSTot/gIBS/vIBS", num(g_ibs, "vIBS", col, "total") if g_ibs is not None and filho(g_ibs, "vIBS") is not None else None, soma["vIBSUF"] + soma["vIBSMun"])
        g_cbs = filho(tot, "gCBS")
        v_cbs_tot = num(g_cbs, "vCBS", col, "total") if g_cbs is not None else num(tot, "vCBS", col, "total")
        comparar("IBSCBSTot/vCBS", v_cbs_tot, soma["vCBS"])
    elif tem_grupo:
        col.add("total", "ALERTA", "Grupo IBSCBSTot ausente no total da nota")

    return {"arquivo": str(caminho), "chave": chave, "modelo": mod, "crt": crt, "ano": ano,
            "itens": len(dets), "itens_sem_erro": itens_ok,
            "soma_itens": {k: round(v, 2) for k, v in soma.items()},
            "problemas": [{"local": a, "severidade": b, "mensagem": c} for a, b, c in col.itens]}


def validar_arquivo(caminho: Path, ano: int | None) -> list[dict]:
    try:
        raiz = ET.parse(caminho).getroot()
    except (ET.ParseError, OSError, ValueError) as e:
        return [{"arquivo": str(caminho), "chave": "", "modelo": None, "crt": None, "ano": ano, "itens": 0,
                 "itens_sem_erro": 0, "soma_itens": {"vBC": 0, "vIBSUF": 0, "vIBSMun": 0, "vCBS": 0},
                 "problemas": [{"local": "arquivo", "severidade": "ERRO", "mensagem": f"XML ilegível ou inexistente: {e}"}]}]
    infs = [e for e in raiz.iter() if ln(e.tag) == "infNFe"]
    if not infs:
        return [{"arquivo": str(caminho), "chave": "", "modelo": None, "crt": None, "ano": ano, "itens": 0,
                 "itens_sem_erro": 0, "soma_itens": {"vBC": 0, "vIBSUF": 0, "vIBSMun": 0, "vCBS": 0},
                 "problemas": [{"local": "arquivo", "severidade": "ERRO", "mensagem": "Nenhuma NF-e (infNFe) encontrada no arquivo"}]}]
    return [validar_nota(inf, raiz, caminho, ano) for inf in infs]


def main(argv=None) -> int:
    for s in (sys.stdout, sys.stderr):
        if hasattr(s, "reconfigure"):
            s.reconfigure(encoding="utf-8")
    ap = argparse.ArgumentParser(description="Valida o grupo IBS/CBS em XMLs de NF-e/NFC-e")
    ap.add_argument("arquivos", nargs="*")
    ap.add_argument("--pasta", help="valida todos os .xml da pasta (recursivo)")
    ap.add_argument("--ano", type=int, help="ano de referência (padrão: ano de dhEmi)")
    ap.add_argument("--json", action="store_true")
    ap.add_argument("--csv", help="grava os problemas em CSV (separador ;)")
    a = ap.parse_args(argv)
    arqs = [Path(x) for x in a.arquivos]
    if a.pasta:
        arqs += sorted(Path(a.pasta).rglob("*.xml"))
    if not arqs:
        ap.error("informe arquivos ou --pasta")
    res = [nota for p in arqs for nota in validar_arquivo(p, a.ano)]

    if a.csv:
        with open(a.csv, "w", newline="", encoding="utf-8-sig") as f:
            w = csv.writer(f, delimiter=";")
            w.writerow(["arquivo", "chave", "local", "severidade", "mensagem"])
            for r in res:
                for p in r["problemas"]:
                    w.writerow([r["arquivo"], r.get("chave", ""), p["local"], p["severidade"], p["mensagem"]])
    total_err = sum(1 for r in res for p in r["problemas"] if p["severidade"] == "ERRO")
    total_al = sum(1 for r in res for p in r["problemas"] if p["severidade"] == "ALERTA")
    if a.json:
        print(json.dumps(res, ensure_ascii=False, indent=2))
        return 1 if total_err else 0
    print(f"# Validação IBS/CBS — {len(res)} nota(s) em {len(arqs)} arquivo(s): {total_err} erro(s), {total_al} alerta(s)\n")
    for r in res:
        bloqueantes = [p for p in r["problemas"] if p["severidade"] in ("ERRO", "ALERTA")]
        status = "OK" if not bloqueantes else ("COM ERROS" if any(p["severidade"] == "ERRO" for p in bloqueantes) else "COM ALERTAS")
        print(f"## {Path(r['arquivo']).name} — {status}")
        if r["itens"]:
            s = r["soma_itens"]
            print(f"Chave {r['chave'] or '-'} | modelo {r['modelo']} | CRT {r['crt']} | ano {r['ano']} | itens {r['itens']} "
                  f"| soma CBS {s['vCBS']:.2f} | soma IBS {s['vIBSUF'] + s['vIBSMun']:.2f}")
        for p in r["problemas"]:
            print(f"- **{p['severidade']}** [{p['local']}] {p['mensagem']}")
        print()
    return 1 if total_err else 0


if __name__ == "__main__":
    sys.exit(main())
