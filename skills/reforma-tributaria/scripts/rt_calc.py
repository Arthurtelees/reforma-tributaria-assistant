#!/usr/bin/env python3
"""
rt_calc.py — Calculadora da Reforma Tributária (IBS / CBS / IS) para a skill `reforma-tributaria`.

Somente biblioteca padrão (Python 3.9+). Alíquotas e cronograma vêm de ../assets/parametros.json
(ou --parametros); tabelas do Simples de ../assets/simples_anexos.json.

PERCENTUAIS NA LINHA DE COMANDO SÃO SEMPRE EM %: 18 = 18%, 0.9 = 0,9%, 60 = 60%.

Subcomandos:
  cronograma   Alíquotas e regras ano a ano (2026–2033)
  operacao     IBS/CBS/IS de uma operação em um ano
  transicao    Carga ano a ano mantendo a receita líquida + perda de margem com preço fixo
  das          Faixa, alíquota efetiva e partilha do DAS (LC 123, Anexos I–V)
  simples      Simples Nacional: IBS/CBS dentro do DAS x regime regular "por fora"
  imovel       Locação ou alienação de imóvel (redutores e reduções)
  cashback     Estimativa de devolução para família do CadÚnico
  converter    Converte alíquota "por fora" <-> "por dentro"

--json, --cenario e --parametros podem vir antes ou depois do subcomando.
Resultados são ESTIMATIVAS: as alíquotas de referência ainda não estão todas fixadas.
"""
from __future__ import annotations

import argparse
import json
import math
import sys
from datetime import date
from decimal import ROUND_HALF_UP, Decimal
from functools import lru_cache
from pathlib import Path

ANOS = [str(a) for a in range(2026, 2034)]
BASE = Path(__file__).resolve().parent.parent / "assets"
PARAMS_PADRAO = BASE / "parametros.json"
SIMPLES_PADRAO = BASE / "simples_anexos.json"
DIAS_ALERTA_DESATUALIZADO = 90


# ---------------------------------------------------------------- utilidades
def r2(x: float) -> float:
    """Arredondamento comercial a 2 casas (meio para cima), como nos documentos fiscais."""
    return float(Decimal(repr(x)).quantize(Decimal("0.01"), rounding=ROUND_HALF_UP))


def rr(x: float, casas: int = 6) -> float:
    """Limpa ruído de ponto flutuante em alíquotas (0.09000000000000001 -> 0.09)."""
    return round(x, casas)


def pct(x: float | None) -> float | None:
    """Percentual da CLI -> fração. SEMPRE em %: 18 -> 0.18; 0.9 -> 0.009."""
    return None if x is None else x / 100.0


def brl(v: float) -> str:
    s = f"{v:,.2f}"
    return "R$ " + s.replace(",", "X").replace(".", ",").replace("X", ".")


def fpct(v: float, casas: int = 2) -> str:
    return f"{v * 100:.{casas}f}%".replace(".", ",")


def tabela_md(cab: list[str], linhas: list[list[str]]) -> str:
    out = ["| " + " | ".join(cab) + " |", "|" + "|".join(["---"] * len(cab)) + "|"]
    out += ["| " + " | ".join(str(c) for c in l) + " |" for l in linhas]
    return "\n".join(out)


def emitir(args, dados: dict, texto: str, avisos: list[str] | None = None) -> None:
    avisos = [a for a in (avisos or []) if a]
    if getattr(args, "json", False):
        if avisos:
            dados = {**dados, "avisos": avisos}
        print(json.dumps(dados, ensure_ascii=False, indent=2))
    else:
        if avisos:
            texto += "\n\n" + "\n".join(f"> ⚠️ {a}" for a in avisos)
        print(texto)


def falhar(msg: str) -> None:
    sys.exit(f"Erro: {msg}")


# ---------------------------------------------------------------- tipos de argumento
def valor_nao_negativo(s: str) -> float:
    try:
        v = float(str(s).replace(",", "."))
    except ValueError:
        raise argparse.ArgumentTypeError(f"número inválido: {s!r}")
    if not math.isfinite(v) or v < 0:
        raise argparse.ArgumentTypeError("o valor deve ser um número ≥ 0")
    return v


def percentual(s: str) -> float:
    """Percentual entre 0 e 100 (aceita '18', '18%', '0,9')."""
    v = valor_nao_negativo(str(s).rstrip("%"))
    if v > 100:
        raise argparse.ArgumentTypeError("percentual deve estar entre 0 e 100")
    return v


def ano_valido(s: str) -> int:
    try:
        a = int(s)
    except ValueError:
        raise argparse.ArgumentTypeError(f"ano inválido: {s!r}")
    if not 2026 <= a <= 2033:
        raise argparse.ArgumentTypeError("ano deve estar entre 2026 e 2033 (de 2034 em diante, use 2033 — regime pleno)")
    return a


# ---------------------------------------------------------------- parâmetros
def carregar_parametros(caminho: str | None) -> dict:
    p = Path(caminho) if caminho else PARAMS_PADRAO
    try:
        with open(p, encoding="utf-8") as f:
            P = json.load(f)
    except OSError:
        falhar(f"arquivo de parâmetros não encontrado: {p}")
    except json.JSONDecodeError as e:
        falhar(f"parâmetros inválidos em {p}: {e}")
    faltando = [a for a in ANOS if a not in P.get("transicao", {})]
    if faltando or "cenarios" not in P or P.get("cenario_padrao") not in P["cenarios"]:
        falhar(f"parametros.json incompleto (anos faltando: {faltando or '-'}; verifique 'cenarios' e 'cenario_padrao')")
    return P


