import unittest

from _util import rodar, rodar_json

import rt_calc
from rt_calc import aliquotas_ano, calc_ibscbs, carregar_parametros, das_simples

P = carregar_parametros(None)


class TestAliquotas(unittest.TestCase):
    def test_cronograma_2026_teste(self):
        a = aliquotas_ano(P, "2026", "tcu_cgibs")
        self.assertEqual((a["cbs"], a["ibs_uf"], a["ibs_mun"]), (0.009, 0.001, 0.0))

    def test_cbs_2027_desconta_0_1pp(self):
        a = aliquotas_ano(P, "2027", "tcu_cgibs")
        self.assertAlmostEqual(a["cbs"], 0.112)
        self.assertAlmostEqual(a["ibs_uf"] + a["ibs_mun"], 0.001)

    def test_2033_soma_cenario(self):
        a = aliquotas_ano(P, "2033", "tcu_cgibs")
        self.assertAlmostEqual(a["cbs"] + a["ibs_uf"] + a["ibs_mun"], 0.30)

    def test_totais_sao_soma_dos_arredondados(self):
        al = aliquotas_ano(P, "2033", "tcu_cgibs")
        for centavos in range(1, 200001, 37):
            r = calc_ibscbs(centavos / 100, al)
            self.assertAlmostEqual(r["total_ibscbs"], round(r["cbs"] + r["ibs_uf"] + r["ibs_mun"], 2), places=9)


class TestOperacao(unittest.TestCase):
    def test_percentual_sempre_em_porcento(self):
        # regressão do bug crítico: 0.9 deve ser 0,9% e não 90%
        _, d = rodar_json(rt_calc.main, ["operacao", "--valor", "1000", "--ano", "2026", "--cbs", "0.9", "--ibs-uf", "0.1"])
        self.assertEqual(d["resultado"]["cbs"], 9.0)
        self.assertEqual(d["resultado"]["ibs_uf"], 1.0)

    def test_reducao_60_em_2027(self):
        _, d = rodar_json(rt_calc.main, ["operacao", "--valor", "1000", "--ano", "2027", "--reducao", "60"])
        r = d["resultado"]
        self.assertEqual((r["cbs"], r["ibs_uf"], r["ibs_mun"], r["total_ibscbs"]), (44.8, 0.2, 0.2, 45.2))

    def test_is_integra_base(self):
        _, d = rodar_json(rt_calc.main, ["operacao", "--valor", "1000", "--ano", "2027", "--aliq-is", "10"])
        self.assertEqual(d["resultado"]["imposto_seletivo"], 100.0)
        self.assertEqual(d["resultado"]["base_ibscbs"], 1100.0)
        self.assertEqual(d["resultado"]["cbs"], 123.2)

    def test_is_zero_em_2026_com_aviso(self):
        _, d = rodar_json(rt_calc.main, ["operacao", "--valor", "1000", "--ano", "2026", "--aliq-is", "10"])
        self.assertEqual(d["resultado"]["imposto_seletivo"], 0.0)
        self.assertTrue(any("Seletivo" in a for a in d.get("avisos", [])))

    def test_json_antes_ou_depois(self):
        c1, s1 = rodar(rt_calc.main, ["--json", "operacao", "--valor", "100"])
        c2, s2 = rodar(rt_calc.main, ["operacao", "--valor", "100", "--json"])
        self.assertEqual((c1, c2), (0, 0))
        import json
        self.assertEqual(json.loads(s1)["resultado"], json.loads(s2)["resultado"])

    def test_entradas_invalidas_saem_sem_traceback(self):
        for argv in (["operacao", "--valor", "-1"], ["operacao", "--valor", "nan"], ["operacao", "--valor", "1", "--ano", "2020"],
                     ["operacao", "--valor", "1", "--reducao", "150"], ["--cenario", "xx", "cronograma"],
                     ["--parametros", "nao-existe.json", "cronograma"], ["converter", "--aliquota", "100", "--para", "fora"]):
            codigo, _ = rodar(rt_calc.main, argv)
            self.assertNotEqual(codigo, 0, argv)


class TestTransicao(unittest.TestCase):
    def test_produto_icms_pis_cofins(self):
        _, d = rodar_json(rt_calc.main, ["transicao", "--valor", "100", "--icms", "18", "--pis-cofins", "9.25"])
        tot = {a["ano"]: a["total_cliente"] for a in d["anos"]}
        self.assertEqual(tot["2026"], 100.0)
        self.assertEqual(tot["2027"], 99.16)
        self.assertEqual(tot["2033"], 96.74)
        self.assertTrue(all(a["receita_liquida"] == 74.42 for a in d["anos"]))

    def test_servico_presumido_preco_fixo(self):
        _, d = rodar_json(rt_calc.main, ["transicao", "--valor", "80000", "--iss", "2", "--pis-cofins", "3.65", "--reducao", "60"])
        a33 = d["anos"][-1]
        self.assertEqual(a33["ano"], "2033")
        self.assertAlmostEqual(a33["perda_margem_preco_fixo"], -4051.43, places=2)

    def test_denominador_invalido(self):
        codigo, _ = rodar(rt_calc.main, ["transicao", "--valor", "100", "--icms", "60", "--pis-cofins", "100"])
        self.assertNotEqual(codigo, 0)


