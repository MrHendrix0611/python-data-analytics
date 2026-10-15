
import pandas as pd


def calcular_movimentacao(
    alunos: pd.DataFrame,
    meses: pd.Series
) -> pd.DataFrame:
    """Calcula matrículas, cancelamentos e alunos ativos."""

    registros = []

    for mes in sorted(pd.to_datetime(meses).unique()):
        inicio = pd.Timestamp(mes)
        fim = inicio + pd.offsets.MonthEnd(0)

        matriculas = alunos["data_matricula"].between(
            inicio, fim
        ).sum()

        cancelamentos = alunos["data_cancelamento"].between(
            inicio, fim
        ).sum()

        ativos = (
            (alunos["data_matricula"] <= fim)
            & (
                alunos["data_cancelamento"].isna()
                | (alunos["data_cancelamento"] > fim)
            )
        ).sum()

        registros.append({
            "mes": inicio,
            "matriculas": int(matriculas),
            "cancelamentos": int(cancelamentos),
            "alunos_ativos": int(ativos)
        })

    return pd.DataFrame(registros)


def calcular_indicadores(
    pagamentos: pd.DataFrame,
    alunos: pd.DataFrame
) -> dict:
    """Calcula indicadores mensais, por plano e consolidados."""

    if pagamentos.empty:
        raise ValueError("Não há pagamentos para analisar")

    # Indicadores mensais
    mensal = pagamentos.groupby(
        "mes", as_index=False
    ).agg(
        receita_recebida=("valor_pago", "sum"),
        valor_cobrado=("valor_cobrado", "sum"),
        valor_exigivel=("valor_exigivel", "sum"),
        valor_vencido=("valor_vencido", "sum"),
        alunos_pagantes=("aluno_pagante", "nunique"),
        cobrancas_inadimplentes=("inadimplente", "sum")
    )

    mensal["taxa_inadimplencia"] = (
        mensal["valor_vencido"]
        .div(
            mensal["valor_exigivel"].where(
                mensal["valor_exigivel"] > 0
            )
        )
        .fillna(0)
        .mul(100)
    )

    mensal["ticket_medio"] = (
        mensal["receita_recebida"]
        .div(
            mensal["alunos_pagantes"].where(
                mensal["alunos_pagantes"] > 0
            )
        )
        .fillna(0)
    )

    # Receita por plano
    por_plano = (
        pagamentos.groupby("nome_plano", as_index=False)
        .agg(
            receita_recebida=("valor_pago", "sum"),
            valor_cobrado=("valor_cobrado", "sum")
        )
        .sort_values("receita_recebida", ascending=False)
    )

    # Movimentação de alunos
    movimentacao = calcular_movimentacao(
        alunos, mensal["mes"]
    )

    total_exigivel = float(pagamentos["valor_exigivel"].sum())
    total_vencido = float(pagamentos["valor_vencido"].sum())
    total_recebido = float(pagamentos["valor_pago"].sum())
    pagantes_total = int(mensal["alunos_pagantes"].sum())

    # Indicadores gerais
    resumo = {
        "receita_recebida": total_recebido,
        "valor_cobrado": float(
            pagamentos["valor_cobrado"].sum()
        ),
        "valor_vencido": total_vencido,
        "taxa_inadimplencia": (
            100 * total_vencido / total_exigivel
        ) if total_exigivel else 0.0,
        "ticket_medio": (
            total_recebido / pagantes_total
        ) if pagantes_total else 0.0,
        "matriculas_periodo": int(
            movimentacao["matriculas"].sum()
        ),
        "cancelamentos_periodo": int(
            movimentacao["cancelamentos"].sum()
        ),
        "alunos_ativos_final": int(
            movimentacao.iloc[-1]["alunos_ativos"]
        )
    }

    return {
        "mensal": mensal,
        "por_plano": por_plano,
        "movimentacao": movimentacao,
        "resumo": resumo
    }
