import tempfile
import unittest
from pathlib import Path

from _util import rodar, rodar_json

import consultar_cclasstrib as cc


class TestConsulta(unittest.TestCase):
    def test_cst_200(self):
        _, d = rodar_json(cc.main, ["200"])
        self.assertGreaterEqual(d["total"], 5)
        self.assertTrue(all(r["cst"] == "200" for r in d["resultados"]))

    def test_cclasstrib_exato(self):
        _, d = rodar_json(cc.main, ["000001"])
        self.assertEqual([r["cclasstrib"] for r in d["resultados"]], ["000001"])

    def test_acentos_e_maiusculas(self):
        _, a = rodar_json(cc.main, ["CESTA BÁSICA"])
        _, b = rodar_json(cc.main, ["cesta basica"])
        self.assertEqual(a["resultados"], b["resultados"])
        self.assertEqual(a["resultados"][0]["cclasstrib"], "200003")

    def test_fisioterapia_acha_saude(self):
        _, d = rodar_json(cc.main, ["fisioterapia"])
        self.assertEqual(d["resultados"][0]["cclasstrib"], "200029")

    def test_sem_resultado_e_termo_vazio(self):
        codigo, d = rodar_json(cc.main, ["999999"])
        self.assertEqual((codigo, d["total"]), (0, 0))
        self.assertNotEqual(rodar(cc.main, ["  "])[0], 0)

    def test_csv_windows_1252(self):
        p = Path(tempfile.mkdtemp()) / "tabela.csv"
        p.write_bytes("CST;cClassTrib;Descrição\n200;200047;Alimentação em restaurante\n".encode("cp1252"))
        _, d = rodar_json(cc.main, ["restaurante", "--tabela", str(p)])
        self.assertEqual(d["total"], 1)

    def test_arquivo_inexistente(self):
        self.assertNotEqual(rodar(cc.main, ["x", "--tabela", "nao-existe.csv"])[0], 0)


if __name__ == "__main__":
    unittest.main()