class TestSimples(unittest.TestCase):
    def test_anexo_iii_faixa4(self):
        r = das_simples("III", 1_200_000, P, "2027")
        self.assertEqual(r["faixa"], 4)
        self.assertAlmostEqual(r["aliquota_efetiva"], 0.1303)
        self.assertAlmostEqual(r["fatia_ibscbs_no_ano"], 0.166)  # PIS 2,96% + Cofins 13,64%

    def test_clinica_960k(self):
        self.assertAlmostEqual(das_simples("III", 960_000, P)["aliquota_efetiva"], 0.122875, places=6)

    def test_teto_iss_5a_faixa(self):
        r = das_simples("iii", 3_000_000, P)
        self.assertAlmostEqual(r["aliquota_efetiva"], 0.16812, places=5)
        self.assertAlmostEqual(r["reparticao"]["ISS"] * r["aliquota_efetiva"], 0.05, places=6)
        self.assertAlmostEqual(sum(r["reparticao"].values()), 1.0, places=5)

    def test_anexo_iv_sem_teto(self):
        r = das_simples("IV", 1_800_001, P)
        self.assertEqual(r["faixa"], 5)
        self.assertLess(r["aliquota_efetiva"], 0.125)

    def test_rbt12_zero_e_limite(self):
        self.assertAlmostEqual(das_simples("III", 0, P)["aliquota_efetiva"], 0.06)
        self.assertEqual(das_simples("III", 4_800_000, P)["faixa"], 6)
        with self.assertRaises(SystemExit):
            das_simples("III", 4_800_001, P)

    def test_fatia_por_ano(self):
        self.assertEqual(das_simples("I", 100_000, P, "2026")["fatia_ibscbs_no_ano"], 0.0)
        self.assertAlmostEqual(das_simples("I", 100_000, P, "2029")["fatia_ibscbs_no_ano"], 0.189)

    def test_simples_neutro(self):
        _, d = rodar_json(rt_calc.main, ["simples", "--receita", "100000", "--anexo", "III", "--rbt12", "1200000",
                                         "--pct-b2b", "85", "--compras-creditaveis", "30000", "--ano", "2027"])
        self.assertAlmostEqual(d["aliquota_das"], 0.1303)
        self.assertAlmostEqual(d["ganho_regular_neutro_vs_das"], 2556.82, places=2)
        self.assertEqual(d["regular_preco_neutro"]["custo_liquido_cliente_b2b_por_100"], d["opcao_das"]["custo_liquido_cliente_b2b_por_100"])

    def test_simples_sem_compras_favorece_das(self):
        _, d = rodar_json(rt_calc.main, ["simples", "--receita", "100000", "--anexo", "III", "--rbt12", "1200000",
                                         "--pct-b2b", "85", "--ano", "2027"])
        self.assertLess(d["ganho_regular_neutro_vs_das"], 0)

    def test_pct_b2b_1_diferente_de_100(self):
        base = ["simples", "--receita", "1000", "--anexo", "III", "--rbt12", "500000"]
        _, a = rodar_json(rt_calc.main, base + ["--pct-b2b", "1"])
        _, b = rodar_json(rt_calc.main, base + ["--pct-b2b", "100"])
        self.assertNotEqual(a["opcao_das"]["credito_gerado_clientes_b2b"], b["opcao_das"]["credito_gerado_clientes_b2b"])


class TestImovelCashback(unittest.TestCase):
    def test_locacao(self):
        _, d = rodar_json(rt_calc.main, ["imovel", "locacao", "--valor", "3000", "--residencial"])
        self.assertEqual((d["base"], d["ibscbs_mensal_por_imovel"]), (2400.0, 216.0))

    def test_locacao_pf_contribuinte(self):
        _, a = rodar_json(rt_calc.main, ["imovel", "locacao", "--valor", "3000", "--imoveis", "5"])
        _, b = rodar_json(rt_calc.main, ["imovel", "locacao", "--valor", "3000", "--imoveis", "7"])
        self.assertFalse(a["pf_seria_contribuinte_estimado"])
        self.assertTrue(b["pf_seria_contribuinte_estimado"])

    def test_venda(self):
        _, d = rodar_json(rt_calc.main, ["imovel", "venda", "--valor", "800000", "--redutor-ajuste", "500000", "--residencial"])
        self.assertEqual((d["base"], d["ibscbs"]), (200000.0, 30000.0))

    def test_cashback(self):
        _, d = rodar_json(rt_calc.main, ["cashback", "--utilidades", "350", "--demais", "1200"])
        self.assertEqual((d["devolucao_cbs_mensal"], d["devolucao_ibs_mensal"]), (51.28, 44.59))
        self.assertEqual(d["total_mensal"], 95.87)
        _, d27 = rodar_json(rt_calc.main, ["cashback", "--utilidades", "350", "--ano", "2027"])
        self.assertEqual(d27["devolucao_ibs_mensal"], 0.0)
        _, d26 = rodar_json(rt_calc.main, ["cashback", "--utilidades", "350", "--ano", "2026"])
        self.assertEqual(d26["total_mensal"], 0.0)

    def test_converter_ida_e_volta(self):
        _, d = rodar_json(rt_calc.main, ["converter", "--aliquota", "28"])
        self.assertAlmostEqual(d["resultado"], 0.21875)
        _, v = rodar_json(rt_calc.main, ["converter", "--aliquota", "21.875", "--para", "fora"])
        self.assertAlmostEqual(v["resultado"], 0.28)


class TestTodosSubcomandosJson(unittest.TestCase):
    def test_json_valido(self):
        casos = [["cronograma"], ["operacao", "--valor", "1"], ["transicao", "--valor", "1"], ["das", "--anexo", "I", "--rbt12", "1"],
                 ["simples", "--receita", "1", "--anexo", "I", "--rbt12", "1"], ["imovel", "venda", "--valor", "1"],
                 ["cashback"], ["converter", "--aliquota", "1"]]
        for c in casos:
            codigo, _ = rodar_json(rt_calc.main, c)
            self.assertEqual(codigo, 0, c)


if __name__ == "__main__":
    unittest.main()
