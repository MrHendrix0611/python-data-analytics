# Academia Analytics — XLSX

Análise financeira e operacional de uma academia a partir de planilha Excel com abas relacionadas de alunos, planos e pagamentos. Inclui validação, `merge`, agregações, indicadores, gráficos e testes automatizados.

## Ferramentas

Python, Pandas, OpenPyXL, Matplotlib e Pytest.

## Estrutura da base

- `data/raw/academia.xlsx`: abas **Alunos**, **Planos** e **Pagamentos**.
- `src/coleta.py`: leitura das abas.
- `src/limpar.py`: validação de chaves e valores.
- `src/tratar.py`: relacionamento das tabelas e cálculo de cobrança vencida.
- `src/analysis.py`: indicadores e evolução de alunos.
- `src/visualization.py`: gráficos.
- `src/report.py`: relatório textual.

## Indicadores

Receita recebida por competência, receita por plano, inadimplência financeira, ticket médio, matrículas, cancelamentos e alunos ativos. Data de referência definida no `main.py`.

## Executar

```powershell
py -m pip install -r requirements.txt
py main.py
py -m pytest -q
```

O arquivo Excel contém dados de estudo. Valores financeiros devem ser interpretados segundo as regras de cálculo documentadas no código.

## Visualização

![Receita mensal da academia](../assets/previews/academia.png)
