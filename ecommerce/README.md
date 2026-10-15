# Inteligência Comercial para E-commerce — SQLite + Pandas

Análise de desempenho comercial de uma loja virtual a partir de um banco de dados relacional SQLite. O projeto cobre modelagem de dados, extração com SQL, validação, transformação com Pandas, indicadores de negócio, visualização e testes automatizados.

A base é **fictícia**, criada exclusivamente para estudo. Não contém informações de clientes ou vendas reais.

## Objetivos

- Identificar faturamento, descontos e lucro bruto estimado.
- Avaliar ticket médio, volume de pedidos e receita por mês.
- Descobrir produtos, categorias e estados com maior faturamento.
- Calcular recompra de clientes e taxa de cancelamento.
- Exercitar `INNER JOIN`, `LEFT JOIN`, `GROUP BY`, `COUNT(DISTINCT ...)`, CTE, integridade referencial e consultas parametrizadas.

## Tecnologias

Python 3.10+, SQLite (`sqlite3`, biblioteca padrão), Pandas, Matplotlib e Pytest.

## Estrutura

```text
ecommerce/
├── data/
│   ├── raw/ecommerce.db                # Dados sintéticos já incluídos
│   └── processed/                     # Tabelas de indicadores exportadas como CSV
├── docs/
│   ├── modelo_dados.md                 # Modelo e definições dos indicadores
│   └── consultas.sql                   # Exercícios SQL independentes
├── outputs/
│   ├── graficos/                       # 5 gráficos PNG
│   └── relatorios/                     # Relatório textual
├── scripts/
│   ├── gerar_base.py                   # Gerador reproduzível (seed fixa)
│   └── inspecionar_banco.py            # Estrutura e volume das tabelas
├── src/
│   ├── coleta.py                       # Conexão e consultas SQL parametrizadas
│   ├── limpar.py                       # Validação de qualidade
│   ├── tratar.py                       # Datas e valores monetários em centavos
│   ├── analysis.py                     # Indicadores com Pandas
│   ├── visualization.py                # Gráficos
│   └── report.py                       # Relatórios e exportações
├── tests/test_pipeline.py             # Testes automatizados
├── main.py                             # Orquestração
├── requirements.txt
└── .gitignore
```

## Instalação e execução (Windows / PowerShell)

Na pasta raiz:

```powershell
py -m venv .venv
.\.venv\Scripts\python.exe -m pip install -r requirements.txt
.\.venv\Scripts\python.exe main.py
```

No Linux/macOS, substitua o Python por `python3` e use `.venv/bin/python`.

### Verificar o banco

```powershell
.\.venv\Scripts\python.exe scripts/inspecionar_banco.py
```

### Recriar dados sintéticos

O banco `data/raw/ecommerce.db` já acompanha o projeto. Caso deseje regenerá-lo, **atenção: `--force` sobrescreve o arquivo existente**:

```powershell
.\.venv\Scripts\python.exe scripts/gerar_base.py --force
```

### Executar testes

```powershell
.\.venv\Scripts\python.exe -m pytest -q
```

## Diferenças em relação a CSV, Excel, JSON e XML

- O SQLite mantém dados em **tabelas com relacionamentos**, em vez de um arquivo plano ou uma estrutura hierárquica.
- A biblioteca padrão `sqlite3` permite executar consultas SQL e trabalhar com um banco local sem servidor.
- `pd.read_sql_query()` produz DataFrames a partir do resultado de consultas SQL.
- `JOIN` relaciona pedidos, clientes, itens e produtos **no próprio banco**, antes da análise.
- `WHERE ... BETWEEN ? AND ?` filtra um intervalo por meio de **parâmetros**, sem concatenar SQL.
- `COUNT(DISTINCT id_pedido)` evita contar um pedido múltiplas vezes devido aos seus itens.
- Indicadores financeiros acumulam valores em centavos inteiros antes da conversão para reais.

## Como a análise funciona

1. Abre `data/raw/ecommerce.db` e verifica integridade.
2. Carrega as quatro tabelas e confere chaves e regras de negócio.
3. Consulta somente itens de pedidos **pagos ou entregues** entre 01/01/2026 e 30/09/2026.
4. Calcula valores brutos, descontos, receita de produtos e lucro bruto estimado.
5. Agrupa os resultados por mês, categoria, produto, estado e cliente.
6. Exporta tabelas e relatório, além de cinco gráficos.

**Escopo financeiro:** não inclui tributos, frete, devoluções, custos logísticos ou despesas operacionais. O lucro bruto é uma estimativa baseada no custo atual cadastrado dos produtos. Veja `docs/modelo_dados.md`.

## Aprendizados e próximos experimentos

- Execute `docs/consultas.sql` em um cliente SQLite para comparar agregações em SQL com as do Pandas.
- Troque `INICIO` e `FIM` no `main.py` para comparar trimestres.
- Adicione análise de sazonalidade, vendas recorrentes e clientes sem compra.
- Adicione uma tabela de pagamentos para distinguir data da compra e data do recebimento.
- Em um sistema real, registre custo histórico por item e utilize migrações para evoluir o banco.