def aviso_desatualizado(P: dict) -> str | None:
    try:
        base = date.fromisoformat(P.get("data_base", ""))
    except ValueError:
        return None
    dias = (date.today() - base).days
    if dias > DIAS_ALERTA_DESATUALIZADO:
        return (f"Parâmetros com data-base {base.strftime('%d/%m/%Y')} ({dias} dias atrás). Alíquotas e prazos podem ter "
                "mudado — confira as fontes oficiais ou rode o comando /rt-novidades.")
    return None


@lru_cache(maxsize=1)
def tabelas_simples() -> dict:
    with open(SIMPLES_PADRAO, encoding="utf-8") as f:
        return json.load(f)["anexos"]


# ---------------------------------------------------------------- alíquotas
def aliquotas_ano(P: dict, ano: str, cenario: str | None = None, cbs=None, ibs_uf=None, ibs_mun=None) -> dict:
    """CBS / IBS-UF / IBS-Mun (frações, sem redução) e fatores do sistema antigo para um ano 2026–2033."""
    t = P["transicao"][ano]
    cen = P["cenarios"][cenario or P["cenario_padrao"]]
    cbs_ref, ibs_ref = cen["cbs_referencia"], cen["ibs_referencia"]
    prop_mun = P.get("proporcao_ibs_municipal", 0.2)

    a_cbs = t["cbs_fixa"] if "cbs_fixa" in t else cbs_ref - t.get("cbs_desconto_pp", 0.0)
    if t.get("fator_ibs") is None:
        a_uf, a_mun = t.get("ibs_uf_fixa", 0.0), t.get("ibs_mun_fixa", 0.0)
    else:
        total = ibs_ref * t["fator_ibs"]
        a_uf, a_mun = total * (1 - prop_mun), total * prop_mun
    if cbs is not None:
        a_cbs = cbs
    if ibs_uf is not None:
        a_uf = ibs_uf
    if ibs_mun is not None:
        a_mun = ibs_mun
    return {"ano": ano, "cbs": rr(a_cbs), "ibs_uf": rr(a_uf), "ibs_mun": rr(a_mun),
            "fator_icms_iss": t["fator_icms_iss"], "pis_cofins": t["pis_cofins"], "ipi": t["ipi"],
            "imposto_seletivo": t["imposto_seletivo"], "nota": t.get("nota", "")}


def calc_ibscbs(base: float, al: dict, reducao: float = 0.0, aliq_is: float = 0.0) -> dict:
    """Cálculo por fora. O IS integra a base do IBS/CBS (LC 214 art. 12 §1º).
    Cada tributo é arredondado e os totais são a soma dos valores arredondados."""
    v_is = r2(base * aliq_is) if al["imposto_seletivo"] else 0.0
    b = r2(base + v_is)
    f = 1 - reducao
    cbs, uf, mun = r2(b * al["cbs"] * f), r2(b * al["ibs_uf"] * f), r2(b * al["ibs_mun"] * f)
    return {"base_ibscbs": b, "imposto_seletivo": v_is,
            "aliq_efetiva_cbs": rr(al["cbs"] * f), "aliq_efetiva_ibs": rr((al["ibs_uf"] + al["ibs_mun"]) * f),
            "cbs": cbs, "ibs_uf": uf, "ibs_mun": mun, "ibs": r2(uf + mun), "total_ibscbs": r2(cbs + uf + mun)}


# ---------------------------------------------------------------- cronograma / operação
def cmd_cronograma(args, P):
    linhas, dados = [], []
    for ano in ANOS:
        a = aliquotas_ano(P, ano, args.cenario)
        dados.append(a)
        linhas.append([ano, fpct(a["cbs"]), fpct(a["ibs_uf"] + a["ibs_mun"]), fpct(a["cbs"] + a["ibs_uf"] + a["ibs_mun"]),
                       fpct(a["fator_icms_iss"], 0), "sim" if a["pis_cofins"] else "extinto",
                       "sim" if a["ipi"] else "zero*", "sim" if a["imposto_seletivo"] else "—"])
    cen_nome = args.cenario or P["cenario_padrao"]
    txt = (f"## Cronograma — cenário `{cen_nome}`\n{P['cenarios'][cen_nome]['descricao']}\n\n"
           + tabela_md(["Ano", "CBS", "IBS", "IBS+CBS", "ICMS/ISS (% da alíq. atual)", "PIS/Cofins", "IPI", "IS"], linhas)
           + "\n\n*IPI mantido apenas para produtos com industrialização incentivada na ZFM. "
             "IBS 2029–2032 é aproximação proporcional (alíquotas reais serão fixadas pelos entes/Senado).")
    emitir(args, {"cenario": cen_nome, "anos": dados}, txt, [aviso_desatualizado(P)])


def cmd_operacao(args, P):
    al = aliquotas_ano(P, str(args.ano), args.cenario, pct(args.cbs), pct(args.ibs_uf), pct(args.ibs_mun))
    red = pct(args.reducao) or 0.0
    r = calc_ibscbs(args.valor, al, red, pct(args.aliq_is) or 0.0)
    total_doc = r2(args.valor + r["imposto_seletivo"] + r["total_ibscbs"])
    avisos = [aviso_desatualizado(P)]
    if args.aliq_is and not al["imposto_seletivo"]:
        avisos.append(f"O Imposto Seletivo só começa em 2027; em {al['ano']} foi considerado zero.")
    entrada = {k: v for k, v in vars(args).items() if k != "func"}
    dados = {"entrada": entrada, "aliquotas": al, "resultado": r, "total_documento": total_doc}
    linhas = [
        ["Valor da operação (sem IBS/CBS)", brl(args.valor)],
        ["Imposto Seletivo", brl(r["imposto_seletivo"])],
        ["Base IBS/CBS", brl(r["base_ibscbs"])],
        [f"CBS ({fpct(r['aliq_efetiva_cbs'], 4)})", brl(r["cbs"])],
        [f"IBS UF ({fpct(al['ibs_uf'] * (1 - red), 4)})", brl(r["ibs_uf"])],
        [f"IBS Município ({fpct(al['ibs_mun'] * (1 - red), 4)})", brl(r["ibs_mun"])],
        ["**Total IBS+CBS**", f"**{brl(r['total_ibscbs'])}**"],
        ["**Total do documento**", f"**{brl(total_doc)}**"],
    ]
    extra = ""
    if al["ano"] == "2026":
        extra = "\n\n> 2026: valores de teste. Recolhimento dispensado se as obrigações acessórias forem cumpridas; compensável com PIS/Cofins."
    txt = (f"## Operação — {al['ano']} (redução {fpct(red, 0)})\n\n" + tabela_md(["Item", "Valor"], linhas)
           + f"\n\nNota do ano: {al['nota']}{extra}")
    emitir(args, dados, txt, avisos)


