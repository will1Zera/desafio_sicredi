<img src="logo.png" align="center" style="border-radius: 10px" />

# Processamento de solicitações de cadastro

## Explicação da solução

O `main.py` lê o arquivo `solicitacoes.json`, filtra as solicitações aprovadas
com CPF preenchido e gera o arquivo `aprovados.csv` (colunas `id;nome;cpf`).
Toda a execução é registrada em `processamento.log`.

O código está organizado no pacote `processamento/`, com **uma classe por arquivo**:

| Arquivo | Classe | Responsabilidade |
|---|---|---|
| `configuracao.py` | `Configuracao` | Parâmetros da execução (caminhos, separador, colunas, status) |
| `leitor_json.py` | `LeitorJson` | Ler o JSON de entrada |
| `validador_registro.py` | `ValidadorRegistro` | Decidir se um registro é válido e aprovado (e o motivo, se não for) |
| `filtro_solicitacoes.py` | `FiltroSolicitacoes` | Separar aprovados e ignorados |
| `resultado_filtro.py` | `ResultadoFiltro` | Guardar o resultado da filtragem |
| `registro_ignorado.py` | `RegistroIgnorado` | Guardar posição, `id` e motivo de um registro ignorado |
| `gerador_csv.py` | `GeradorCsv` | Gerar o CSV |
| `configurador_log.py` | `ConfiguradorLog` | Configurar e encerrar o log |
| `processador_solicitacoes.py` | `ProcessadorSolicitacoes` | Orquestrar o fluxo e tratar erros |
| `erros.py` | `ErroProcessamento` | Exceção para falhas que impedem o processamento |

O `main.py` apenas monta a `Configuracao` a partir dos argumentos e chama
`ProcessadorSolicitacoes(configuracao).executar()`.

## Pré-requisitos

- Python 3.8 ou superior.
- Nenhuma biblioteca externa (só biblioteca padrão), por isso não há `requirements.txt`.

## Como executar

```bash
python main.py
```

Os arquivos `aprovados.csv` e `processamento.log` são criados na mesma pasta do `main.py`.
Opcionalmente, é possível informar outros caminhos:

```bash
python main.py --entrada outro.json --saida saida.csv --log execucao.log
```

Código de saída: `0` em caso de sucesso e `1` quando ocorre um erro que impede a geração do arquivo.

### Testes automatizados

```bash
python -m unittest -v
```

Os testes ficam na pasta `tests/`, com um arquivo por classe (`test_validador_registro.py`,
`test_filtro_solicitacoes.py`, `test_leitor_json.py`, `test_gerador_csv.py`,
`test_configurador_log.py`, `test_processador_solicitacoes.py`) e `test_main.py` para o ponto de entrada.

## Premissas adotadas

- Um registro é exportado somente se `status` for `APROVADO` **e** o CPF não for nulo nem vazio.
- A comparação do status ignora maiúsculas/minúsculas e espaços nas pontas (`" aprovado "` é aceito).
- CPF só contendo espaços é considerado vazio. O CPF deve ser texto; valores numéricos são rejeitados,
  pois perderiam zeros à esquerda. Os dígitos verificadores não são validados, conforme o enunciado.
- Registros sem algum dos campos `id`, `nome`, `cpf` ou `status`, ou sem `nome` preenchido, são ignorados.
- Itens do JSON que não são objetos (ex.: uma string solta na lista) são ignorados e registrados.
- O arquivo de entrada precisa conter uma lista JSON na raiz; qualquer outra estrutura é tratada como erro.
- Por envolver dado pessoal (LGPD), o log registra apenas o `id` e o motivo dos registros ignorados, nunca o CPF ou o nome.
- O log é sobrescrito a cada execução (um log por execução).

## Decisões relevantes

- **Separador do CSV: ponto e vírgula (`;`)**, pois é o padrão do Excel em português do Brasil e evita problemas com
  nomes que contenham vírgula. Valores que contenham `;` são protegidos automaticamente com aspas pelo módulo `csv`.
- CSV em UTF-8, sem BOM, com cabeçalho `id;nome;cpf`.
- O CSV é gravado primeiro em um arquivo temporário e renomeado ao final. Assim, uma falha no meio da escrita
  nunca deixa um `aprovados.csv` incompleto para as outras áreas.
- Registros inválidos geram apenas `WARNING` no log e não interrompem o processamento. Já arquivo ausente,
  JSON inválido e falha ao gerar o CSV geram `ERROR`, encerram a execução com código `1` e não produzem CSV.
- Uso apenas da biblioteca padrão (`json`, `csv`, `logging`, `argparse`, `pathlib`) para facilitar a execução.

## Tratamento de erros

| Situação | Comportamento |
|---|---|
| Arquivo não encontrado | `ERROR` no log e no console; código de saída 1 |
| JSON inválido (informa linha e coluna) | `ERROR` no log e no console; código de saída 1 |
| JSON que não é uma lista | `ERROR` no log; código de saída 1 |
| Registro sem campos necessários / inválido | `WARNING` com id e motivo; segue o processamento |
| Falha ao gerar o CSV (permissão, pasta inexistente etc.) | `ERROR`; arquivo temporário removido; código de saída 1 |
| Erro inesperado | Registrado no log com o traceback; código de saída 1 |

## Integração com processos (BPM)

Eu manteria a regra de negócio (`ValidadorRegistro`, `FiltroSolicitacoes`, `GeradorCsv`) independente da origem
dos dados (hoje `LeitorJson`) e a reaproveitaria como um serviço chamado pelo fluxo de BPM. No formulário, cada solicitação seria gravada
em uma base ou fila com o status `PENDENTE` e entraria na etapa de aprovação do processo. Quando o aprovador
decidisse, o BPM atualizaria o status para `APROVADO` ou `REPROVADO` e, ao final da etapa (ou em lote, em
horário agendado), acionaria o script/serviço, que passaria a ler os registros dessa base ou de um JSON
gerado pelo próprio BPM em vez de um arquivo fixo. O CSV seria publicado em uma pasta compartilhada ou
enviado por integração, e o log de cada execução seria guardado junto do identificador da instância do processo,
para rastreabilidade. Um mesmo registro não deve ser exportado duas vezes, então eu marcaria na base os já exportados.
Falhas retornariam ao BPM para alertar o responsável e permitir reprocessamento.

## Ferramentas de consulta ou IA utilizadas

- **Claude (Anthropic)**: Usado para estruturar a solução inicial e documentar este README.
- **Google**: Usado para consultar documentação do Python e consultar a melhor maneira de usar Docstrings.
