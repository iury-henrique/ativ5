# Sistema de Análise de Dados

Programa em Python que lê um CSV e valida e-mail, CPF, telefone e data. O
relatório no terminal apresenta estatísticas e detalha os registros válidos e
inválidos.

## Requisitos

- Python 3.10 ou superior
- Não há dependências externas

## Como executar

Na pasta do projeto, execute:

```powershell
python analisador.py
```

Sem argumentos, o programa lê `dados.csv`. Para indicar outro arquivo:

```powershell
python analisador.py caminho\para\entrada.csv
```

O CSV deve usar cabeçalho e conter as colunas `email`, `cpf`, `telefone` e
`data`. A data deve estar no formato `DD/MM/AAAA`.

## Exemplo de entrada

```csv
email,cpf,telefone,data
ana.silva@example.com,529.982.247-25,(11) 91234-5678,15/03/2024
contato+loja@example.com,111.111.111-11,123,31/02/2024
```

## Exemplo de saída

```text
RELATÓRIO DA ANÁLISE DE DADOS
==============================
Total de registros: 2
Registros válidos: 1
Registros inválidos: 1

REGISTROS VÁLIDOS
Linha 2: e-mail=ana.silva@example.com, CPF=529.982.247-25, telefone=(11) 91234-5678, data=15/03/2024

REGISTROS INVÁLIDOS
Linha 3: formato ou valor inválido no campo 'cpf'; formato ou valor inválido no campo 'telefone'; formato ou valor inválido no campo 'data'
Análise finalizada.
```

## Validações e exceções

- **E-mail:** expressão regular ancorada com `^` e `$`, aceitando letras,
  números, `_`, ponto, `+` e `-`, além de domínio com pelo menos uma extensão.
- **CPF:** a regex verifica `000.000.000-00` e os dígitos verificadores também
  são calculados, rejeitando sequências repetidas.
- **Telefone:** a regex aceita telefone de oito ou nove dígitos com hífen e DDD
  opcional no formato `(DD)`, com espaço opcional.
- **Data:** a regex exige `DD/MM/AAAA` e `datetime.strptime` confirma que a data
  existe no calendário.
- **`FormatoInvalidoError`:** exceção personalizada para sinalizar campos que
  não satisfazem as regras de negócio; os erros são apresentados por registro
  no relatório.
- **`FileNotFoundError`:** informa quando o caminho de entrada não existe.
- **`ValueError`:** `datetime.strptime` rejeita datas impossíveis (por exemplo,
  `31/02/2024`); a exceção é capturada pela validação e o campo é marcado como
  inválido sem interromper a análise dos demais registros.
- **`KeyError`:** sinaliza cabeçalho ausente ou coluna obrigatória faltante.
- **`try/except/else/finally`:** a execução principal trata falhas de leitura,
  imprime o relatório no `else` após uma leitura bem-sucedida e informa o
  encerramento no `finally`.

O arquivo é aberto com `with open` (via `Path.open`) e `encoding="utf-8"` para
fechamento automático e suporte a acentos. As expressões regulares são
declaradas como raw strings.

## Testes

Execute a suíte padrão, sem instalar pacotes:

```powershell
python -m unittest -v
```
