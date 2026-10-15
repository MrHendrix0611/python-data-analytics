"""KPIs de receita, margem, ticket médio, recompra e comportamento de compra."""

import pandas as pd


def calcular_indicadores(vendas: pd.DataFrame, pedidos: pd.DataFrame,
                        clientes: pd.DataFrame) -> dict:
    if vendas.empty:
        raise ValueError("Não há vendas válidas para calcular indicadores")

    total_centavos = int(vendas["receita_liquida_centavos"].sum())
    bruto_centavos = int(vendas["receita_bruta_centavos"].sum())
    desconto_centavos = int(vendas["desconto_centavos"].sum())
    lucro_centavos = int(vendas["lucro_bruto_centavos"].sum())
    total_pedidos = int(vendas["id_pedido"].nunique())
    total_compradores = int(vendas["id_cliente"].nunique())

    mensal = (
        vendas.groupby("mes", as_index=False)
        .agg(receita_centavos=("receita_liquida_centavos", "sum"),
             pedidos=("id_pedido", "nunique"),
             itens_vendidos=("quantidade", "sum"))
        .sort_values("mes")
    )
    mensal["receita_reais"] = mensal["receita_centavos"] / 100
    mensal["ticket_medio_reais"] = mensal["receita_reais"] / mensal["pedidos"]

    categorias = (
        vendas.groupby("categoria", as_index=False)
        .agg(receita_centavos=("receita_liquida_centavos", "sum"),
             lucro_centavos=("lucro_bruto_centavos", "sum"),
             unidades=("quantidade", "sum"))
        .sort_values("receita_centavos", ascending=False)
    )
    categorias["receita_reais"] = categorias["receita_centavos"] / 100
    categorias["margem_pct"] = categorias["lucro_centavos"] / categorias["receita_centavos"] * 100

    produtos = (
        vendas.groupby(["id_produto", "nome_produto", "categoria"], as_index=False)
        .agg(receita_centavos=("receita_liquida_centavos", "sum"), unidades=("quantidade", "sum"))
        .sort_values("receita_centavos", ascending=False)
    )
    produtos["receita_reais"] = produtos["receita_centavos"] / 100

    estados = (
        vendas.groupby("estado", as_index=False)
        .agg(receita_centavos=("receita_liquida_centavos", "sum"), pedidos=("id_pedido", "nunique"))
        .sort_values("receita_centavos", ascending=False)
    )
    estados["receita_reais"] = estados["receita_centavos"] / 100

    status = (
        pedidos.groupby("status", as_index=False)
        .agg(quantidade=("id_pedido", "nunique"))
        .sort_values("quantidade", ascending=False)
    )

    compras_por_cliente = (
        vendas.groupby("id_cliente", as_index=False)
        .agg(pedidos=("id_pedido", "nunique"),
             receita_centavos=("receita_liquida_centavos", "sum"))
    )
    compras_por_cliente = compras_por_cliente.merge(
        clientes[["id_cliente", "nome", "estado"]], on="id_cliente", validate="one_to_one"
    ).sort_values("receita_centavos", ascending=False)
    compras_por_cliente["receita_reais"] = compras_por_cliente["receita_centavos"] / 100
    clientes_recorrentes = int((compras_por_cliente["pedidos"] >= 2).sum())

    cancelados = int(pedidos["status"].eq("Cancelado").sum())
    registrados = len(pedidos)

    resumo = {
        "receita_bruta_reais": bruto_centavos / 100,
        "descontos_reais": desconto_centavos / 100,
        "receita_liquida_reais": total_centavos / 100,
        "lucro_bruto_reais": lucro_centavos / 100,
        "margem_bruta_pct": 100 * lucro_centavos / total_centavos if total_centavos else 0.0,
        "pedidos_validos": total_pedidos,
        "pedidos_totais": registrados,
        "unidades_vendidas": int(vendas["quantidade"].sum()),
        "ticket_medio_reais": total_centavos / 100 / total_pedidos if total_pedidos else 0.0,
        "clientes_com_compra": total_compradores,
        "clientes_sem_compra": int(len(clientes) - total_compradores),
        "clientes_recorrentes": clientes_recorrentes,
        "taxa_recompra_pct": 100 * clientes_recorrentes / total_compradores if total_compradores else 0.0,
        "pedidos_cancelados": cancelados,
        "taxa_cancelamento_pct": 100 * cancelados / registrados if registrados else 0.0,
    }
    return {
        "resumo": resumo,
        "mensal": mensal,
        "categorias": categorias,
        "produtos": produtos,
        "estados": estados,
        "status": status,
        "clientes": compras_por_cliente,
    }
