import json
from pathlib import Path
from typing import Any, List

from processamento.erros import ErroProcessamento


class LeitorJson:
    """Lê o arquivo JSON de entrada e devolve a lista de registros.

    Atributos:
        caminho (Path): Caminho do arquivo JSON a ser lido.
    """

    def __init__(self, caminho: Path):
        """Inicializa o leitor.

        Args:
            caminho (Path): Caminho do arquivo JSON de entrada.
        """
        self.caminho = Path(caminho)

    def ler(self) -> List[Any]:
        """Carrega todos os registros do arquivo JSON.

        O conteúdo de cada registro não é validado aqui; apenas se garante
        que o arquivo existe, é um JSON válido e tem uma lista na raiz.

        Returns:
            List[Any]: Lista com os itens encontrados no arquivo, na ordem original.

        Levanta:
            ErroProcessamento: Se o arquivo não for encontrado, não puder ser
                lido, não for um JSON válido ou não tiver uma lista na raiz.
        """
        try:
            with open(self.caminho, "r", encoding="utf-8") as arquivo:
                dados = json.load(arquivo)
        except FileNotFoundError:
            raise ErroProcessamento(
                f"Arquivo de entrada não encontrado: {self.caminho}"
            )
        except json.JSONDecodeError as erro:
            raise ErroProcessamento(
                f"JSON inválido em {self.caminho.name} "
                f"(linha {erro.lineno}, coluna {erro.colno}): {erro.msg}"
            )
        except (OSError, UnicodeDecodeError) as erro:
            raise ErroProcessamento(f"Não foi possível ler {self.caminho}: {erro}")

        if not isinstance(dados, list):
            raise ErroProcessamento(
                "Estrutura inesperada: esperada uma lista de registros, "
                f"recebido {type(dados).__name__}"
            )
        return dados
