import unittest

from analisador import (
    FormatoInvalidoError,
    gerar_relatorio,
    validar_cpf,
    validar_data,
    validar_email,
    validar_registro,
    validar_telefone,
)


class ValidacaoTestes(unittest.TestCase):
    def test_validar_email(self):
        self.assertTrue(validar_email("ana.silva@example.com"))
        self.assertFalse(validar_email("ana@"))

    def test_validar_cpf_com_digitos_verificadores(self):
        self.assertTrue(validar_cpf("529.982.247-25"))
        self.assertFalse(validar_cpf("111.111.111-11"))
        self.assertFalse(validar_cpf("52998224725"))

    def test_validar_telefone(self):
        self.assertTrue(validar_telefone("(11) 91234-5678"))
        self.assertTrue(validar_telefone("3234-5678"))
        self.assertFalse(validar_telefone("123"))

    def test_validar_data_real(self):
        self.assertTrue(validar_data("29/02/2024"))
        self.assertFalse(validar_data("31/02/2024"))
        self.assertFalse(validar_data("2024-02-29"))

    def test_validar_registro_coleta_erros(self):
        registro = validar_registro(
            {
                "email": "invalido",
                "cpf": "111.111.111-11",
                "telefone": "123",
                "data": "31/02/2024",
            },
            2,
        )
        self.assertFalse(registro.valido)
        self.assertEqual(len(registro.erros), 4)

    def test_coluna_ausente_gera_key_error(self):
        with self.assertRaises(KeyError):
            validar_registro({"email": "a@b.com"}, 2)

    def test_relatorio_exibe_estatisticas(self):
        registro = validar_registro(
            {
                "email": "ana@example.com",
                "cpf": "529.982.247-25",
                "telefone": "(11) 91234-5678",
                "data": "15/03/2024",
            },
            2,
        )
        relatorio = gerar_relatorio([registro])
        self.assertIn("Total de registros: 1", relatorio)
        self.assertIn("Registros válidos: 1", relatorio)
        self.assertIn("REGISTROS VÁLIDOS", relatorio)

    def test_excecao_personalizada_herda_exception(self):
        self.assertTrue(issubclass(FormatoInvalidoError, Exception))


if __name__ == "__main__":
    unittest.main()
