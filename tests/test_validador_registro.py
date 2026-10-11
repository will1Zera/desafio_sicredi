import unittest

from processamento.validador_registro import ValidadorRegistro


class ValidadorRegistroTest(unittest.TestCase):
    """Testa as regras de validação de um registro."""

    def setUp(self):
        self.validador = ValidadorRegistro(
            campos_obrigatorios=("id", "nome", "cpf", "status"),
            status_aprovado="APROVADO",
        )

    @staticmethod
    def registro(**alteracoes):
        base = {"id": 1, "nome": "Maria", "cpf": "123", "status": "APROVADO"}
        base.update(alteracoes)
        return base

    def test_registro_valido_retorna_none(self):
        self.assertIsNone(self.validador.validar(self.registro()))

    def test_status_ignora_caixa_e_espacos(self):
        self.assertIsNone(self.validador.validar(self.registro(status=" aprovado ")))

    def test_status_pendente_e_reprovado(self):
        for status in ("PENDENTE", "REPROVADO"):
            with self.subTest(status=status):
                self.assertIn("status", self.validador.validar(self.registro(status=status)))

    def test_status_com_tipo_invalido(self):
        self.assertIn("status", self.validador.validar(self.registro(status=1)))

    def test_cpf_nulo(self):
        self.assertEqual(self.validador.validar(self.registro(cpf=None)), "cpf nulo")

    def test_cpf_vazio_e_somente_espacos(self):
        for cpf in ("", "   "):
            with self.subTest(cpf=cpf):
                self.assertEqual(self.validador.validar(self.registro(cpf=cpf)), "cpf vazio")

    def test_cpf_com_tipo_invalido(self):
        self.assertIn("tipo", self.validador.validar(self.registro(cpf=12345678900)))

    def test_nome_vazio_ou_nulo(self):
        for nome in ("", None):
            with self.subTest(nome=nome):
                self.assertEqual(
                    self.validador.validar(self.registro(nome=nome)), "nome nulo ou vazio"
                )

    def test_campo_ausente(self):
        registro = self.registro()
        del registro["cpf"]
        self.assertEqual(self.validador.validar(registro), "campos ausentes: cpf")

    def test_varios_campos_ausentes(self):
        self.assertEqual(
            self.validador.validar({"id": 1}), "campos ausentes: nome, cpf, status"
        )

    def test_registro_que_nao_e_objeto(self):
        for item in ("texto", 10, None, [1, 2]):
            with self.subTest(item=item):
                self.assertIn("não é um objeto", self.validador.validar(item))


if __name__ == "__main__":
    unittest.main()
