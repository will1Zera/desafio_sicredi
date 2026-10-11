import unittest

from processamento.filtro_solicitacoes import FiltroSolicitacoes
from processamento.registro_ignorado import RegistroIgnorado
from processamento.validador_registro import ValidadorRegistro


class FiltroSolicitacoesTest(unittest.TestCase):
    """Testa a separação entre registros aprovados e ignorados."""

    def setUp(self):
        validador = ValidadorRegistro(("id", "nome", "cpf", "status"), "APROVADO")
        self.filtro = FiltroSolicitacoes(validador)

    def test_lista_vazia(self):
        resultado = self.filtro.filtrar([])
        self.assertEqual(resultado.aprovados, [])
        self.assertEqual(resultado.ignorados, [])

    def test_separa_aprovados_e_ignorados_com_motivo(self):
        registros = [
            {"id": 1, "nome": "Maria", "cpf": "111", "status": "APROVADO"},
            {"id": 2, "nome": "Pedro", "cpf": "222", "status": "PENDENTE"},
            {"id": 3, "nome": "Ana", "cpf": "", "status": "APROVADO"},
            "lixo",
        ]
        resultado = self.filtro.filtrar(registros)

        self.assertEqual(
            resultado.aprovados, [{"id": 1, "nome": "Maria", "cpf": "111"}]
        )
        self.assertEqual(
            [(i.posicao, i.identificador) for i in resultado.ignorados],
            [(2, 2), (3, 3), (4, None)],
        )
        self.assertIsInstance(resultado.ignorados[0], RegistroIgnorado)
        self.assertIn("status", resultado.ignorados[0].motivo)
        self.assertEqual(resultado.ignorados[1].motivo, "cpf vazio")

    def test_normaliza_espacos_e_descarta_campos_extras(self):
        registros = [
            {"id": 1, "nome": "  Maria  ", "cpf": " 111 ", "status": "APROVADO", "extra": "x"}
        ]
        resultado = self.filtro.filtrar(registros)
        self.assertEqual(resultado.aprovados, [{"id": 1, "nome": "Maria", "cpf": "111"}])

    def test_registro_invalido_nao_interrompe_os_demais(self):
        registros = [
            None,
            {"id": 2, "nome": "Ana", "cpf": "222", "status": "APROVADO"},
        ]
        resultado = self.filtro.filtrar(registros)
        self.assertEqual(len(resultado.aprovados), 1)
        self.assertEqual(len(resultado.ignorados), 1)

    def test_registro_sem_id_e_ignorado_com_id_none(self):
        resultado = self.filtro.filtrar([{"nome": "Ana", "cpf": "1", "status": "APROVADO"}])
        self.assertIsNone(resultado.ignorados[0].identificador)
        self.assertIn("id", resultado.ignorados[0].motivo)


if __name__ == "__main__":
    unittest.main()
