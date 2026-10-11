import csv
import json
import tempfile
import unittest
from pathlib import Path

from processamento.configuracao import Configuracao
from processamento.processador_solicitacoes import ProcessadorSolicitacoes


class ProcessadorSolicitacoesTest(unittest.TestCase):
    """Testa o fluxo completo (leitura, filtragem, CSV e log)."""

    def setUp(self):
        self._tmp = tempfile.TemporaryDirectory()
        self.addCleanup(self._tmp.cleanup)
        pasta = Path(self._tmp.name)
        self.entrada = pasta / "entrada.json"
        self.saida = pasta / "aprovados.csv"
        self.log = pasta / "processamento.log"

    def executar(self):
        configuracao = Configuracao(self.entrada, self.saida, self.log)
        return ProcessadorSolicitacoes(configuracao).executar()

    def ler_log(self):
        return self.log.read_text(encoding="utf-8")

    def test_fluxo_completo(self):
        dados = [
            {"id": 1, "nome": "Maria Silva", "cpf": "111", "status": "APROVADO"},
            {"id": 2, "nome": "Pedro", "cpf": "222", "status": "PENDENTE"},
            {"id": 3, "nome": "Ana", "cpf": "", "status": "APROVADO"},
            {"id": 4, "nome": "João; Teste", "cpf": "444", "status": "APROVADO"},
            "lixo",
        ]
        self.entrada.write_text(json.dumps(dados), encoding="utf-8")

        self.assertEqual(self.executar(), ProcessadorSolicitacoes.CODIGO_SUCESSO)

        with open(self.saida, encoding="utf-8", newline="") as arquivo:
            linhas = list(csv.reader(arquivo, delimiter=";"))
        self.assertEqual(linhas[0], ["id", "nome", "cpf"])
        self.assertEqual(linhas[1:], [["1", "Maria Silva", "111"], ["4", "João; Teste", "444"]])

        log = self.ler_log()
        self.assertIn("Início do processamento", log)
        self.assertIn("Total de registros lidos: 5", log)
        self.assertIn("Total de registros exportados: 2", log)
        self.assertIn("Total de registros ignorados: 3", log)
        self.assertIn("posição 3, id=3", log)
        self.assertIn("cpf vazio", log)
        self.assertIn("Processamento concluído com sucesso", log)

    def test_log_nao_expoe_cpf_nem_nome(self):
        dados = [{"id": 9, "nome": "Fulano Secreto", "cpf": "99999999999", "status": "PENDENTE"}]
        self.entrada.write_text(json.dumps(dados), encoding="utf-8")
        self.executar()
        log = self.ler_log()
        self.assertNotIn("99999999999", log)
        self.assertNotIn("Fulano Secreto", log)

    def test_arquivo_nao_encontrado(self):
        self.assertEqual(self.executar(), ProcessadorSolicitacoes.CODIGO_ERRO)
        self.assertIn("não encontrado", self.ler_log())
        self.assertIn("Processamento encerrado com erro", self.ler_log())
        self.assertFalse(self.saida.exists())

    def test_json_invalido(self):
        self.entrada.write_text("{ isto não é json", encoding="utf-8")
        self.assertEqual(self.executar(), ProcessadorSolicitacoes.CODIGO_ERRO)
        self.assertIn("JSON inválido", self.ler_log())
        self.assertFalse(self.saida.exists())

    def test_json_que_nao_e_lista(self):
        self.entrada.write_text('{"id": 1}', encoding="utf-8")
        self.assertEqual(self.executar(), ProcessadorSolicitacoes.CODIGO_ERRO)
        self.assertIn("Estrutura inesperada", self.ler_log())

    def test_erro_ao_gerar_csv(self):
        self.entrada.write_text("[]", encoding="utf-8")
        self.saida = Path(self._tmp.name) / "pasta_inexistente" / "aprovados.csv"
        self.assertEqual(self.executar(), ProcessadorSolicitacoes.CODIGO_ERRO)
        self.assertIn("Falha ao gerar o CSV", self.ler_log())

    def test_nao_foi_possivel_criar_log(self):
        self.log = Path(self._tmp.name) / "pasta_inexistente" / "processamento.log"
        self.entrada.write_text("[]", encoding="utf-8")
        self.assertEqual(self.executar(), ProcessadorSolicitacoes.CODIGO_ERRO)
        self.assertFalse(self.saida.exists())

    def test_erro_inesperado_e_registrado_no_log(self):
        self.entrada.write_text("[]", encoding="utf-8")
        configuracao = Configuracao(self.entrada, self.saida, self.log)
        processador = ProcessadorSolicitacoes(configuracao)

        def falhar(_registros):
            raise RuntimeError("falha simulada")

        processador.filtro.filtrar = falhar
        self.assertEqual(processador.executar(), ProcessadorSolicitacoes.CODIGO_ERRO)
        self.assertIn("Erro inesperado", self.ler_log())
        self.assertIn("falha simulada", self.ler_log())


if __name__ == "__main__":
    unittest.main()
