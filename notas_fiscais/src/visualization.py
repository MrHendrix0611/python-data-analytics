"""Gráficos estáticos do projeto de documentos fiscais."""

from pathlib import Path

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt


def _salvar(fig, pasta: Path, nome: str) -> None:
    fig.tight_layout()
    fig.savefig(pasta / nome, dpi=150)
    plt.close(fig)


def gerar_graficos(indicadores: dict, destino: str | Path) -> None:
    pasta = Path(destino)
    pasta.mkdir(parents=True, exist_ok=True)

    mensal = indicadores["mensal"]
    fig, ax = plt.subplots(figsize=(10, 5))
    ax.plot(mensal["mes"].dt.strftime("%m/%Y"), mensal["faturamento"], marker="o")
    ax.set(title="Faturamento por mês de emissão", xlabel="Mês", ylabel="Valor (R$)")
    ax.tick_params(axis="x", rotation=45)
    ax.grid(axis="y", alpha=0.25)
    _salvar(fig, pasta, "01_faturamento_mensal.png")

    top = indicadores["por_produto"].head(8).iloc[::-1]
    fig, ax = plt.subplots(figsize=(11, 5))
    ax.barh(top["produto"], top["faturamento"])
    ax.set(title="Produtos com maior faturamento", xlabel="Valor (R$)")
    _salvar(fig, pasta, "02_top_produtos.png")

    categorias = indicadores["por_categoria"]
    fig, ax = plt.subplots(figsize=(8, 5))
    ax.bar(categorias["categoria"], categorias["faturamento"])
    ax.set(title="Faturamento por categoria", xlabel="Categoria", ylabel="Valor (R$)")
    _salvar(fig, pasta, "03_categorias.png")

    tributos = indicadores["tributos"]
    fig, ax = plt.subplots(figsize=(8, 5))
    ax.bar(tributos["tributo"].str.upper(), tributos["valor"])
    ax.set(title="Tributos simulados (exercício)", xlabel="Tipo", ylabel="Valor (R$)")
    _salvar(fig, pasta, "04_tributos_simulados.png")

    ufs = indicadores["por_uf"]
    fig, ax = plt.subplots(figsize=(8, 5))
    ax.bar(ufs["uf"], ufs["faturamento"])
    ax.set(title="Faturamento por UF", xlabel="Estado", ylabel="Valor (R$)")
    _salvar(fig, pasta, "05_faturamento_por_uf.png")
