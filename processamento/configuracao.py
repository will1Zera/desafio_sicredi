from dataclasses import dataclass
from pathlib import Path
from typing import Tuple


@dataclass(frozen=True)
class Configuracao:
    """Reúne todos os parâmetros de uma execução do processamento.

    A classe é imutável: depois de criada, os valores não podem ser alterados,
    o que evita que uma etapa modifique a configuração usada por outra.

    Atributos:
        arquivo_entrada (Path): Caminho do JSON com as solicitações.
        arquivo_saida (Path): Caminho do CSV que será gerado.
        arquivo_log (Path): Caminho do arquivo de log da execução.
        separador_csv (str): Separador de colunas do CSV. Padrão: ``;``.
        colunas_csv (Tuple[str, ...]): Colunas exportadas, na ordem do CSV.
        campos_obrigatorios (Tuple[str, ...]): Campos que todo registro de
            entrada deve possuir.
        status_aprovado (str): Valor de ``status`` que indica solicitação
            aprovada.
    """

    arquivo_entrada: Path
    arquivo_saida: Path
    arquivo_log: Path
    separador_csv: str = ";"
    colunas_csv: Tuple[str, ...] = ("id", "nome", "cpf")
    campos_obrigatorios: Tuple[str, ...] = ("id", "nome", "cpf", "status")
    status_aprovado: str = "APROVADO"
