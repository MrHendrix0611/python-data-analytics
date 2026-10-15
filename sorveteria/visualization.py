import matplotlib.pyplot as plt
import seaborn as sns


def visualizar_vendas_diarias(dados_diarios):

    plt.figure(figsize=(10, 6))

    sns.lineplot(
        data=dados_diarios,
        x="data",
        y="quantidade_vendida",
        marker="o",
        color="royalblue",
        linewidth=2
    )

    plt.title(
        "Evolução das Vendas de Sorvete por Dia",
        fontsize=15
    )

    plt.xlabel("Data", fontsize=12)

    plt.ylabel(
        "Quantidade de Sorvetes Vendida",
        fontsize=12
    )

    plt.xticks(rotation=45)

    plt.grid(
        True,
        linestyle="--",
        alpha=0.5
    )

    plt.tight_layout()

    plt.show()


def visualizar_vendas_por_sabor(vendas_sabor):

    vendas_sabor.plot(kind="bar")

    plt.title("Vendas por Sabor")

    plt.xlabel("Sabor")

    plt.ylabel("Quantidade Vendida")

    plt.xticks(rotation=45)

    plt.tight_layout()

    plt.show()


def visualizar_temperatura_vs_vendas(dados_temperatura):

    plt.figure(figsize=(8, 6))

    plt.scatter(
        dados_temperatura["temperatura_c"],
        dados_temperatura["quantidade_vendida"],
        color="orange",
        alpha=0.7
    )

    plt.title(
        "Influência da Temperatura nas Vendas de Sorvete"
    )

    plt.xlabel("Temperatura Média (ºC)")

    plt.ylabel(
        "Quantidade Total Vendida (unidades)"
    )

    plt.grid(
        True,
        linestyle="--",
        alpha=0.5
    )

    plt.tight_layout()

    plt.show()


def visualizar_vendas_por_clima(dados_clima):

    plt.figure(figsize=(8, 6))

    sns.barplot(
        data=dados_clima,
        x="clima",
        y="quantidade_vendida",
        hue="clima",
        legend=False,
        palette="viridis"
    )

    plt.title(
        "Média de Vendas Diárias por Clima",
        fontsize=14
    )

    plt.xlabel(
        "Condição Climática",
        fontsize=12
    )

    plt.ylabel(
        "Média de Sorvetes Vendidos (unidades)",
        fontsize=12
    )

    plt.xticks(
        ticks=range(len(dados_clima)),
        labels=dados_clima["clima"].str.title()
    )

    plt.tight_layout()

    plt.show()


def visualizar_vendas_por_fim_de_semana(dados_fim_de_semana):

    plt.figure(figsize=(8, 6))

    sns.barplot(
        data=dados_fim_de_semana,
        x="fim_de_semana",
        y="quantidade_vendida",
        hue="fim_de_semana",
        legend=False,
        palette="Set2"
    )

    plt.title(
        "Média de Vendas: Dia Útil vs Fim de Semana",
        fontsize=14
    )

    plt.xlabel(
        "Período da Semana",
        fontsize=12
    )

    plt.ylabel(
        "Média de Sorvetes Vendidos",
        fontsize=12
    )

    plt.xticks(
        ticks=[0, 1],
        labels=["Dia de Semana", "Fim de Semana"]
    )

    plt.tight_layout()

    plt.show()


def visualizar_vendas_por_feriado(dados_feriado):

    plt.figure(figsize=(8, 6))

    sns.barplot(
        data=dados_feriado,
        x="feriado",
        y="quantidade_vendida",
        hue="feriado",
        legend=False,
        palette="pastel"
    )

    plt.title(
        "Impacto dos Feriados nas Vendas",
        fontsize=14
    )

    plt.xlabel(
        "Feriado",
        fontsize=12
    )

    plt.ylabel(
        "Média de Sorvetes Vendidos",
        fontsize=12
    )

    plt.xticks(
        ticks=[0, 1],
        labels=["Dia Normal", "Feriado"]
    )

    plt.tight_layout()

    plt.show()