# ---------------------------------------------------------------- transição
def _transicao_ano(P, ano, args) -> dict:
    """Mantém a receita líquida (preço − tributos sobre a venda) constante e calcula o preço necessário."""
    al = aliquotas_ano(P, ano, args.cenario)
    red = pct(args.reducao) or 0.0
    icms, iss, pc, ipi = (pct(x) or 0.0 for x in (args.icms, args.iss, args.pis_cofins, args.ipi))
    V0 = args.valor
    icms0, iss0 = V0 * icms, V0 * iss
    pc0 = (V0 - icms0) * pc  # PIS/Cofins sem ICMS na base (STF, Tema 69)
    liquido = V0 - icms0 - iss0 - pc0

    f = al["fator_icms_iss"]
    a, p = (icms + iss) * f, (pc if al["pis_cofins"] else 0.0)
    denom = 1 - a - (1 - icms * f) * p  # V − V·a − (V − V·icms·f)·p = líquido
    if denom <= 0:
        falhar(f"combinação de alíquotas inviável em {ano} (tributos por dentro ≥ 100% do preço).")
    V = liquido / denom
    v_icms, v_iss = V * icms * f, V * iss * f
    v_pc = (V - v_icms) * p
    v_ipi = V * ipi if (al["ipi"] or args.zfm) else 0.0
    base = V - v_icms - v_iss - v_pc  # LC 214 art. 12 §2º: tributos antigos fora da base na transição
    r = calc_ibscbs(base, al, red, pct(args.aliq_is) or 0.0)
    dispensado = ano == "2026" and not args.cobrar_2026
    novos = 0.0 if dispensado else r["total_ibscbs"]
    tributos = v_icms + v_iss + v_pc + v_ipi + r["imposto_seletivo"] + novos
    total_cliente = V + v_ipi + r["imposto_seletivo"] + novos

    compras = args.compras or 0.0
    cred_leg = compras * ((pct(args.compras_icms) or 0.0) * f + (pct(args.compras_pis_cofins) or 0.0) * (1 if al["pis_cofins"] else 0))
    cred_novo = 0.0 if dispensado else compras * (al["cbs"] + al["ibs_uf"] + al["ibs_mun"]) * (1 - (pct(args.reducao_compras) or 0.0))
    return {"ano": ano, "preco_sem_ibscbs": r2(V), "icms": r2(v_icms), "iss": r2(v_iss), "pis_cofins": r2(v_pc),
            "ipi": r2(v_ipi), "is": r["imposto_seletivo"], "cbs": r["cbs"], "ibs": r["ibs"],
            "ibscbs_dispensado_2026": dispensado, "total_tributos": r2(tributos), "total_cliente": r2(total_cliente),
            "receita_liquida": r2(liquido), "carga_sobre_preco_final": rr(tributos / total_cliente) if total_cliente else 0,
            "credito_compras_legado": r2(cred_leg), "credito_compras_ibscbs": r2(cred_novo),
            "tributo_liquido_estimado": r2(tributos - cred_leg - cred_novo)}


def cmd_transicao(args, P):
    res = [_transicao_ano(P, ano, args) for ano in ANOS]
    base_cli = res[0]["total_cliente"]
    for r in res:  # preço final fixo: tudo é linear no preço -> receita líquida escala por preço_hoje / preço_necessário
        fator = base_cli / r["total_cliente"] if r["total_cliente"] else 1
        r["receita_liquida_preco_fixo"] = r2(r["receita_liquida"] * fator)
        r["perda_margem_preco_fixo"] = r2(r["receita_liquida"] * fator - r["receita_liquida"])
    linhas = []
    for r in res:
        var = (r["total_cliente"] / base_cli - 1) if base_cli else 0
        inf = " (inf.)" if r["ibscbs_dispensado_2026"] else ""
        linhas.append([r["ano"], brl(r["preco_sem_ibscbs"]), brl(r["icms"] + r["iss"]), brl(r["pis_cofins"]),
                       brl(r["cbs"]) + inf, brl(r["ibs"]) + inf, brl(r["is"] + r["ipi"]), brl(r["total_cliente"]),
                       fpct(r["carga_sobre_preco_final"]), fpct(var)])
    txt = (f"## Transição 2026–2033 — receita líquida mantida em {brl(res[0]['receita_liquida'])}\n"
           f"Cenário `{args.cenario or P['cenario_padrao']}`; redução de alíquota {fpct(pct(args.reducao) or 0, 0)}.\n\n"
           + tabela_md(["Ano", "Preço (sem IBS/CBS)", "ICMS+ISS", "PIS/Cofins", "CBS", "IBS", "IPI+IS", "Total ao cliente",
                        "Carga s/ total", "Var. preço final vs 2026"], linhas)
           + "\n\nLeitura: 'Total ao cliente' é o preço que mantém a mesma receita líquida para a empresa. "
             "Se o cliente é contribuinte do regime regular, ele recupera CBS/IBS como crédito — o custo real dele é o "
             "'Preço (sem IBS/CBS)'. '(inf.)' = 2026 informativo (recolhimento dispensado).")
    txt += ("\n\n### Se o preço final ao cliente ficar fixo (ex.: consumidor final que não aceita aumento)\n"
            + tabela_md(["Ano", "Receita líquida", "Variação vs hoje", "Variação %"],
                        [[r["ano"], brl(r["receita_liquida_preco_fixo"]), brl(r["perda_margem_preco_fixo"]),
                          fpct(r["perda_margem_preco_fixo"] / r["receita_liquida"] if r["receita_liquida"] else 0)] for r in res])
            + "\n\nValores proporcionais ao `--valor` informado: use o faturamento mensal ou anual em `--valor` para obter o efeito em reais.")
    if args.compras:
        txt += "\n\n### Créditos sobre compras (estimativa)\n" + tabela_md(
            ["Ano", "Créditos legados (ICMS/PIS/Cofins)", "Créditos IBS/CBS", "Tributo líquido estimado"],
            [[r["ano"], brl(r["credito_compras_legado"]), brl(r["credito_compras_ibscbs"]), brl(r["tributo_liquido_estimado"])] for r in res])
    emitir(args, {"anos": res}, txt, [aviso_desatualizado(P)])


