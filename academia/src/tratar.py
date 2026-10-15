
import pandas as pd


def preparar_pagamentos(
    dados: dict[str, pd.DataFrame],
    data_referencia: str = "2026-09-30"
) -> pd.DataFrame:
    """Relaciona as tabelas e calcula campos financeiros."""

    pagamentos = dados["Pagamentos"].copy()
    alunos = dados["Alunos"][["id_aluno", "id_plano"]]
    planos = dados["Planos"][["id_plano", "nome_plano"]]

    # Relacionar pagamentos aos alunos
    pagamentos = pagamentos.merge(
        alunos,
        on="id_aluno",
        how="left",
        validate="many_to_one"
    )

    # Relacionar pagamentos aos planos
    pagamentos = pagamentos.merge(
        planos,
        on="id_plano",
        how="left",
        validate="many_to_one"
    )

    # Normalizar a competência para o primeiro dia do mês
    pagamentos["mes"] = (
        pagamentos["competencia"]
        .dt.to_period("M")
        .dt.to_timestamp()
    )

    # Calcular saldo não recebido
    pagamentos["valor_em_aberto"] = (
        pagamentos["valor_cobrado"]
        - pagamentos["valor_pago"]
    ).clip(lower=0)

    # Identificar cobranças vencidas na data de referência
    vencida = (
        pagamentos["data_vencimento"]
        < pd.Timestamp(data_referencia)
    )

    pagamentos["valor_exigivel"] = (
        pagamentos["valor_cobrado"].where(vencida, 0.0)
    )

    pagamentos["valor_vencido"] = (
        pagamentos["valor_em_aberto"].where(vencida, 0.0)
    )

    pagamentos["inadimplente"] = (
        vencida & (pagamentos["valor_em_aberto"] > 0)
    )

    pagamentos["aluno_pagante"] = (
        pagamentos["id_aluno"].where(
            pagamentos["valor_pago"] > 0
        )
    )

    return pagamentos
