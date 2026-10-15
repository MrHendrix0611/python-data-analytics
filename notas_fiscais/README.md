# Análise de Documentos Fiscais (XML)

Projeto de análise de documentos fiscais **fictícios**, com extração de arquivos XML, validação de valores, tratamento de dados com Pandas e geração de relatórios e gráficos. Os arquivos possuem um **modelo XML didático próprio**, inspirado na organização hierárquica de documentos comerciais, **não seguem o leiaute oficial de NF-e e não têm validade fiscal**.

## Objetivo

Responder às seguintes perguntas:

1. Qual o faturamento por mês de emissão?
2. Quais produtos geraram maior faturamento?
3. Quais categorias e estados apresentam maior participação?
4. Qual o ticket médio por documento?
5. Como os valores tributários **simulados** estão distribuídos?
6. Qual a quantidade de documentos cancelados?

## Estrutura

```text
notas_fiscais/
├── data/
│   ├── raw/notas/             # 240 documentos XML fictícios
│   └── processed/             # tabelas geradas pelo pipeline
├── src/
│   ├── coleta.py              # leitura segura de XML, namespaces e XPath
│   ├── limpar.py              # validação de tipos, chaves e totais
│   ├── tratar.py              # join, datas e status
│   ├── analysis.py            # indicadores de negócio
│   ├── visualization.py       # cinco gráficos
│   └── report.py              # relatório consolidado
├── scripts/
│   ├── gerar_base.py          # regeneração reproduzível dos dados
│   └── exemplo_read_xml.py    # exemplo com pandas.read_xml()
├── tests/test_pipeline.py
├── outputs/
│   ├── graficos/
│   └── relatorios/
├── main.py
├── requirements.txt
└── README.md
```

## Execução no Windows (PowerShell)

```powershell
py -m venv .venv
.\.venv\Scripts\python.exe -m pip install -r requirements.txt
.\.venv\Scripts\python.exe main.py
.\.venv\Scripts\python.exe -m pytest -q
```

## Gerar novamente a base de dados

```powershell
.\.venv\Scripts\python.exe scripts/gerar_base.py
```

O script cria 240 arquivos XML na pasta `data/raw/notas`. Para reproduzir os resultados, a semente de aleatoriedade é fixa. Ao executar novamente, os arquivos `NF-2026-0001.xml` a `NF-2026-0240.xml` existentes serão sobrescritos. O gerador não apaga arquivos adicionais existentes na pasta.

## Estrutura de um arquivo XML

Cada nota possui um elemento `<doc:nota>` com os atributos `id` e `situacao`. Dentro dele ficam a data, o emitente, o destinatário e os itens. Cada `<doc:item>` possui atributos, informações do produto e elementos em outro namespace para tributos simulados.

Namespaces utilizados:
- `doc`: `urn:projeto:documentos-fiscais:v1`
- `trib`: `urn:projeto:tributos-simulados:v1`

`src/coleta.py` utiliza `defusedxml.ElementTree` para percorrer a árvore XML com XPath simples e extrair duas tabelas, uma para notas e outra para itens. As operações analíticas posteriores são parecidas com aquelas feitas em arquivos CSV e XLSX.

O script `scripts/exemplo_read_xml.py` mostra como o `pd.read_xml()` também pode ler elementos repetidos. Para XML aninhado, a extração explícita fornece maior controle sobre os relacionamentos e os tipos.

## Decisões sobre indicadores

- **Faturamento:** soma dos valores das notas com `situacao = emitida`. Notas canceladas são excluídas.
- **Ticket médio:** faturamento dividido pela quantidade de notas emitidas.
- **Produtos mais vendidos:** ordenação por faturamento; o relatório também mantém a quantidade de unidades.
- **Tributos:** valores gerados por alíquotas arbitrárias fixas, sem pretensão de corresponder a regras tributárias vigentes.
- **Período:** janeiro a setembro de 2026.

Os nomes, códigos, estados e documentos foram criados apenas para estudo; não há informações pessoais reais.

## Saídas

O programa salva `data/processed/notas.csv` e `data/processed/itens.csv`, cinco imagens em `outputs/graficos/` e `outputs/relatorios/relatorio.txt`.

## Testes

Os testes verificam leitura de namespaces e atributos, contagem de arquivos, integridade dos valores, exclusão dos cancelamentos, detecção de notas duplicadas, detecção de valores divergentes e geração de gráficos.
