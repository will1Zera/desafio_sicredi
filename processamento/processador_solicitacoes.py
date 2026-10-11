import sys

from processamento.configuracao import Configuracao
from processamento.configurador_log import ConfiguradorLog
from processamento.erros import ErroProcessamento
from processamento.filtro_solicitacoes import FiltroSolicitacoes
from processamento.gerador_csv import GeradorCsv
from processamento.leitor_json import LeitorJson
from processamento.validador_registro import ValidadorRegistro


class ProcessadorSolicitacoes:
    """Orquestra o fluxo completo: ler, filtrar, gerar o CSV e registrar o log.

    Erros que impedem a geração do arquivo são registrados no log e
    convertidos em código de saída, sem propagar exceções para quem chama.

    Atributos:
        configuracao (Configuracao): Parâmetros da execução.
        leitor (LeitorJson): Leitura do arquivo de entrada.
        filtro (FiltroSolicitacoes): Separação de aprovados e ignorados.
        gerador (GeradorCsv): Geração do CSV de saída.
        configurador_log (ConfiguradorLog): Configuração do log.
        logger (logging.Logger): Logger da execução, disponível após ``executar`` iniciar.
    """

    CODIGO_SUCESSO = 0
    CODIGO_ERRO = 1

    def __init__(self, configuracao: Configuracao):
        """Inicializa o processador e monta suas dependências.

        Args:
            configuracao (Configuracao): Parâmetros da execução.
        """
        self.configuracao = configuracao
        self.leitor = LeitorJson(configuracao.arquivo_entrada)
        self.filtro = FiltroSolicitacoes(
            ValidadorRegistro(
                configuracao.campos_obrigatorios, configuracao.status_aprovado
            )
        )
        self.gerador = GeradorCsv(
            configuracao.arquivo_saida,
            configuracao.colunas_csv,
            configuracao.separador_csv,
        )
        self.configurador_log = ConfiguradorLog()
        self.logger = self.configurador_log.logger

    def executar(self) -> int:
        """Executa o processamento do início ao fim.

        Returns:
            int: ``0`` se concluiu com sucesso; ``1`` se ocorreu erro que
            impediu a geração do arquivo.
        """
        try:
            self.logger = self.configurador_log.configurar(
                self.configuracao.arquivo_log
            )
        except OSError as erro:
            print(
                f"ERRO: não foi possível criar o arquivo de log: {erro}",
                file=sys.stderr,
            )
            return self.CODIGO_ERRO

        try:
            self.logger.info("Início do processamento")
            self._processar()
            self.logger.info("Processamento concluído com sucesso")
            return self.CODIGO_SUCESSO
        except ErroProcessamento as erro:
            self.logger.error("%s", erro)
            self.logger.error("Processamento encerrado com erro")
            return self.CODIGO_ERRO
        except Exception:  # rede de segurança: nada deve falhar sem registro no log
            self.logger.exception("Erro inesperado durante o processamento")
            return self.CODIGO_ERRO
        finally:
            self.configurador_log.encerrar()

    def _processar(self) -> None:
        """Executa as etapas de leitura, filtragem e geração, registrando o resumo no log.

        Levanta:
            ErroProcessamento: Se a leitura do JSON ou a geração do CSV falhar.
        """
        registros = self.leitor.ler()
        self.logger.info("Total de registros lidos: %d", len(registros))

        resultado = self.filtro.filtrar(registros)
        for ignorado in resultado.ignorados:
            self.logger.warning(
                "Registro ignorado (posição %d, id=%s): %s",
                ignorado.posicao,
                ignorado.identificador,
                ignorado.motivo,
            )

        self.gerador.gerar(resultado.aprovados)

        self.logger.info("Total de registros exportados: %d", len(resultado.aprovados))
        self.logger.info("Total de registros ignorados: %d", len(resultado.ignorados))
        self.logger.info("Arquivo gerado: %s", self.configuracao.arquivo_saida)
