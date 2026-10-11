import logging
from pathlib import Path


class ConfiguradorLog:
    """Configura e encerra o log da execução.

    O log é gravado em arquivo (UTF-8, sobrescrito a cada execução) e também
    exibido no console, no formato ``data | nível | mensagem``.

    Atributos:
        nome_logger (str): Nome do logger usado pela aplicação.
        logger (logging.Logger): Logger configurado, disponível após ``configurar``.
    """

    FORMATO = "%(asctime)s | %(levelname)-7s | %(message)s"

    def __init__(self, nome_logger: str = "processamento"):
        """Inicializa o configurador.

        Args:
            nome_logger (str): Nome do logger. Padrão: ``processamento``.
        """
        self.nome_logger = nome_logger
        self.logger = logging.getLogger(nome_logger)

    def configurar(self, caminho_log: Path) -> logging.Logger:
        """Prepara o logger para gravar no arquivo e no console.

        Handlers de execuções anteriores são removidos para evitar mensagens duplicadas.

        Args:
            caminho_log (Path): Caminho do arquivo de log.

        Returns:
            logging.Logger: Logger pronto para uso.

        Levanta:
            OSError: Se o arquivo de log não puder ser criado.
        """
        self.encerrar()
        self.logger.setLevel(logging.INFO)
        formato = logging.Formatter(self.FORMATO)

        handler_arquivo = logging.FileHandler(caminho_log, mode="w", encoding="utf-8")
        handler_arquivo.setFormatter(formato)
        self.logger.addHandler(handler_arquivo)

        handler_console = logging.StreamHandler()
        handler_console.setFormatter(formato)
        self.logger.addHandler(handler_console)
        return self.logger

    def encerrar(self) -> None:
        """Fecha e remove todos os handlers do logger, liberando o arquivo de log."""
        for handler in list(self.logger.handlers):
            handler.close()
            self.logger.removeHandler(handler)