# ---------------------------------------------------------------- Simples Nacional
def das_simples(anexo: str, rbt12: float, P: dict | None = None, ano: str = "2033") -> dict:
    """Faixa, alíquota efetiva e partilha do DAS (LC 123, Anexos I–V) + fatia substituída por IBS/CBS no ano.

    Alíquota efetiva = (RBT12 × nominal − dedução) / RBT12. Aplica o teto de 5% do ISS na 5ª faixa
    dos Anexos III e IV. A fatia substituída é APROXIMAÇÃO da transição: PIS/Cofins (+IPI) a partir
    de 2027 e ICMS/ISS proporcionalmente à redução de 2029–2032; integral em 2033.
    """
    T = tabelas_simples()
    anexo = anexo.strip().upper()
    if anexo not in T:
        falhar(f"anexo inválido: {anexo}. Use I, II, III, IV ou V.")
    if rbt12 < 0:
        falhar("RBT12 não pode ser negativa.")
    tab = T[anexo]
    fx = next((f for f in tab["faixas"] if rbt12 <= f["ate"]), None)
    if fx is None:
        falhar("RBT12 acima de R$ 4,8 milhões: fora do Simples Nacional.")
    efetiva = (rbt12 * fx["aliquota"] / 100 - fx["deducao"]) / rbt12 if rbt12 > 0 else fx["aliquota"] / 100
    rep = {k: (v or 0.0) / 100 for k, v in fx["reparticao"].items()}
    teto = tab.get("teto_iss_5a_faixa")
    if teto and fx["faixa"] == 5 and efetiva * 100 > teto["limiar_aliquota_efetiva"]:
        exced = efetiva - 0.05
        rep = {k: exced * v / 100 / efetiva for k, v in teto["reparticao_excedente"].items()}
        rep["ISS"] = 0.05 / efetiva
    loc = rep.get("ICMS", 0.0) + rep.get("ISS", 0.0)
    fed = rep.get("PIS", 0.0) + rep.get("Cofins", 0.0) + rep.get("IPI", 0.0)
    ano_i = int(ano)
    if ano_i <= 2026:
        fatia = 0.0
    else:
        fator = P["transicao"][str(min(ano_i, 2033))]["fator_icms_iss"] if P else (0.0 if ano_i >= 2033 else 1.0)
        fatia = fed + loc * (1 - fator)
    avisos = []
    if fx["faixa"] == 6:
        avisos.append("6ª faixa: ICMS/ISS são recolhidos fora do DAS (sublimite) — a fatia não inclui o ICMS/ISS que o IBS substituirá.")
    return {"anexo": anexo, "titulo": tab["titulo"], "faixa": fx["faixa"], "rbt12": rbt12,
            "aliquota_nominal": fx["aliquota"] / 100, "deducao": fx["deducao"], "aliquota_efetiva": rr(efetiva),
            "reparticao": {k: rr(v) for k, v in rep.items()}, "fatia_ibscbs_no_ano": rr(fatia), "ano": str(ano_i),
            "avisos": avisos}


def cmd_das(args, P):
    r = das_simples(args.anexo, args.rbt12, P, str(args.ano))
    linhas = [[k, fpct(v), fpct(v * r["aliquota_efetiva"])] for k, v in r["reparticao"].items()]
    anos = []
    for a in ANOS[1:]:
        x = das_simples(args.anexo, args.rbt12, P, a)
        anos.append([a, fpct(x["fatia_ibscbs_no_ano"]), fpct(x["fatia_ibscbs_no_ano"] * x["aliquota_efetiva"])])
    txt = (f"## DAS — Anexo {r['anexo']} ({r['titulo']}) — RBT12 {brl(args.rbt12)}\n\n"
           f"**{r['faixa']}ª faixa**: nominal {fpct(r['aliquota_nominal'])}, dedução {brl(r['deducao'])} → "
           f"**alíquota efetiva {fpct(r['aliquota_efetiva'])}** = ({brl(args.rbt12)} × {fpct(r['aliquota_nominal'])} − "
           f"{brl(r['deducao'])}) ÷ {brl(args.rbt12)}\n\n"
           + tabela_md(["Tributo", "% do DAS", "% da receita"], linhas)
           + "\n\n### Fatia do DAS que o IBS/CBS substitui\n"
           + tabela_md(["Ano", "% do DAS", "% da receita"], anos)
           + "\n\nFonte: LC 123/2006, Anexos I–V (redação LC 155/2016). Fatia por ano é aproximação da transição "
             "(a LC 214 altera a partilha a partir de 2027 — conferir a tabela vigente). Anexo III × V depende do "
             "Fator R (folha/receita ≥ 28% → III).")
    emitir(args, r, txt, [aviso_desatualizado(P), *r["avisos"]])


