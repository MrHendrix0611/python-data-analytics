
from pathlib import Path


def formatar_real(valor: float) -> str:
    return (
        "R$ "
        + f"{valor:,.2f}"
        .replace(",", "X")
        .replace(".", ",")
        .replace("X", ".")
    )


def gerar_relatorio(
    indicadores: dict,
    caminho_saida: str | Path
) -> None:
    """Exibe e salva os indicadores da academia."""

    resumo = indicadores["resumo"]
    mensal = indicadores["mensal"]
    planos = indicadores["por_plano"]

    linhas = [
        "=== ACADEMIA ANALYTICS — RELATÓRIO ===",
        (
            "Período das competências: "
            + mensal["mes"].min().strftime("%m/%Y")
            + " a "
            + mensal["mes"].max().strftime("%m/%Y")
        ),
        "Receita recebida: " + formatar_real(resumo["receita_recebida"]),
        "Valor cobrado: " + formatar_real(resumo["valor_cobrado"]),
        "Valor vencido e em aberto: " + formatar_real(resumo["valor_vencido"]),
        f"Inadimplência em valor: {resumo['taxa_inadimplencia']:.2f}%",
        "Ticket médio por aluno pagante/mês: " + formatar_real(resumo["ticket_medio"]),
        f"Matrículas no período: {resumo['matriculas_periodo']}",
        f"Cancelamentos no período: {resumo['cancelamentos_periodo']}",
        f"Alunos ativos no fim do período: {resumo['alunos_ativos_final']}",
        "",
        "=== RECEITA RECEBIDA POR PLANO ===",
    ]

    for _, plano in planos.iterrows():
        linhas.append(
            f"{plano['nome_plano']}: "
            f"{formatar_real(plano['receita_recebida'])}"
        )

    linhas.extend([
        "",
        "=== RECEITA MENSAL (POR COMPETÊNCIA) ==="
    ])

    for _, mes in mensal.iterrows():
        linhas.append(
            f"{mes['mes']:%m/%Y}: "
            f"{formatar_real(mes['receita_recebida'])} "
            f"| inadimplência: {mes['taxa_inadimplencia']:.2f}%"
        )

    linhas.extend([
        "",
        "NOTAS METODOLÓGICAS:",
        "- A receita é agrupada pelo mês da cobrança (competência), não pela data em que o dinheiro entrou.",
        "- Inadimplência = valor vencido ainda em aberto / valor total das cobranças vencidas.",
        "- Ticket médio = soma recebida / soma dos alunos pagantes de cada mês.",
    ])

    texto = "\n".join(linhas)

    destino = Path(caminho_saida)
    destino.parent.mkdir(parents=True, exist_ok=True)
    destino.write_text(texto, encoding="utf-8")

    print(texto)
    print(f"\nRelatório salvo em: {destino}")
