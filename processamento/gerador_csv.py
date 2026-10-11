import csv
import os
from pathlib import Path
from typing import Dict, List, Tuple

from processamento.erros import ErroProcessamento


class GeradorCsv:
    """Gera o arquivo CSV com as solicitações aprovadas.

    O arquivo é escrito em UTF-8, com cabeçalho. A escrita é feita primeiro em
    um arquivo temporário, que só substitui o definitivo quando tudo termina
    com sucesso, evitando deixar um CSV incompleto em caso de falha.

    Atributos:
        caminho (Path): Caminho do CSV de saída.
        colunas (Tuple[str, ...]): Nomes das colunas, na ordem do arquivo.
        separador (str): Separador de colunas.
    """

    def __init__(self, caminho: Path, colunas: Tuple[str, ...], separador: str = ";"):
        """Inicializa o gerador.

        Args:
            caminho (Path): Caminho do CSV de saída.
            colunas (Tuple[str, ...]): Nomes das colunas do cabeçalho.
            separador (str): Separador de colunas. Padrão: ``;``.
        """
        self.caminho = Path(caminho)
        self.colunas = colunas
        self.separador = separador

    def gerar(self, registros: List[Dict[str, str]]) -> None:
        """Grava os registros no arquivo CSV.

        Args:
            registros (List[Dict[str, str]]): Registros a exportar; cada um
                deve conter as chaves definidas em ``colunas``.

        Levanta:
            ErroProcessamento: Se houver falha de escrita (permissão, pasta
                inexistente etc.) ou erro na formatação do CSV. O arquivo
                temporário é removido nesse caso.
        """
        temporario = self.caminho.with_name(self.caminho.name + ".tmp")
        try:
            with open(temporario, "w", encoding="utf-8", newline="") as arquivo:
                escritor = csv.DictWriter(
                    arquivo, fieldnames=self.colunas, delimiter=self.separador
                )
                escritor.writeheader()
                escritor.writerows(registros)
            os.replace(temporario, self.caminho)
        except (OSError, csv.Error, ValueError) as erro:
            self._remover_temporario(temporario)
            raise ErroProcessamento(f"Falha ao gerar o CSV {self.caminho}: {erro}")

    @staticmethod
    def _remover_temporario(temporario: Path) -> None:
        """Apaga o arquivo temporário, ignorando falhas na remoção.

        Args:
            temporario (Path): Caminho do arquivo temporário.
        """
        try:
            temporario.unlink()
        except OSError:
            pass
