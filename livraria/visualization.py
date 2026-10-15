import matplotlib.pyplot as plt

import matplotlib.pyplot as plt

def gerar_graficos(df):
    plt.style.use("ggplot")
    
    # Gráfico 1: Lucro por Categoria
    plt.figure(figsize=(10, 5))
    df.groupby("categoria")["lucro_total"].sum().sort_values().plot(kind="barh", color="steelblue")
    plt.title("Lucro Absoluto por Categoria")
    plt.xlabel("Lucro (R$)")
    plt.ylabel("Categoria")
    plt.tight_layout()
    plt.show()

    # Gráfico 2: Dispersão Nota Média x Vendas
    plt.figure(figsize=(8, 5))
    plt.scatter(df["avaliacao_media"], df["unidades_vendidas_mes"], alpha=0.7, color="darkorange")
    plt.title("Avaliação Média vs Unidades Vendidas")
    plt.xlabel("Nota Média")
    plt.ylabel("Unidades Vendidas (Mês)")
    plt.grid(True)
    plt.tight_layout()
    plt.show()