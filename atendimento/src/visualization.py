"""Criação dos gráficos de acompanhamento do suporte."""

from pathlib import Path

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import pandas as pd


def gerar_graficos(indicadores: dict, pasta_saida: str | Path) -> list[Path]:
    """Salva cinco gráficos e retorna seus caminhos."""
    destino = Path(pasta_saida)
    destino.mkdir(parents=True, exist_ok=True)
    arquivos = []

    def salvar(fig, nome):
        fig.tight_layout()
        caminho = destino / nome
        fig.savefig(caminho, dpi=160, bbox_inches="tight")
        plt.close(fig)
        arquivos.append(caminho)

    evolucao = indicadores["evolucao"]
    categorias = indicadores["por_categoria"]
    atendentes = indicadores["por_atendente"]
    recorrencia = indicadores["recorrencia"]
    canais = indicadores["por_canal"]

    fig, ax = plt.subplots(figsize=(10, 5))
    meses = evolucao["mes"].dt.strftime("%m/%Y")
    ax.plot(meses, evolucao["abertos"], marker="o", label="Abertos")
    ax.plot(meses, evolucao["resolvidos"], marker="o", label="Resolvidos")
    ax.set(title="Evolução mensal dos chamados", xlabel="Mês", ylabel="Chamados")
    ax.tick_params(axis="x", rotation=45)
    ax.grid(axis="y", alpha=0.2)
    ax.legend()
    salvar(fig, "01_evolucao_chamados.png")

    fig, ax = plt.subplots(figsize=(9, 5))
    base = categorias.sort_values("chamados")
    ax.barh(base["categoria"], base["chamados"])
    ax.set(title="Volume por categoria", xlabel="Quantidade de chamados")
    salvar(fig, "02_categorias.png")

    fig, ax = plt.subplots(figsize=(9, 5))
    base = atendentes.sort_values("resolvidos")
    ax.barh(base["atendente.nome"], base["resolvidos"])
    ax.set(title="Chamados resolvidos por atendente", xlabel="Chamados resolvidos")
    salvar(fig, "03_atendentes.png")

    fig, ax = plt.subplots(figsize=(9, 5))
    base = recorrencia.sort_values("taxa_recorrencia_pct")
    ax.barh(base["categoria"], base["taxa_recorrencia_pct"])
    ax.set(
        title="Clientes recorrentes por categoria",
        xlabel="Clientes com 2+ chamados na categoria (%)",
        xlim=(0, 100),
    )
    salvar(fig, "04_recorrencia.png")

    fig, ax = plt.subplots(figsize=(8, 5))
    ax.bar(canais["canal"], canais["interacoes"])
    ax.set(title="Interações por canal", xlabel="Canal", ylabel="Interações")
    ax.tick_params(axis="x", rotation=20)
    salvar(fig, "05_canais.png")

    return arquivos
