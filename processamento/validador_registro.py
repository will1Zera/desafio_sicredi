from typing import Any, Optional, Tuple


class ValidadorRegistro:
    """Valida se um registro pode ser exportado para o CSV.

    Um registro é aceito somente quando é um objeto JSON com todos os campos
    obrigatórios, ``status`` igual ao valor de aprovação (sem diferenciar
    maiúsculas de minúsculas), CPF preenchido e nome preenchido. Os dígitos
    verificadores do CPF não são conferidos.

    Atributos:
        campos_obrigatorios (Tuple[str, ...]): Campos exigidos em cada registro.
        status_aprovado (str): Valor de ``status`` que indica aprovação.
    """

    def __init__(self, campos_obrigatorios: Tuple[str, ...], status_aprovado: str):
        """Inicializa o validador.

        Args:
            campos_obrigatorios (Tuple[str, ...]): Campos que o registro deve possuir.
            status_aprovado (str): Valor de ``status`` considerado aprovado.
        """
        self.campos_obrigatorios = campos_obrigatorios
        self.status_aprovado = status_aprovado

    def validar(self, registro: Any) -> Optional[str]:
        """Verifica se o registro é válido e está aprovado.

        As regras são avaliadas em ordem e a primeira que falhar define o motivo.

        Args:
            registro (Any): Item lido do JSON, normalmente um dicionário.

        Returns:
            Optional[str]: ``None`` se o registro for válido e aprovado;
            caso contrário, o motivo pelo qual deve ser ignorado.
        """
        if not isinstance(registro, dict):
            return f"registro não é um objeto JSON (tipo {type(registro).__name__})"

        ausentes = [c for c in self.campos_obrigatorios if c not in registro]
        if ausentes:
            return f"campos ausentes: {', '.join(ausentes)}"

        return (
            self._validar_status(registro["status"])
            or self._validar_cpf(registro["cpf"])
            or self._validar_nome(registro["nome"])
        )

    def _validar_status(self, status: Any) -> Optional[str]:
        """Confere se o status corresponde ao valor de aprovação.

        Args:
            status (Any): Valor do campo ``status`` do registro.

        Returns:
            Optional[str]: ``None`` se estiver aprovado; senão, o motivo.
        """
        if not isinstance(status, str) or status.strip().upper() != self.status_aprovado:
            return f"status diferente de {self.status_aprovado} (valor: {status!r})"
        return None

    @staticmethod
    def _validar_cpf(cpf: Any) -> Optional[str]:
        """Confere se o CPF é um texto não nulo e não vazio.

        Valores numéricos são rejeitados porque perderiam zeros à esquerda.

        Args:
            cpf (Any): Valor do campo ``cpf`` do registro.

        Returns:
            Optional[str]: ``None`` se o CPF for aceito; senão, o motivo.
        """
        if cpf is None:
            return "cpf nulo"
        if not isinstance(cpf, str):
            return f"cpf com tipo inválido ({type(cpf).__name__})"
        if not cpf.strip():
            return "cpf vazio"
        return None

    @staticmethod
    def _validar_nome(nome: Any) -> Optional[str]:
        """Confere se o nome é um texto não nulo e não vazio.

        Args:
            nome (Any): Valor do campo ``nome`` do registro.

        Returns:
            Optional[str]: ``None`` se o nome for aceito; senão, o motivo.
        """
        if not isinstance(nome, str) or not nome.strip():
            return "nome nulo ou vazio"
        return None
