"""Validação explícita das tabelas extraídas dos documentos XML."""

import pandas as pd

NOTAS_NUMEROS = ("valor_produtos", "valor_nota", "tributos_simulados")
ITENS_NUMEROS = ("numero_item", "quantidade", "valor_unitario", "valor_total", "icms", "pis", "cofins")


def validar_e_limpar(dados: dict[str, pd.DataFrame]) -> dict[str, pd.DataFrame]:
    """Converte tipos e rejeita dados inválidos sem descartar registros."""
    if set(dados) != {"notas", "itens"}:
        raise ValueError("Esperadas as tabelas notas e itens")
    notas = dados["notas"].copy()
    itens = dados["itens"].copy()

    if notas.empty or itens.empty:
        raise ValueError("Tabelas de origem vazias")
    if notas.isna().any().any() or itens.isna().any().any():
        raise ValueError("Há campos obrigatórios vazios")
    if notas["id_nota"].duplicated().any():
        raise ValueError("ID de nota duplicado")
    if itens.duplicated(["id_nota", "numero_item"]).any():
        raise ValueError("Número de item duplicado na mesma nota")
    if not itens["id_nota"].isin(notas["id_nota"]).all():
        raise ValueError("Há itens associados a notas inexistentes")
    if not notas["situacao"].isin(["emitida", "cancelada"]).all():
        raise ValueError("Situação de documento desconhecida")
    if not notas["uf"].str.fullmatch(r"[A-Z]{2}").all():
        raise ValueError("UF fora do formato esperado")

    notas["data_emissao"] = pd.to_datetime(notas["data_emissao"], errors="raise")
    if notas["data_emissao"].isna().any():
        raise ValueError("Datas de emissão ausentes")

    for coluna in NOTAS_NUMEROS:
        notas[coluna] = pd.to_numeric(notas[coluna], errors="raise")
    for coluna in ITENS_NUMEROS:
        itens[coluna] = pd.to_numeric(itens[coluna], errors="raise")

    if (notas[list(NOTAS_NUMEROS)] < 0).any().any():
        raise ValueError("Totais negativos")
    if (itens[["quantidade", "valor_unitario", "valor_total"]] <= 0).any().any():
        raise ValueError("Quantidade ou preço inválidos")
    if (itens[["icms", "pis", "cofins"]] < 0).any().any():
        raise ValueError("Tributos simulados negativos")
    if (itens["numero_item"] <= 0).any():
        raise ValueError("Número de item inválido")

    # A validação de valores utiliza tolerância de centavos.
    erro_item = (itens["quantidade"] * itens["valor_unitario"] - itens["valor_total"]).abs()
    if (erro_item > 0.011).any():
        raise ValueError("Valor total de item inconsistente")

    somas = itens.assign(
        tributos=itens[["icms", "pis", "cofins"]].sum(axis=1)
    ).groupby("id_nota").agg(
        itens_total=("valor_total", "sum"),
        tributos_total=("tributos", "sum"),
    )
    comparacao = notas.set_index("id_nota").join(somas, validate="one_to_one")
    if (comparacao["valor_produtos"] - comparacao["itens_total"]).abs().gt(0.011).any():
        raise ValueError("Total dos produtos não confere com itens")
    if (comparacao["valor_nota"] - comparacao["valor_produtos"]).abs().gt(0.011).any():
        raise ValueError("Valor da nota não confere com produtos")
    if (comparacao["tributos_simulados"] - comparacao["tributos_total"]).abs().gt(0.011).any():
        raise ValueError("Tributos simulados não conferem")

    return {"notas": notas, "itens": itens}
