"""Regras de qualidade para dados extraídos do SQLite."""

import pandas as pd

CHAVES = {
    "clientes": "id_cliente", "produtos": "id_produto",
    "pedidos": "id_pedido", "itens_pedido": "id_item",
}


def validar_tabelas(tabelas: dict[str, pd.DataFrame]) -> None:
    """Aponta inconsistências sem modificar ou excluir registros."""
    for nome, chave in CHAVES.items():
        if nome not in tabelas:
            raise ValueError(f"Tabela obrigatória ausente: {nome}")
        df = tabelas[nome]
        if chave not in df or df[chave].isna().any() or df[chave].duplicated().any():
            raise ValueError(f"Chave primária inválida: {nome}.{chave}")

    clientes, produtos, pedidos, itens = (tabelas[n] for n in CHAVES)
    if not pedidos["id_cliente"].isin(clientes["id_cliente"]).all():
        raise ValueError("Pedido associado a cliente inexistente")
    if not itens["id_pedido"].isin(pedidos["id_pedido"]).all():
        raise ValueError("Item associado a pedido inexistente")
    if not itens["id_produto"].isin(produtos["id_produto"]).all():
        raise ValueError("Item associado a produto inexistente")
    if not pedidos["status"].isin(["Pendente", "Pago", "Entregue", "Cancelado"]).all():
        raise ValueError("Status desconhecido")

    if (itens["quantidade"] <= 0).any():
        raise ValueError("Quantidade inválida")
    if ((itens["preco_unitario_centavos"] <= 0)
            | (itens["desconto_unitario_centavos"] < 0)
            | (itens["desconto_unitario_centavos"] >= itens["preco_unitario_centavos"])).any():
        raise ValueError("Preço ou desconto inválido")
    if ((produtos["custo_centavos"] < 0) | (produtos["estoque_atual"] < 0)).any():
        raise ValueError("Custo ou estoque inválido")
    if itens.duplicated(["id_pedido", "id_produto"]).any():
        raise ValueError("Produto duplicado no mesmo pedido")
    if pd.to_datetime(pedidos["data_pedido"], errors="raise").isna().any():
        raise ValueError("Data de pedido inválida")
