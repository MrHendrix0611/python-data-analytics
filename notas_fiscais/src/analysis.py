"""Indicadores de faturamento, produtos, clientes e tributos ilustrativos."""

import pandas as pd


def calcular_indicadores(dados: dict[str, pd.DataFrame]) -> dict:
    todas = dados["notas_todas"]
    notas = dados["notas"]
    itens = dados["itens"]
    if notas.empty or itens.empty:
        raise ValueError("Não há documentos emitidos para analisar")

    mensal = (
        notas.groupby("mes", as_index=False)
        .agg(faturamento=("valor_nota", "sum"), quantidade_notas=("id_nota", "nunique"))
        .sort_values("mes")
    )
    por_produto = (
        itens.groupby(["codigo_produto", "produto", "categoria"], as_index=False)
        .agg(quantidade=("quantidade", "sum"), faturamento=("valor_total", "sum"))
        .sort_values("faturamento", ascending=False)
    )
    por_categoria = (
        itens.groupby("categoria", as_index=False)
        .agg(faturamento=("valor_total", "sum"), quantidade=("quantidade", "sum"))
        .sort_values("faturamento", ascending=False)
    )
    por_uf = (
        notas.groupby("uf", as_index=False)
        .agg(faturamento=("valor_nota", "sum"), quantidade_notas=("id_nota", "nunique"))
        .sort_values("faturamento", ascending=False)
    )
    por_cliente = (
        notas.groupby(["cliente_id", "cliente"], as_index=False)
        .agg(faturamento=("valor_nota", "sum"), quantidade_notas=("id_nota", "nunique"))
        .sort_values("faturamento", ascending=False)
    )
    tributos = itens[["icms", "pis", "cofins"]].sum().rename_axis("tributo").reset_index(name="valor")

    quantidade_validas = len(notas)
    receita = float(notas["valor_nota"].sum())
    resumo = {
        "notas_total": len(todas),
        "notas_emitidas": quantidade_validas,
        "notas_canceladas": int((todas["situacao"] == "cancelada").sum()),
        "faturamento": receita,
        "ticket_medio": receita / quantidade_validas,
        "quantidade_itens": int(itens["quantidade"].sum()),
        "tributos_simulados": float(tributos["valor"].sum()),
        "clientes_unicos": int(notas["cliente_id"].nunique()),
    }
    return {
        "resumo": resumo,
        "mensal": mensal,
        "por_produto": por_produto,
        "por_categoria": por_categoria,
        "por_uf": por_uf,
        "por_cliente": por_cliente,
        "tributos": tributos,
    }
