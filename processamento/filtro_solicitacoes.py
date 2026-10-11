from typing import Any, List

from processamento.registro_ignorado import RegistroIgnorado
from processamento.resultado_filtro import ResultadoFiltro
from processamento.validador_registro import ValidadorRegistro


class FiltroSolicitacoes:
    """Separa os registros aprovados dos ignorados.

    Um registro com problema nunca interrompe a filtragem dos demais: ele é
    apenas colocado na lista de ignorados, junto com o motivo.

    Atributos:
        validador (ValidadorRegistro): Responsável por decidir se cada
            registro é válido e aprovado.
    """

    def __init__(self, validador: ValidadorRegistro):
        """Inicializa o filtro.

        Args:
            validador (ValidadorRegistro): Validador aplicado a cada registro.
        """
        self.validador = validador

    def filtrar(self, registros: List[Any]) -> ResultadoFiltro:
        """Percorre os registros e classifica cada um como aprovado ou ignorado.

        Os registros aprovados são normalizados: ``nome`` e ``cpf`` perdem os
        espaços das pontas e só as chaves ``id``, ``nome`` e ``cpf`` são mantidas.

        Args:
            registros (List[Any]): Itens lidos do arquivo de entrada.

        Returns:
            ResultadoFiltro: Registros aprovados e registros ignorados (com
            posição, ``id`` e motivo).
        """
        aprovados = []
        ignorados = []
        for posicao, registro in enumerate(registros, start=1):
            motivo = self.validador.validar(registro)
            if motivo is None:
                aprovados.append(self._normalizar(registro))
            else:
                ignorados.append(
                    RegistroIgnorado(posicao, self._obter_id(registro), motivo)
                )
        return ResultadoFiltro(aprovados=aprovados, ignorados=ignorados)

    @staticmethod
    def _normalizar(registro: dict) -> dict:
        """Monta o registro de saída a partir de um registro válido.

        Args:
            registro (dict): Registro já validado.

        Returns:
            dict: Dicionário com ``id``, ``nome`` e ``cpf`` (textos sem espaços nas pontas).
        """
        return {
            "id": registro["id"],
            "nome": registro["nome"].strip(),
            "cpf": registro["cpf"].strip(),
        }

    @staticmethod
    def _obter_id(registro: Any) -> Any:
        """Obtém o ``id`` de um registro, se existir, para uso no log.

        Args:
            registro (Any): Item lido do JSON.

        Returns:
            Any: Valor de ``id`` ou ``None`` se o registro não for um
            dicionário ou não tiver esse campo.
        """
        return registro.get("id") if isinstance(registro, dict) else None
