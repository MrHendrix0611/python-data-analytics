"""Relacionamento de notas e itens e criação de colunas derivadas."""

import pandas as pd


def preparar_dados(dados: dict[str, pd.DataFrame]) -> dict[str, pd.DataFrame]:
    """Mantém situação geral e separa documentos válidos para faturamento."""
    notas = dados["notas"].copy()
    itens = dados["itens"].copy()

    notas["mes"] = notas["data_emissao"].dt.to_period("M").dt.to_timestamp()

    # JOIN many_to_one: muitos itens pertencem a uma única nota.
    itens = itens.merge(
        notas[["id_nota", "situacao", "data_emissao", "mes", "cliente_id", "cliente", "uf"]],
        on="id_nota",
        how="left",
        validate="many_to_one",
    )

    return {
        "notas_todas": notas,
        "itens_todos": itens,
        "notas": notas.loc[notas["situacao"] == "emitida"].copy(),
        "itens": itens.loc[itens["situacao"] == "emitida"].copy(),
    }
