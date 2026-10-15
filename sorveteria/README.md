# Análise de vendas de uma sorveteria — CSV

Estudo exploratório sobre volume de vendas por sabor, temperatura, condições climáticas, finais de semana e feriados. O objetivo é transformar um arquivo tabular em análises visuais que apoiem decisões comerciais.

## Ferramentas

Python, Pandas, Matplotlib e Seaborn.

## Base

- `sorveteria.csv`: registros de vendas e informações contextuais de cada período.
- `analysis.py`: agrupamentos, médias e consolidações.
- `visualization.py`: gráficos.
- `main.py`: menu interativo de análises.

## Questões investigadas

1. Quais sabores concentram mais vendas?
2. Como temperatura e clima se relacionam ao volume vendido?
3. Existem diferenças entre dias úteis, finais de semana e feriados?

## Executar

No diretório do projeto:

```powershell
py -m pip install -r requirements.txt
py main.py
```

O programa apresenta um menu interativo. A relação entre clima, temperatura e vendas é observacional e não estabelece causalidade por si só.

## Visualização

![Gráfico do estudo da sorveteria](../assets/previews/sorveteria.png)
