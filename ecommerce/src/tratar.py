"""Enriquecimento de consultas relacionais e cálculo monetário em centavos."""

import pandas as pd


def preparar_vendas(df: pd.DataFrame) -> pd.DataFrame:
    vendas = df.copy()
    if vendas.empty:
        raise ValueError("Nenhuma venda paga ou entregue no período")
    vendas["data_pedido"] = pd.to_datetime(vendas["data_pedido"], errors="raise")
    vendas["mes"] = vendas["data_pedido"].dt.to_period("M").astype(str)
    vendas["receita_bruta_centavos"] = vendas["quantidade"] * vendas["preco_unitario_centavos"]
    vendas["desconto_centavos"] = vendas["quantidade"] * vendas["desconto_unitario_centavos"]
    vendas["receita_liquida_centavos"] = vendas["receita_bruta_centavos"] - vendas["desconto_centavos"]
    vendas["custo_total_centavos"] = vendas["quantidade"] * vendas["custo_centavos"]
    vendas["lucro_bruto_centavos"] = vendas["receita_liquida_centavos"] - vendas["custo_total_centavos"]
    return vendas


def preparar_pedidos(df: pd.DataFrame) -> pd.DataFrame:
    pedidos = df.copy()
    pedidos["data_pedido"] = pd.to_datetime(pedidos["data_pedido"], errors="raise")
    pedidos["mes"] = pedidos["data_pedido"].dt.to_period("M").astype(str)
    return pedidos
