from dataclasses import dataclass
from typing import Any


@dataclass(frozen=True)
class RegistroIgnorado:
    """Representa um registro que não foi exportado, com o motivo.

    Atributos:
        posicao (int): Posição do registro no arquivo de entrada, começando em 1.
        identificador (Any): Valor do campo ``id`` do registro, ou ``None``
            quando o registro não possui ``id`` ou não é um objeto JSON.
        motivo (str): Descrição legível do motivo pelo qual foi ignorado.
    """

    posicao: int
    identificador: Any
    motivo: str
