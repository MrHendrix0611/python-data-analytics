"""Gráficos comerciais exportados para a pasta outputs/graficos."""

from pathlib import Path
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt


def gerar_graficos(indicadores: dict, destino: str | Path) -> list[Path]:
    destino = Path(destino)
    destino.mkdir(parents=True, exist_ok=True)
    mensal = indicadores["mensal"]
    categorias = indicadores["categorias"]
    produtos = indicadores["produtos"].head(10).iloc[::-1]
    status = indicadores["status"]
    estados = indicadores["estados"].head(8).iloc[::-1]
    saidas = []

    def salvar(fig, nome):
        caminho = destino / nome
        fig.savefig(caminho, dpi=160, bbox_inches="tight")
        plt.close(fig)
        saidas.append(caminho)

    fig, ax = plt.subplots(figsize=(10, 5))
    ax.plot(mensal["mes"], mensal["receita_reais"], marker="o", linewidth=2)
    ax.set(title="Receita líquida mensal", xlabel="Competência da venda", ylabel="Receita (R$)")
    ax.grid(axis="y", alpha=0.25)
    ax.tick_params(axis="x", rotation=40)
    salvar(fig, "01_receita_mensal.png")

    fig, ax = plt.subplots(figsize=(10, 5))
    categorias.sort_values("receita_reais").plot.barh(
        x="categoria", y="receita_reais", ax=ax, legend=False
    )
    ax.set(title="Receita por categoria", xlabel="Receita (R$)", ylabel="")
    salvar(fig, "02_categorias.png")

    fig, ax = plt.subplots(figsize=(10, 6))
    ax.barh(produtos["nome_produto"], produtos["receita_reais"])
    ax.set(title="10 produtos com maior receita", xlabel="Receita (R$)", ylabel="")
    salvar(fig, "03_top_produtos.png")

    fig, ax = plt.subplots(figsize=(8, 5))
    ax.bar(status["status"], status["quantidade"])
    ax.set(title="Distribuição de status dos pedidos", xlabel="Status", ylabel="Número de pedidos")
    salvar(fig, "04_status_pedidos.png")

    fig, ax = plt.subplots(figsize=(9, 5))
    ax.barh(estados["estado"], estados["receita_reais"])
    ax.set(title="Receita por estado (8 maiores)", xlabel="Receita (R$)", ylabel="")
    salvar(fig, "05_estados.png")

    return saidas
