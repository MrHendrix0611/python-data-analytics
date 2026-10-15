"""Validação de estrutura, datas e integridade dos dados."""

import pandas as pd


COLUNAS_CLIENTES = {"id_cliente", "nome", "segmento"}
COLUNAS_CHAMADOS = {
    "id_chamado", "categoria", "prioridade", "status", "aberto_em",
    "fechado_em", "reaberto", "avaliacao", "interacoes",
    "atendente.id_atendente", "atendente.nome", "clientes.id_cliente",
}
STATUS_VALIDOS = {"Aberto", "Em andamento", "Resolvido"}


def validar_e_limpar(tabelas: dict[str, pd.DataFrame]) -> dict[str, pd.DataFrame]:
    """Valida tabelas sem modificar os DataFrames originais."""
    if not {"clientes", "chamados"}.issubset(tabelas):
        raise ValueError("As tabelas de clientes e chamados são obrigatórias.")

    clientes = tabelas["clientes"].copy()
    chamados = tabelas["chamados"].copy()

    for nome, df, colunas in [
        ("clientes", clientes, COLUNAS_CLIENTES),
        ("chamados", chamados, COLUNAS_CHAMADOS),
    ]:
        ausentes = colunas.difference(df.columns)
        if ausentes:
            raise ValueError(f"Colunas ausentes em {nome}: {sorted(ausentes)}")
        if df.empty:
            raise ValueError(f"A tabela {nome} está vazia.")

    for nome, df, chave in [
        ("clientes", clientes, "id_cliente"),
        ("chamados", chamados, "id_chamado"),
    ]:
        if df[chave].isna().any() or df[chave].duplicated().any():
            raise ValueError(f"Identificador ausente ou duplicado em {nome}: {chave}")

    if clientes[list(COLUNAS_CLIENTES)].isna().any().any():
        raise ValueError("Há campos obrigatórios vazios em clientes.")

    obrigatorios = ["categoria", "prioridade", "status", "aberto_em", "clientes.id_cliente"]
    if chamados[obrigatorios].isna().any().any():
        raise ValueError("Há campos obrigatórios vazios nos chamados.")

    if not chamados["clientes.id_cliente"].isin(clientes["id_cliente"]).all():
        raise ValueError("Existem chamados vinculados a clientes inexistentes.")

    if not chamados["status"].isin(STATUS_VALIDOS).all():
        raise ValueError("Existem chamados com status inválido.")

    for coluna in ["aberto_em", "fechado_em"]:
        chamados[coluna] = pd.to_datetime(chamados[coluna], errors="raise")

    resolvido = chamados["status"].eq("Resolvido")
    tem_fechamento = chamados["fechado_em"].notna()
    if (resolvido != tem_fechamento).any():
        raise ValueError("A data de fechamento não corresponde ao status.")

    if (chamados.loc[resolvido, "fechado_em"] < chamados.loc[resolvido, "aberto_em"]).any():
        raise ValueError("Há chamados encerrados antes da abertura.")

    if chamados.loc[resolvido, "atendente.id_atendente"].isna().any():
        raise ValueError("Chamados resolvidos precisam de atendente.")

    chamados["avaliacao"] = pd.to_numeric(chamados["avaliacao"], errors="raise")
    avaliacao = chamados["avaliacao"].dropna()
    if not avaliacao.between(1, 5).all() or not avaliacao.mod(1).eq(0).all():
        raise ValueError("A avaliação deve ser um inteiro de 1 a 5.")

    if chamados["reaberto"].map(lambda valor: not isinstance(valor, bool)).any():
        raise ValueError("O campo 'reaberto' deve ser booleano.")

    if (chamados["reaberto"] & ~resolvido).any():
        raise ValueError("Nesta base, reaberturas são registradas após a resolução.")

    if chamados["interacoes"].map(
        lambda valor: not isinstance(valor, list) or len(valor) == 0
    ).any():
        raise ValueError("Todos os chamados precisam de uma lista de interações.")

    return {"clientes": clientes, "chamados": chamados}