def cmd_simples(args, P):
    al = aliquotas_ano(P, str(args.ano), args.cenario)
    R = args.receita
    avisos = [aviso_desatualizado(P)]
    if (args.anexo is None) != (args.rbt12 is None):
        falhar("informe --anexo e --rbt12 juntos.")
    if args.anexo is not None:
        calc = das_simples(args.anexo, args.rbt12, P, al["ano"])
        d = pct(args.aliquota_das) if args.aliquota_das is not None else calc["aliquota_efetiva"]
        share = pct(args.parcela_ibscbs_das) if args.parcela_ibscbs_das is not None else calc["fatia_ibscbs_no_ano"]
        origem = f"calculada — Anexo {calc['anexo']}, {calc['faixa']}ª faixa, RBT12 {brl(args.rbt12)}"
        avisos += calc["avisos"]
    elif args.aliquota_das is not None and args.parcela_ibscbs_das is not None:
        d, share, origem = pct(args.aliquota_das), pct(args.parcela_ibscbs_das), "informada"
    else:
        falhar("informe --anexo e --rbt12 (recomendado) ou --aliquota-das e --parcela-ibscbs-das.")
    b2b = pct(args.pct_b2b) or 0.0
    full = (al["cbs"] + al["ibs_uf"] + al["ibs_mun"]) * (1 - (pct(args.reducao) or 0.0))
    compras = args.compras_creditaveis or 0.0
    das = R * d
    R_b2b, R_b2c = R * b2b, R * (1 - b2b)
    cred = compras * full  # supõe fornecedores do regime regular

    a_cred_cli = R_b2b * d * share  # cliente credita só o valor pago no Simples (LC 214 art. 47 §9º)
    a_liq = R - das

    def regime_regular(pex_b2b: float, pex_b2c: float) -> dict:
        receita = pex_b2b + pex_b2c
        das_rest = receita * d * (1 - share)  # aproximação: mesma alíquota efetiva sobre a nova receita
        debito = receita * full
        a_recolher = max(debito - cred, 0.0)
        return {"receita_sem_ibscbs": r2(receita), "das_restante": r2(das_rest), "ibscbs_debito": r2(debito),
                "creditos_compras": r2(cred), "ibscbs_a_recolher": r2(a_recolher),
                "tributos_pagos": r2(das_rest + a_recolher), "receita_liquida_empresa": r2(receita - das_rest + cred),
                "credito_gerado_clientes_b2b": r2(pex_b2b * full),
                "custo_liquido_cliente_b2b_por_100": r2(100 * pex_b2b / R_b2b) if R_b2b else None,
                "preco_final_b2c_por_100": r2(100 * pex_b2c * (1 + full) / R_b2c) if R_b2c else None}

    b1 = regime_regular(R_b2b, R_b2c)                                # repasse total (teto otimista)
    b2 = regime_regular(R_b2b * (1 - d * share), R_b2c / (1 + full))  # preço neutro (comparação justa)
    ganho = r2(b2["receita_liquida_empresa"] - a_liq)
    dados = {"ano": al["ano"], "aliquota_das": rr(d), "fatia_ibscbs_das": rr(share), "origem_aliquota": origem,
             "aliquota_ibscbs_cheia": rr(full),
             "opcao_das": {"tributos_pagos": r2(das), "receita_liquida_empresa": r2(a_liq),
                           "credito_gerado_clientes_b2b": r2(a_cred_cli),
                           "custo_liquido_cliente_b2b_por_100": r2(100 * (1 - d * share)), "preco_final_b2c_por_100": 100.0},
             "regular_repasse_total": b1, "regular_preco_neutro": b2, "ganho_regular_neutro_vs_das": ganho}
    melhor = "regime regular (por fora)" if ganho > 0 else "DAS"
    nd = lambda v: "—" if v is None else brl(v)  # noqa: E731
    linhas = [
        ["Receita sem IBS/CBS", brl(R), brl(b1["receita_sem_ibscbs"]), brl(b2["receita_sem_ibscbs"])],
        ["Tributos pagos (DAS + IBS/CBS líquido)", brl(das), brl(b1["tributos_pagos"]), brl(b2["tributos_pagos"])],
        ["**Receita líquida da empresa**", f"**{brl(a_liq)}**", f"**{brl(b1['receita_liquida_empresa'])}**", f"**{brl(b2['receita_liquida_empresa'])}**"],
        ["Crédito transferido aos clientes B2B", brl(a_cred_cli), brl(b1["credito_gerado_clientes_b2b"]), brl(b2["credito_gerado_clientes_b2b"])],
        ["Custo líquido do cliente B2B (por R$ 100 de hoje)", brl(100 * (1 - d * share)), nd(b1["custo_liquido_cliente_b2b_por_100"]), nd(b2["custo_liquido_cliente_b2b_por_100"])],
        ["Preço final ao consumidor (por R$ 100 de hoje)", brl(100.0), nd(b1["preco_final_b2c_por_100"]), nd(b2["preco_final_b2c_por_100"])],
    ]
    txt = (f"## Simples Nacional — {al['ano']} — receita {brl(R)}\n"
           f"Alíquota efetiva DAS {fpct(d)} ({origem}); fatia do DAS que vira IBS/CBS {fpct(share)}; "
           f"IBS+CBS cheia {fpct(full)}; vendas B2B {fpct(b2b, 0)}; compras creditáveis {brl(compras)}.\n\n"
           + tabela_md(["Indicador", "A) IBS/CBS no DAS", "B1) Regular — repasse total", "B2) Regular — preço neutro"], linhas)
           + "\n\nComo ler: **B2 é a comparação justa** — o cliente B2B paga o mesmo custo líquido que pagava no DAS e o "
             "consumidor final paga o mesmo preço. B1 supõe que todos aceitam pagar IBS/CBS por cima do preço atual "
             "(teto otimista). Créditos de compras supõem fornecedores do regime regular: compras de MEI/Simples geram "
             "crédito bem menor. Não inclui o custo extra de contabilidade do regime regular. Decisão é semestral."
           + f"\n\nResultado no cenário neutro: **{melhor}** ({'+' if ganho >= 0 else ''}{brl(ganho)} no período, a favor do regime regular)."
           if ganho >= 0 else
           f"## Simples Nacional — {al['ano']} — receita {brl(R)}\n"
           f"Alíquota efetiva DAS {fpct(d)} ({origem}); fatia do DAS que vira IBS/CBS {fpct(share)}; "
           f"IBS+CBS cheia {fpct(full)}; vendas B2B {fpct(b2b, 0)}; compras creditáveis {brl(compras)}.\n\n"
           + tabela_md(["Indicador", "A) IBS/CBS no DAS", "B1) Regular — repasse total", "B2) Regular — preço neutro"], linhas)
           + "\n\nComo ler: **B2 é a comparação justa** — o cliente B2B paga o mesmo custo líquido que pagava no DAS e o "
             "consumidor final paga o mesmo preço. B1 supõe repasse total (teto otimista). Decisão é semestral."
           + f"\n\nResultado no cenário neutro: **DAS** (o regime regular renderia {brl(-ganho)} a menos no período).")
    if int(al["ano"]) < 2033 and args.anexo is None:
        avisos.append(f"Em {al['ano']} ICMS/ISS ainda estão no DAS: em --parcela-ibscbs-das informe só a fatia que o IBS/CBS "
                      "substitui naquele ano (2027–2028: PIS/Cofins). Prefira --anexo/--rbt12, que calcula isso.")
    emitir(args, dados, txt, avisos)


