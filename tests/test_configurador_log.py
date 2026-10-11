import tempfile
import unittest
from pathlib import Path

from processamento.configurador_log import ConfiguradorLog


class ConfiguradorLogTest(unittest.TestCase):
    """Testa a configuração e o encerramento do log."""

    def setUp(self):
        self._tmp = tempfile.TemporaryDirectory()
        self.addCleanup(self._tmp.cleanup)
        self.caminho = Path(self._tmp.name) / "processamento.log"
        self.configurador = ConfiguradorLog("teste_configurador_log")
        self.addCleanup(self.configurador.encerrar)

    def test_grava_mensagem_no_arquivo(self):
        logger = self.configurador.configurar(self.caminho)
        logger.info("mensagem de teste")
        self.configurador.encerrar()
        conteudo = self.caminho.read_text(encoding="utf-8")
        self.assertIn("INFO", conteudo)
        self.assertIn("mensagem de teste", conteudo)

    def test_configurar_duas_vezes_nao_duplica_handlers(self):
        self.configurador.configurar(self.caminho)
        logger = self.configurador.configurar(self.caminho)
        self.assertEqual(len(logger.handlers), 2)

    def test_encerrar_remove_handlers(self):
        logger = self.configurador.configurar(self.caminho)
        self.configurador.encerrar()
        self.assertEqual(logger.handlers, [])

    def test_sobrescreve_log_anterior(self):
        logger = self.configurador.configurar(self.caminho)
        logger.info("primeira execução")
        self.configurador.encerrar()
        logger = self.configurador.configurar(self.caminho)
        logger.info("segunda execução")
        self.configurador.encerrar()
        conteudo = self.caminho.read_text(encoding="utf-8")
        self.assertNotIn("primeira execução", conteudo)
        self.assertIn("segunda execução", conteudo)

    def test_pasta_inexistente_levanta_oserror(self):
        with self.assertRaises(OSError):
            self.configurador.configurar(Path(self._tmp.name) / "inexistente" / "x.log")


if __name__ == "__main__":
    unittest.main()
