import json
import tempfile
import unittest
from pathlib import Path

from processamento.erros import ErroProcessamento
from processamento.leitor_json import LeitorJson


class LeitorJsonTest(unittest.TestCase):
    """Testa a leitura do arquivo JSON de entrada."""

    def setUp(self):
        self._tmp = tempfile.TemporaryDirectory()
        self.addCleanup(self._tmp.cleanup)
        self.caminho = Path(self._tmp.name) / "entrada.json"

    def test_le_lista_de_registros(self):
        dados = [{"id": 1, "nome": "João"}, "qualquer coisa"]
        self.caminho.write_text(json.dumps(dados), encoding="utf-8")
        self.assertEqual(LeitorJson(self.caminho).ler(), dados)

    def test_lista_vazia(self):
        self.caminho.write_text("[]", encoding="utf-8")
        self.assertEqual(LeitorJson(self.caminho).ler(), [])

    def test_arquivo_nao_encontrado(self):
        with self.assertRaisesRegex(ErroProcessamento, "não encontrado"):
            LeitorJson(self.caminho).ler()

    def test_json_invalido(self):
        self.caminho.write_text("{ isto não é json", encoding="utf-8")
        with self.assertRaisesRegex(ErroProcessamento, "JSON inválido"):
            LeitorJson(self.caminho).ler()

    def test_raiz_que_nao_e_lista(self):
        self.caminho.write_text('{"id": 1}', encoding="utf-8")
        with self.assertRaisesRegex(ErroProcessamento, "Estrutura inesperada"):
            LeitorJson(self.caminho).ler()

    def test_arquivo_com_codificacao_invalida(self):
        self.caminho.write_bytes(b"\xff\xfe\x00[")
        with self.assertRaises(ErroProcessamento):
            LeitorJson(self.caminho).ler()


if __name__ == "__main__":
    unittest.main()
