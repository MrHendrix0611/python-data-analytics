
from pathlib import Path

import matplotlib
matplotlib.use("Agg")

import matplotlib.pyplot as plt


def gerar_graficos(indicadores: dict, pasta_saida: str | Path) -> None:
    """Gera e salva gráficos em PNG."""

    pasta = Path(pasta_saida)
    pasta.mkdir(parents=True, exist_ok=True)

    mensal = indicadores["mensal"]
    planos = indicadores["por_plano"]
    movimento = indicadores["movimentacao"]

    meses = mensal["mes"].dt.strftime("%m/%Y")

    # Gráfico 1: Receita mensal
    fig, ax = plt.subplots(figsize=(10, 5))

    ax.plot(
        meses, mensal["receita_recebida"],
        marker="o", label="Recebido"
    )
    ax.plot(
        meses, mensal["valor_cobrado"],
        marker="o", label="Cobrado"
    )

    ax.set(
        title="Receita por competência",
        xlabel="Mês",
        ylabel="R$"
    )
    ax.legend()
    ax.tick_params(axis="x", rotation=45)

    fig.tight_layout()
    fig.savefig(pasta / "01_receita_mensal.png", dpi=150)
    plt.close(fig)

    # Gráfico 2: Receita por plano
    fig, ax = plt.subplots(figsize=(8, 5))

    ax.bar(planos["nome_plano"], planos["receita_recebida"])
    ax.set(
        title="Receita recebida por plano",
        xlabel="Plano",
        ylabel="R$"
    )

    fig.tight_layout()
    fig.savefig(pasta / "02_receita_por_plano.png", dpi=150)
    plt.close(fig)

    # Gráfico 3: Matrículas e cancelamentos
    fig, ax = plt.subplots(figsize=(10, 5))

    eixo_x = list(range(len(movimento)))

    ax.bar(
        [x - 0.2 for x in eixo_x],
        movimento["matriculas"],
        width=0.4,
        label="Matrículas"
    )

    ax.bar(
        [x + 0.2 for x in eixo_x],
        movimento["cancelamentos"],
        width=0.4,
        label="Cancelamentos"
    )

    ax.set_xticks(
        eixo_x,
        movimento["mes"].dt.strftime("%m/%Y"),
        rotation=45
    )
    ax.set(
        title="Movimentação de alunos",
        xlabel="Mês",
        ylabel="Quantidade"
    )
    ax.legend()

    fig.tight_layout()
    fig.savefig(pasta / "03_movimentacao_alunos.png", dpi=150)
    plt.close(fig)

    # Gráfico 4: Inadimplência
    fig, ax = plt.subplots(figsize=(10, 5))

    ax.plot(
        meses,
        mensal["taxa_inadimplencia"],
        marker="o"
    )
    ax.set(
        title="Inadimplência por competência",
        xlabel="Mês",
        ylabel="Percentual (%)"
    )
    ax.tick_params(axis="x", rotation=45)

    fig.tight_layout()
    fig.savefig(pasta / "04_inadimplencia.png", dpi=150)
    plt.close(fig)
