import csv
import tempfile
import unittest
from pathlib import Path

from processamento.erros import ErroProcessamento
from processamento.gerador_csv import GeradorCsv


class GeradorCsvTest(unittest.TestCase):
    """Testa a geração do arquivo CSV."""

    COLUNAS = ("id", "nome", "cpf")

    def setUp(self):
        self._tmp = tempfile.TemporaryDirectory()
        self.addCleanup(self._tmp.cleanup)
        self.pasta = Path(self._tmp.name)
        self.caminho = self.pasta / "aprovados.csv"

    def ler_linhas(self):
        with open(self.caminho, encoding="utf-8", newline="") as arquivo:
            return list(csv.reader(arquivo, delimiter=";"))

    def test_gera_cabecalho_e_linhas(self):
        registros = [{"id": 1, "nome": "Maria", "cpf": "111"}]
        GeradorCsv(self.caminho, self.COLUNAS).gerar(registros)
        self.assertEqual(self.ler_linhas(), [["id", "nome", "cpf"], ["1", "Maria", "111"]])

    def test_sem_registros_gera_apenas_cabecalho(self):
        GeradorCsv(self.caminho, self.COLUNAS).gerar([])
        self.assertEqual(self.ler_linhas(), [["id", "nome", "cpf"]])

    def test_arquivo_usa_utf8_e_preserva_acentos(self):
        GeradorCsv(self.caminho, self.COLUNAS).gerar([{"id": 1, "nome": "João Conceição", "cpf": "1"}])
        self.assertIn("João Conceição", self.caminho.read_text(encoding="utf-8"))

    def test_valor_com_separador_e_protegido_com_aspas(self):
        GeradorCsv(self.caminho, self.COLUNAS).gerar([{"id": 1, "nome": "Ana; Maria", "cpf": "1"}])
        self.assertEqual(self.ler_linhas()[1][1], "Ana; Maria")

    def test_respeita_separador_configurado(self):
        GeradorCsv(self.caminho, self.COLUNAS, separador=",").gerar([{"id": 1, "nome": "Ana", "cpf": "1"}])
        self.assertEqual(self.caminho.read_text(encoding="utf-8").splitlines()[0], "id,nome,cpf")

    def test_sobrescreve_arquivo_existente(self):
        gerador = GeradorCsv(self.caminho, self.COLUNAS)
        gerador.gerar([{"id": 1, "nome": "Ana", "cpf": "1"}])
        gerador.gerar([])
        self.assertEqual(len(self.ler_linhas()), 1)

    def test_nao_deixa_arquivo_temporario(self):
        GeradorCsv(self.caminho, self.COLUNAS).gerar([])
        self.assertEqual([p.name for p in self.pasta.iterdir()], ["aprovados.csv"])

    def test_pasta_inexistente_levanta_erro(self):
        gerador = GeradorCsv(self.pasta / "inexistente" / "aprovados.csv", self.COLUNAS)
        with self.assertRaisesRegex(ErroProcessamento, "Falha ao gerar o CSV"):
            gerador.gerar([])

    def test_registro_com_chave_inesperada_levanta_erro_e_limpa_temporario(self):
        gerador = GeradorCsv(self.caminho, self.COLUNAS)
        with self.assertRaises(ErroProcessamento):
            gerador.gerar([{"id": 1, "nome": "Ana", "cpf": "1", "extra": "x"}])
        self.assertFalse(self.caminho.exists())
        self.assertEqual(list(self.pasta.iterdir()), [])


if __name__ == "__main__":
    unittest.main()
