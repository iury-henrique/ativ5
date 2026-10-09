import argparse
import csv
import re
import sys
from dataclasses import dataclass
from datetime import datetime
from pathlib import Path


class FormatoInvalidoError(Exception):
    """Sinaliza que um campo não atende às regras de negócio do analisador."""


EMAIL_PATTERN = re.compile(r"^[\w.+-]+@[\w-]+(?:\.[\w-]+)+$", re.ASCII)
CPF_PATTERN = re.compile(r"^\d{3}\.\d{3}\.\d{3}-\d{2}$")
TELEFONE_PATTERN = re.compile(
    r"^(?:\(\d{2}\)\s?)?(?:9?\d{4})-\d{4}$"
)
DATA_PATTERN = re.compile(r"^\d{2}/\d{2}/\d{4}$")
COLUNAS_OBRIGATORIAS = ("email", "cpf", "telefone", "data")


@dataclass
class Registro:
    numero_linha: int
    dados: dict[str, str]
    erros: list[str]

    @property
    def valido(self) -> bool:
        return not self.erros


def validar_email(email: str) -> bool:
    return bool(EMAIL_PATTERN.fullmatch(email.strip()))


def validar_cpf(cpf: str) -> bool:
    cpf = cpf.strip()
    if not CPF_PATTERN.fullmatch(cpf):
        return False

    digitos = re.sub(r"\D", "", cpf)
    if digitos == digitos[0] * len(digitos):
        return False

    numeros = [int(digito) for digito in digitos]
    primeiro = sum(numeros[indice] * (10 - indice) for indice in range(9))
    primeiro = (primeiro * 10 % 11) % 10
    segundo = sum(numeros[indice] * (11 - indice) for indice in range(10))
    segundo = (segundo * 10 % 11) % 10
    return numeros[9:] == [primeiro, segundo]


def validar_telefone(telefone: str) -> bool:
    return bool(TELEFONE_PATTERN.fullmatch(telefone.strip()))


def validar_data(data: str) -> bool:
    data = data.strip()
    if not DATA_PATTERN.fullmatch(data):
        return False
    try:
        datetime.strptime(data, "%d/%m/%Y")
    except ValueError:
        return False
    return True


def validar_registro(dados: dict[str, str], numero_linha: int) -> Registro:
    validadores = {
        "email": validar_email,
        "cpf": validar_cpf,
        "telefone": validar_telefone,
        "data": validar_data,
    }
    erros = []

    for campo, validador in validadores.items():
        try:
            valor = dados[campo]
            if not validador(valor):
                raise FormatoInvalidoError(
                    f"formato ou valor inválido no campo '{campo}'"
                )
        except KeyError as erro:
            raise KeyError(f"Coluna obrigatória ausente: {erro.args[0]}") from erro
        except FormatoInvalidoError as erro:
            erros.append(str(erro))

    return Registro(numero_linha=numero_linha, dados=dados, erros=erros)


def gerar_relatorio(registros: list[Registro]) -> str:
    total = len(registros)
    validos = sum(registro.valido for registro in registros)
    invalidos = total - validos
    linhas = [
        "RELATÓRIO DA ANÁLISE DE DADOS",
        "=" * 30,
        f"Total de registros: {total}",
        f"Registros válidos: {validos}",
        f"Registros inválidos: {invalidos}",
        "",
        "REGISTROS VÁLIDOS",
    ]

    registros_validos = [registro for registro in registros if registro.valido]
    if registros_validos:
        for registro in registros_validos:
            linhas.append(
                f"Linha {registro.numero_linha}: "
                f"e-mail={registro.dados['email']}, "
                f"CPF={registro.dados['cpf']}, "
                f"telefone={registro.dados['telefone']}, "
                f"data={registro.dados['data']}"
            )
    else:
        linhas.append("Nenhum registro válido.")

    linhas.extend(("", "REGISTROS INVÁLIDOS"))
    registros_invalidos = [registro for registro in registros if not registro.valido]
    if registros_invalidos:
        for registro in registros_invalidos:
            linhas.append(
                f"Linha {registro.numero_linha}: "
                f"{'; '.join(registro.erros)}"
            )
    else:
        linhas.append("Nenhum registro inválido.")

    return "\n".join(linhas)


def analisar_arquivo(caminho: Path) -> list[Registro]:
    registros = []
    with caminho.open("r", encoding="utf-8", newline="") as arquivo:
        leitor = csv.DictReader(arquivo)
        if leitor.fieldnames is None:
            raise KeyError("Cabeçalho CSV ausente.")

        faltantes = set(COLUNAS_OBRIGATORIAS) - set(leitor.fieldnames)
        if faltantes:
            raise KeyError(
                f"Colunas obrigatórias ausentes: {', '.join(sorted(faltantes))}"
            )

        for numero_linha, dados in enumerate(leitor, start=2):
            try:
                registro = validar_registro(dados, numero_linha)
            except ValueError as erro:
                registro = Registro(
                    numero_linha,
                    dados,
                    [f"valor inválido: {erro}"],
                )
            registros.append(registro)
    return registros


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Valida e-mails, CPFs, telefones e datas em um arquivo CSV."
    )
    parser.add_argument(
        "arquivo",
        nargs="?",
        default="dados.csv",
        help="caminho do arquivo CSV (padrão: dados.csv)",
    )
    argumentos = parser.parse_args()
    caminho = Path(argumentos.arquivo)

    try:
        registros = analisar_arquivo(caminho)
    except FileNotFoundError:
        print(f"Erro: arquivo não encontrado: {caminho}", file=sys.stderr)
        return 1
    except KeyError as erro:
        print(f"Erro: {erro}", file=sys.stderr)
        return 1
    except (OSError, UnicodeDecodeError, csv.Error) as erro:
        print(f"Erro ao ler o arquivo '{caminho}': {erro}", file=sys.stderr)
        return 1
    else:
        print(gerar_relatorio(registros))
        return 0
    finally:
        print("Análise finalizada.")


if __name__ == "__main__":
    raise SystemExit(main())
