import csv
import json
import tempfile
import unittest
from pathlib import Path

import main


class CriarConfiguracaoTest(unittest.TestCase):
    """Testa a leitura dos argumentos de linha de comando."""

    def test_valores_padrao_ficam_ao_lado_do_main(self):
        configuracao = main.criar_configuracao([])
        self.assertEqual(configuracao.arquivo_entrada, main.PASTA_BASE / "solicitacoes.json")
        self.assertEqual(configuracao.arquivo_saida, main.PASTA_BASE / "aprovados.csv")
        self.assertEqual(configuracao.arquivo_log, main.PASTA_BASE / "processamento.log")
        self.assertEqual(configuracao.separador_csv, ";")

    def test_argumentos_sobrescrevem_padroes(self):
        configuracao = main.criar_configuracao(
            ["--entrada", "a.json", "--saida", "b.csv", "--log", "c.log"]
        )
        self.assertEqual(configuracao.arquivo_entrada, Path("a.json"))
        self.assertEqual(configuracao.arquivo_saida, Path("b.csv"))
        self.assertEqual(configuracao.arquivo_log, Path("c.log"))


class MainTest(unittest.TestCase):
    """Testa o ponto de entrada da aplicação."""

    def test_main_retorna_zero_e_gera_arquivos(self):
        with tempfile.TemporaryDirectory() as pasta:
            pasta = Path(pasta)
            (pasta / "e.json").write_text(
                json.dumps([{"id": 1, "nome": "Ana", "cpf": "1", "status": "APROVADO"}]),
                encoding="utf-8",
            )
            codigo = main.main(
                ["--entrada", str(pasta / "e.json"),
                 "--saida", str(pasta / "s.csv"),
                 "--log", str(pasta / "l.log")]
            )
            self.assertEqual(codigo, 0)
            with open(pasta / "s.csv", encoding="utf-8", newline="") as arquivo:
                self.assertEqual(
                    list(csv.reader(arquivo, delimiter=";")),
                    [["id", "nome", "cpf"], ["1", "Ana", "1"]],
                )
            self.assertTrue((pasta / "l.log").exists())

    def test_main_retorna_um_quando_entrada_nao_existe(self):
        with tempfile.TemporaryDirectory() as pasta:
            pasta = Path(pasta)
            codigo = main.main(
                ["--entrada", str(pasta / "nao_existe.json"),
                 "--saida", str(pasta / "s.csv"),
                 "--log", str(pasta / "l.log")]
            )
            self.assertEqual(codigo, 1)


if __name__ == "__main__":
    unittest.main()