# ---------------------------------------------------------------- imóveis
def cmd_imovel(args, P):
    al = aliquotas_ano(P, str(args.ano), args.cenario)
    full = al["cbs"] + al["ibs_uf"] + al["ibs_mun"]
    I = P["imoveis"]
    avisos = [aviso_desatualizado(P)]
    if args.tipo == "locacao":
        if args.redutor_ajuste:
            avisos.append("--redutor-ajuste vale só para venda; ignorado na locação.")
        red = pct(args.reducao) if args.reducao is not None else P["reducoes"]["locacao_imoveis"]
        redutor = args.redutor if args.redutor is not None else (I["redutor_social_locacao_mensal"] if args.residencial else 0.0)
        base = max(args.valor - redutor, 0.0)
        imp = r2(base * full * (1 - red))
        n = args.imoveis or 1
        anual = args.valor * 12 * n
        limite = I["pf_locacao_limite_receita_anual"]
        pf_contrib = anual > limite and n > I["pf_locacao_limite_imoveis"]
        pf_mesmo_ano = anual > limite * I.get("pf_locacao_limite_mesmo_ano_fator", 1.2)
        dados = {"tipo": "locacao", "aluguel_mensal": args.valor, "redutor_social": redutor, "base": r2(base),
                 "aliquota_cheia": rr(full), "reducao": red, "aliquota_efetiva_sobre_base": rr(full * (1 - red)),
                 "ibscbs_mensal_por_imovel": imp, "carga_sobre_aluguel": rr(imp / args.valor) if args.valor else 0,
                 "pf_seria_contribuinte_estimado": pf_contrib, "pf_excede_120pct_no_ano": pf_mesmo_ano}
        if pf_mesmo_ano and not pf_contrib:
            avisos.append(f"Receita anual estimada ({brl(anual)}) excede em mais de 20% o limite de {brl(limite)}: pela "
                          "LC 214 art. 251 §2º, II, a PF pode virar contribuinte no próprio ano (há divergência se exige > 3 imóveis).")
        avisos.append("Limite de R$ 240 mil é atualizado mensalmente pelo IPCA (art. 251 §5º); o script usa o valor nominal.")
        txt = (f"## Locação — {al['ano']}\n\n" + tabela_md(["Item", "Valor"], [
            ["Aluguel mensal", brl(args.valor)], ["Redutor social", brl(redutor)], ["Base", brl(base)],
            ["Alíquota cheia IBS+CBS", fpct(full)], ["Redução", fpct(red, 0)],
            ["**IBS+CBS mensal (por imóvel)**", f"**{brl(imp)}**"], ["Carga sobre o aluguel", fpct(dados['carga_sobre_aluguel'])],
        ]) + f"\n\nPF: contribuinte só se, no ano anterior, a receita de aluguel passou de {brl(I['pf_locacao_limite_receita_anual'])} "
            f"E havia mais de {I['pf_locacao_limite_imoveis']} imóveis locados. Estimativa com {n} imóvel(is) iguais "
            f"({brl(anual)}/ano): {'**provavelmente contribuinte**' if pf_contrib else 'provavelmente **não** contribuinte'}.")
    else:
        red = pct(args.reducao) if args.reducao is not None else P["reducoes"]["alienacao_imoveis"]
        redutor_social = args.redutor if args.redutor is not None else (I["redutor_social_imovel_residencial_novo"] if args.residencial else 0.0)
        base = max(args.valor - (args.redutor_ajuste or 0.0) - redutor_social, 0.0)
        imp = r2(base * full * (1 - red))
        dados = {"tipo": "venda", "valor_venda": args.valor, "redutor_ajuste": args.redutor_ajuste or 0.0,
                 "redutor_social": redutor_social, "base": r2(base), "aliquota_cheia": rr(full), "reducao": red,
                 "ibscbs": imp, "carga_sobre_venda": rr(imp / args.valor) if args.valor else 0}
        txt = (f"## Alienação de imóvel — {al['ano']}\n\n" + tabela_md(["Item", "Valor"], [
            ["Valor de venda", brl(args.valor)], ["Redutor de ajuste (custo atualizado)", brl(args.redutor_ajuste or 0.0)],
            ["Redutor social", brl(redutor_social)], ["Base", brl(base)], ["Alíquota cheia IBS+CBS", fpct(full)],
            ["Redução", fpct(red, 0)], ["**IBS+CBS**", f"**{brl(imp)}**"], ["Carga sobre a venda", fpct(dados['carga_sobre_venda'])],
        ]) + "\n\nSimplificação: o redutor de ajuste real considera valor de aquisição atualizado + custos (LC 214, arts. 257–258).")
    emitir(args, dados, txt, avisos)


