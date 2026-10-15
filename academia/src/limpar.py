
import pandas as pd

COLUNAS_OBRIGATORIAS = {
    "Alunos": [
        "id_aluno", "nome_aluno", "data_matricula",
        "data_cancelamento", "id_plano"
    ],
    "Planos": [
        "id_plano", "nome_plano", "valor_mensal"
    ],
    "Pagamentos": [
        "id_pagamento", "id_aluno", "competencia",
        "data_vencimento", "data_pagamento",
        "valor_cobrado", "valor_pago"
    ],
}


def validar_e_limpar(dados: dict[str, pd.DataFrame]) -> dict[str, pd.DataFrame]:
    """Valida a estrutura, tipos e consistência das tabelas."""
    limpos = {}

    for aba, colunas in COLUNAS_OBRIGATORIAS.items():
        if aba not in dados:
            raise ValueError(f"Aba obrigatória ausente: {aba}")

        ausentes = set(colunas) - set(dados[aba].columns)
        if ausentes:
            raise ValueError(
                f"Colunas ausentes em {aba}: {sorted(ausentes)}"
            )

        limpos[aba] = dados[aba].copy()

    alunos = limpos["Alunos"]
    planos = limpos["Planos"]
    pagamentos = limpos["Pagamentos"]

    # Converter datas
    for df, coluna in [
        (alunos, "data_matricula"),
        (alunos, "data_cancelamento"),
        (pagamentos, "competencia"),
        (pagamentos, "data_vencimento"),
        (pagamentos, "data_pagamento"),
    ]:
        df[coluna] = pd.to_datetime(df[coluna], errors="raise")

    # Converter valores numéricos
    for df, coluna in [
        (alunos, "id_plano"),
        (planos, "id_plano"),
        (planos, "valor_mensal"),
        (pagamentos, "valor_cobrado"),
        (pagamentos, "valor_pago"),
    ]:
        df[coluna] = pd.to_numeric(df[coluna], errors="raise")

    # Validar chaves primárias
    for df, chave in [
        (alunos, "id_aluno"),
        (planos, "id_plano"),
        (pagamentos, "id_pagamento"),
    ]:
        if df[chave].isna().any() or df[chave].duplicated().any():
            raise ValueError(f"Chave ausente ou duplicada: {chave}")

    # Validar campos obrigatórios
    for df, colunas in [
        (alunos, ["nome_aluno", "data_matricula", "id_plano"]),
        (planos, ["nome_plano", "valor_mensal"]),
        (pagamentos, [
            "id_aluno", "competencia", "data_vencimento",
            "valor_cobrado", "valor_pago"
        ]),
    ]:
        if df[colunas].isna().any().any():
            raise ValueError(
                f"Valores obrigatórios ausentes: {colunas}"
            )

    # Validar datas de matrícula e cancelamento
    cancelamento_invalido = (
        alunos["data_cancelamento"].notna()
        & (
            alunos["data_cancelamento"]
            < alunos["data_matricula"]
        )
    )

    if cancelamento_invalido.any():
        raise ValueError("Cancelamento anterior à matrícula")

    # Validar relacionamentos
    if not alunos["id_plano"].isin(planos["id_plano"]).all():
        raise ValueError("Há alunos com plano inexistente")

    if not pagamentos["id_aluno"].isin(alunos["id_aluno"]).all():
        raise ValueError("Há pagamentos com aluno inexistente")

    if pagamentos.duplicated(["id_aluno", "competencia"]).any():
        raise ValueError(
            "Há mais de uma cobrança por aluno e competência"
        )

    # Validar valores financeiros
    if (planos["valor_mensal"] <= 0).any():
        raise ValueError("Planos precisam ter mensalidade positiva")

    valores_invalidos = (
        (pagamentos["valor_cobrado"] <= 0)
        | (pagamentos["valor_pago"] < 0)
        | (
            pagamentos["valor_pago"]
            > pagamentos["valor_cobrado"]
        )
    )

    if valores_invalidos.any():
        raise ValueError(
            "Valores de cobrança/pagamento inconsistentes"
        )

    # Pagamentos positivos precisam ter data
    tem_data = pagamentos["data_pagamento"].notna()
    tem_valor = pagamentos["valor_pago"] > 0

    if (tem_data != tem_valor).any():
        raise ValueError(
            "Data de pagamento e valor pago inconsistentes"
        )

    return limpos
