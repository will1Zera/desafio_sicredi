from dataclasses import dataclass
from typing import Dict, List

from processamento.registro_ignorado import RegistroIgnorado


@dataclass(frozen=True)
class ResultadoFiltro:
    """Resultado da filtragem das solicitações.

    Atributos:
        aprovados (List[Dict[str, str]]): Registros válidos e aprovados, já
            normalizados (sem espaços nas pontas) e prontos para o CSV.
        ignorados (List[RegistroIgnorado]): Registros descartados, cada um
            com sua posição, identificador e motivo.
    """

    aprovados: List[Dict[str, str]]
    ignorados: List[RegistroIgnorado]