# ---------------------------------------------------------------- cashback / conversão
def cmd_cashback(args, P):
    al = aliquotas_ano(P, str(args.ano), args.cenario)
    C = P["cashback"]
    ano = int(al["ano"])
    on_cbs, on_ibs = ano >= C["inicio_cbs"], ano >= C["inicio_ibs"]
    full = al["cbs"] + al["ibs_uf"] + al["ibs_mun"]
    ibs_al = al["ibs_uf"] + al["ibs_mun"]
    red_d = pct(args.reducao_media_demais) or 0.0
    u, d = args.utilidades or 0.0, args.demais or 0.0

    def embutido(gasto, ali, red=0.0):  # gasto inclui o tributo (por fora) -> parcela de tributo
        return gasto * ali * (1 - red) / (1 + full * (1 - red))

    dev_cbs = r2(embutido(u, al["cbs"]) * C["utilidades"]["cbs"] + embutido(d, al["cbs"], red_d) * C["demais"]["cbs"]) if on_cbs else 0.0
    dev_ibs = r2(embutido(u, ibs_al) * C["utilidades"]["ibs"] + embutido(d, ibs_al, red_d) * C["demais"]["ibs"]) if on_ibs else 0.0
    total = r2(dev_cbs + dev_ibs)
    dados = {"ano": al["ano"], "devolucao_cbs_mensal": dev_cbs, "devolucao_ibs_mensal": dev_ibs,
             "total_mensal": total, "total_anual": r2(total * 12)}
    txt = (f"## Cashback estimado — {al['ano']}\n\n" + tabela_md(["Item", "Mensal"], [
        ["Gastos com luz/água/esgoto/gás/telecom", brl(u)], ["Demais gastos com nota (CPF)", brl(d)],
        ["Devolução CBS", brl(dev_cbs)], ["Devolução IBS", brl(dev_ibs)],
        ["**Total**", f"**{brl(total)}** ({brl(dados['total_anual'])}/ano)"],
    ]) + "\n\nRequisitos: família no CadÚnico, renda per capita até ½ salário mínimo, CPF regular. CBS a partir de "
         f"{C['inicio_cbs']}, IBS a partir de {C['inicio_ibs']}. Estados/municípios podem ampliar percentuais. "
         "Itens com alíquota zero (cesta básica) não geram devolução.")
    emitir(args, dados, txt, [aviso_desatualizado(P)])


def cmd_converter(args, P):
    a = pct(args.aliquota)
    if args.para == "dentro":
        r = a / (1 + a)
        txt = f"Alíquota {fpct(a)} **por fora** equivale a **{fpct(r)} por dentro** (peso no preço final)."
    else:
        if a >= 1:
            falhar("alíquota por dentro deve ser menor que 100%.")
        r = a / (1 - a)
        txt = f"Alíquota {fpct(a)} **por dentro** equivale a **{fpct(r)} por fora** (sobre o preço sem tributo)."
    emitir(args, {"entrada": rr(a), "resultado": rr(r), "para": args.para}, txt)


