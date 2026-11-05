import os
import tempfile
import unittest
from pathlib import Path

from _util import EXEMPLOS, rodar, rodar_json

import validar_nfe
from validar_nfe import dv_mod11, validar_arquivo

NS = 'xmlns="http://www.portalfiscal.inf.br/nfe"'


def chave(base43: str) -> str:
    return base43 + str(dv_mod11(base43))


def item(n, vbc, pcbs=0.9, vcbs=None, cst="000", cct="000001", extra_cbs=""):
    vcbs = round(vbc * pcbs / 100, 2) if vcbs is None else vcbs
    vuf = round(vbc * 0.1 / 100, 2)
    return (f'<det nItem="{n}"><prod><vProd>{vbc:.2f}</vProd></prod><imposto><IBSCBS><CST>{cst}</CST>'
            f'<cClassTrib>{cct}</cClassTrib><gIBSCBS><vBC>{vbc:.2f}</vBC><gIBSUF><pIBSUF>0.1000</pIBSUF><vIBSUF>{vuf:.2f}</vIBSUF></gIBSUF>'
            f'<gIBSMun><pIBSMun>0.0000</pIBSMun><vIBSMun>0.00</vIBSMun></gIBSMun><vIBS>{vuf:.2f}</vIBS>'
            f'<gCBS><pCBS>{pcbs:.4f}</pCBS>{extra_cbs}<vCBS>{vcbs:.2f}</vCBS></gCBS></gIBSCBS></IBSCBS></imposto></det>')


def nota(itens, tot_cbs, tot_ibs, nnf=7, cnf="12345678", dh="2026-11-04"):
    k = chave(f"352611000000000001005500100000{nnf:04d}{nnf % 10 if False else ''}"[:25] + f"{nnf:09d}"[-9:] + "1" + cnf)
    return (f'<NFe {NS}><infNFe Id="NFe{k}" versao="4.00"><ide><mod>55</mod><nNF>{nnf}</nNF><dhEmi>{dh}T10:00:00-03:00</dhEmi></ide>'
            f'<emit><CRT>3</CRT></emit>{"".join(itens)}<total><IBSCBSTot><gIBS><vIBS>{tot_ibs:.2f}</vIBS></gIBS>'
            f'<gCBS><vCBS>{tot_cbs:.2f}</vCBS></gCBS></IBSCBSTot></total></infNFe></NFe>')


def erros(res):
    return [p for r in res for p in r["problemas"] if p["severidade"] == "ERRO"]


class Base(unittest.TestCase):
    def xml(self, conteudo, nome="t.xml"):
        d = tempfile.mkdtemp()
        p = Path(d) / nome
        p.write_text('<?xml version="1.0" encoding="UTF-8"?>' + conteudo, encoding="utf-8")
        return p


class TestExemplos(Base):
    def test_exemplo_valido_sem_erro(self):
        self.assertEqual(erros(validar_arquivo(EXEMPLOS / "nfe_exemplo_2026.xml", None)), [])

    def test_exemplo_com_erros(self):
        msgs = " | ".join(p["mensagem"] for p in erros(validar_arquivo(EXEMPLOS / "nfe_com_erros_2026.xml", None)))
        for esperado in ("Dígito verificador", "AAMM", "Grupo IBSCBS ausente", "não corresponde ao CST 200", "vCBS informado 2.70", "IBSCBSTot/vCBS 5.00"):
            self.assertIn(esperado, msgs)

    def test_codigo_de_saida(self):
        self.assertEqual(rodar(validar_nfe.main, [str(EXEMPLOS / "nfe_exemplo_2026.xml")])[0], 0)
        self.assertEqual(rodar(validar_nfe.main, [str(EXEMPLOS / "nfe_com_erros_2026.xml")])[0], 1)


class TestRegras(Base):
    def test_nota_correta(self):
        p = self.xml(nota([item(1, 1000), item(2, 300)], 11.70, 1.30))
        self.assertEqual(erros(validar_arquivo(p, None)), [])

    def test_lote_com_duas_notas_validadas_separadamente(self):
        n1 = nota([item(1, 100)], 0.90, 0.10, nnf=1)
        n2 = nota([item(1, 200)], 1.80, 0.20, nnf=2)
        p = self.xml(f'<enviNFe {NS}>{n1}{n2}</enviNFe>')
        res = validar_arquivo(p, None)
        self.assertEqual(len(res), 2)
        self.assertEqual(erros(res), [])

    def test_total_errado_com_muitos_itens(self):
        itens = [item(i, 100) for i in range(1, 51)]
        p = self.xml(nota(itens, 44.10, 5.00))  # correto seria 45,00
        self.assertTrue(any("vCBS" in e["mensagem"] for e in erros(validar_arquivo(p, None))))

    def test_gred_consistente_e_inconsistente(self):
        ok = '<gRed><pRedAliq>60.0000</pRedAliq><pAliqEfet>0.3600</pAliqEfet></gRed>'
        ruim = '<gRed><pRedAliq>60.0000</pRedAliq><pAliqEfet>0.5000</pAliqEfet></gRed>'
        p1 = self.xml(nota([item(1, 100, vcbs=0.36, cst="200", cct="200034", extra_cbs=ok)], 0.36, 0.10))
        p2 = self.xml(nota([item(1, 100, vcbs=0.50, cst="200", cct="200034", extra_cbs=ruim)], 0.50, 0.10))
        self.assertEqual(erros(validar_arquivo(p1, None)), [])
        self.assertTrue(any("pAliqEfet" in e["mensagem"] for e in erros(validar_arquivo(p2, None))))

    def test_diferimento_nao_gera_falso_erro(self):
        dif = '<gDif><pDif>100.0000</pDif><vDif>0.90</vDif></gDif>'
        p = self.xml(nota([item(1, 100, vcbs=0.0, cst="510", cct="510001", extra_cbs=dif)], 0.0, 0.10))
        self.assertFalse(any("vCBS informado" in e["mensagem"] for e in erros(validar_arquivo(p, None))))

    def test_virgula_decimal_e_arquivo_ruim_nao_abortam_lote(self):
        ruim = self.xml(nota([item(1, 100)], 0.90, 0.10).replace("<vIBS>0.10</vIBS><gCBS>", "<vIBS>0,10</vIBS><gCBS>"))
        quebrado = self.xml("<NFe><infNFe>", "q.xml")
        inexistente = Path(tempfile.mkdtemp()) / "nao.xml"
        for p in (ruim, quebrado, inexistente):
            self.assertTrue(erros(validar_arquivo(p, None)), p)

    def test_simples_sem_grupo_em_2026_e_alerta(self):
        x = nota([item(1, 100)], 0.0, 0.0).replace("<CRT>3</CRT>", "<CRT>1</CRT>")
        x = x.replace(x[x.index("<IBSCBS>"):x.index("</IBSCBS>") + 9], "")
        res = validar_arquivo(self.xml(x), None)
        self.assertEqual(erros(res), [])
        self.assertTrue(any(p["severidade"] == "ALERTA" for p in res[0]["problemas"]))

    def test_json_e_csv(self):
        d = tempfile.mkdtemp()
        csv = os.path.join(d, "p.csv")
        codigo, res = rodar_json(validar_nfe.main, [str(EXEMPLOS / "nfe_com_erros_2026.xml"), "--csv", csv])
        self.assertEqual(codigo, 1)
        self.assertEqual(len(res), 1)
        texto = Path(csv).read_text(encoding="utf-8-sig")
        self.assertTrue(texto.startswith("arquivo;chave;local;severidade;mensagem"))


if __name__ == "__main__":
    unittest.main()