# ---------------------------------------------------------------- CLI
def construir_parser() -> argparse.ArgumentParser:
    comum = argparse.ArgumentParser(add_help=False)
    comum.add_argument("--parametros", default=argparse.SUPPRESS, help="caminho alternativo do parametros.json")
    comum.add_argument("--cenario", default=argparse.SUPPRESS, help="cenário de alíquotas (ver parametros.json)")
    comum.add_argument("--json", action="store_true", default=argparse.SUPPRESS, help="saída JSON")

    ap = argparse.ArgumentParser(parents=[comum],
                                 description="Calculadora da Reforma Tributária (IBS/CBS/IS). Percentuais SEMPRE em %: 18 = 18%, 0.9 = 0,9%.")
    sub = ap.add_subparsers(dest="cmd", required=True)
    V, PCT, ANO = valor_nao_negativo, percentual, ano_valido

    s = sub.add_parser("cronograma", parents=[comum], help="alíquotas ano a ano"); s.set_defaults(func=cmd_cronograma)

    s = sub.add_parser("operacao", parents=[comum], help="IBS/CBS/IS de uma operação")
    s.add_argument("--valor", type=V, required=True, help="valor da operação sem IBS/CBS (sem ICMS/ISS/PIS/Cofins na transição)")
    s.add_argument("--ano", type=ANO, default=2027)
    s.add_argument("--reducao", type=PCT, default=0, help="redução de alíquota em %%: 30, 40, 60, 100")
    s.add_argument("--aliq-is", type=PCT, help="alíquota ad valorem do Imposto Seletivo, em %%")
    s.add_argument("--cbs", type=PCT, help="sobrescreve a alíquota da CBS, em %% (ex.: 0.9)")
    s.add_argument("--ibs-uf", type=PCT, help="sobrescreve a alíquota do IBS estadual, em %%")
    s.add_argument("--ibs-mun", type=PCT, help="sobrescreve a alíquota do IBS municipal, em %%")
    s.set_defaults(func=cmd_operacao)

    s = sub.add_parser("transicao", parents=[comum], help="carga ano a ano mantendo a receita líquida")
    s.add_argument("--valor", type=V, required=True, help="preço atual 'por dentro' (com ICMS/ISS/PIS/Cofins, sem IPI)")
    s.add_argument("--icms", type=PCT, default=0); s.add_argument("--iss", type=PCT, default=0)
    s.add_argument("--pis-cofins", type=PCT, default=0, help="9.25 não cumulativo; 3.65 cumulativo")
    s.add_argument("--ipi", type=PCT, default=0); s.add_argument("--zfm", action="store_true", help="produto incentivado ZFM mantém IPI")
    s.add_argument("--reducao", type=PCT, default=0); s.add_argument("--aliq-is", type=PCT)
    s.add_argument("--compras", type=V, help="compras creditáveis do período (valor sem tributos novos)")
    s.add_argument("--compras-icms", type=PCT, help="ICMS creditável nas compras hoje, em %%")
    s.add_argument("--compras-pis-cofins", type=PCT, help="PIS/Cofins creditável nas compras hoje, em %%")
    s.add_argument("--reducao-compras", type=PCT, help="redução média de IBS/CBS das compras, em %%")
    s.add_argument("--cobrar-2026", action="store_true", help="tratar 2026 como recolhido (sem dispensa)")
    s.set_defaults(func=cmd_transicao)

    s = sub.add_parser("das", parents=[comum], help="faixa, alíquota efetiva e partilha do DAS (LC 123)")
    s.add_argument("--anexo", required=True, help="I, II, III, IV ou V")
    s.add_argument("--rbt12", type=V, required=True, help="receita bruta dos últimos 12 meses")
    s.add_argument("--ano", type=ANO, default=2033)
    s.set_defaults(func=cmd_das)

    s = sub.add_parser("simples", parents=[comum], help="Simples Nacional: DAS x regime regular")
    s.add_argument("--receita", type=V, required=True, help="receita do período (mês ou ano)")
    s.add_argument("--anexo", help="Anexo do Simples (I–V) — calcula DAS e partilha automaticamente")
    s.add_argument("--rbt12", type=V, help="receita bruta dos últimos 12 meses (define a faixa)")
    s.add_argument("--aliquota-das", type=PCT, help="alíquota efetiva do DAS em %% (só se não usar --anexo/--rbt12)")
    s.add_argument("--parcela-ibscbs-das", type=PCT, help="%% do DAS que o IBS/CBS substitui (só se não usar --anexo/--rbt12)")
    s.add_argument("--pct-b2b", type=PCT, default=0, help="%% das vendas para contribuintes do regime regular")
    s.add_argument("--compras-creditaveis", type=V, help="compras do período que gerariam crédito no regime regular")
    s.add_argument("--reducao", type=PCT, default=0); s.add_argument("--ano", type=ANO, default=2033)
    s.set_defaults(func=cmd_simples)

    s = sub.add_parser("imovel", parents=[comum], help="locação ou venda de imóvel")
    s.add_argument("tipo", choices=["locacao", "venda"])
    s.add_argument("--valor", type=V, required=True, help="aluguel mensal ou valor de venda")
    s.add_argument("--redutor", type=V, help="redutor social (padrão conforme parametros)")
    s.add_argument("--redutor-ajuste", type=V, help="venda: custo de aquisição atualizado + custos")
    s.add_argument("--residencial", action="store_true", help="aplica redutor social residencial")
    s.add_argument("--imoveis", type=int, help="quantidade de imóveis locados (teste de contribuinte PF)")
    s.add_argument("--reducao", type=PCT); s.add_argument("--ano", type=ANO, default=2033)
    s.set_defaults(func=cmd_imovel)

    s = sub.add_parser("cashback", parents=[comum], help="estimativa de devolução (CadÚnico)")
    s.add_argument("--utilidades", type=V, help="gasto mensal com energia, água, esgoto, gás, telecom")
    s.add_argument("--demais", type=V, help="demais gastos mensais com nota no CPF")
    s.add_argument("--reducao-media-demais", type=PCT, help="redução média de alíquota nos demais gastos, em %%")
    s.add_argument("--ano", type=ANO, default=2033)
    s.set_defaults(func=cmd_cashback)

    s = sub.add_parser("converter", parents=[comum], help="converter alíquota por fora <-> por dentro")
    s.add_argument("--aliquota", type=PCT, required=True, help="alíquota em %%")
    s.add_argument("--para", choices=["dentro", "fora"], default="dentro")
    s.set_defaults(func=cmd_converter)
    return ap


def main(argv=None) -> int:
    for s in (sys.stdout, sys.stderr):
        if hasattr(s, "reconfigure"):
            s.reconfigure(encoding="utf-8")
    args = construir_parser().parse_args(argv)
    for k, v in (("json", False), ("cenario", None), ("parametros", None)):
        if not hasattr(args, k):
            setattr(args, k, v)
    P = carregar_parametros(args.parametros)
    if args.cenario and args.cenario not in P["cenarios"]:
        falhar(f"cenário inválido. Opções: {', '.join(P['cenarios'])}")
    args.func(args, P)
    return 0


if __name__ == "__main__":
    sys.exit(main())
