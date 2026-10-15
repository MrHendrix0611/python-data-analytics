"""Transformação de estruturas aninhadas e criação de variáveis derivadas."""

import pandas as pd

TIPOS_INTERACAO = {"mensagem_cliente", "resposta_atendente", "nota_interna"}


def normalizar_interacoes(chamados: pd.DataFrame) -> pd.DataFrame:
    """Converte a lista de interações de cada chamado em linhas individuais."""
    expandidos = chamados[
        ["id_chamado", "clientes.id_cliente", "aberto_em", "fechado_em", "interacoes"]
    ].explode("interacoes", ignore_index=True)

    detalhes = pd.json_normalize(expandidos["interacoes"], sep=".")
    campos = {"data", "tipo", "canal", "tempo_gasto_minutos"}
    if not campos.issubset(detalhes.columns):
        raise ValueError("Há interações sem os campos esperados.")

    interacoes = pd.concat(
        [expandidos.drop(columns="interacoes"), detalhes], axis=1
    )
    interacoes["data"] = pd.to_datetime(interacoes["data"], errors="raise")
    interacoes["tempo_gasto_minutos"] = pd.to_numeric(
        interacoes["tempo_gasto_minutos"], errors="raise"
    )

    if interacoes[list(campos)].isna().any().any():
        raise ValueError("Há informações obrigatórias ausentes em interações.")
    if not interacoes["tipo"].isin(TIPOS_INTERACAO).all():
        raise ValueError("Há tipos de interação desconhecidos.")
    if (interacoes["tempo_gasto_minutos"] < 0).any():
        raise ValueError("Tempo de atendimento não pode ser negativo.")
    if (interacoes["data"] < interacoes["aberto_em"]).any():
        raise ValueError("Há interações anteriores à abertura do chamado.")

    encerradas = interacoes["fechado_em"].notna()
    if (interacoes.loc[encerradas, "data"] > interacoes.loc[encerradas, "fechado_em"]).any():
        raise ValueError("Há interações posteriores ao fechamento do chamado.")

    return interacoes.sort_values(["id_chamado", "data"]).reset_index(drop=True)


def preparar_chamados(
    chamados: pd.DataFrame,
    interacoes: pd.DataFrame,
    data_referencia: str = "2026-09-30",
) -> pd.DataFrame:
    """Calcula tempo de resolução e intervalo até a primeira resposta."""
    resultado = chamados.drop(columns=["interacoes"]).copy()
    corte = pd.Timestamp(data_referencia) + pd.Timedelta(days=1)

    if (resultado["aberto_em"] >= corte).any():
        raise ValueError("Há chamados abertos após a data de referência.")
    if (interacoes["data"] >= corte).any():
        raise ValueError("Há interações após a data de referência.")
    if (resultado["fechado_em"].dropna() >= corte).any():
        raise ValueError("Há fechamentos após a data de referência.")

    resultado["mes_abertura"] = (
        resultado["aberto_em"].dt.to_period("M").dt.to_timestamp()
    )
    resultado["tempo_resolucao_horas"] = (
        (resultado["fechado_em"] - resultado["aberto_em"])
        .dt.total_seconds()
        .div(3600)
    )

    primeira_resposta = (
        interacoes[interacoes["tipo"].eq("resposta_atendente")]
        .groupby("id_chamado")["data"]
        .min()
        .rename("primeira_resposta")
    )
    resultado = resultado.merge(
        primeira_resposta,
        how="left",
        left_on="id_chamado",
        right_index=True,
        validate="one_to_one",
    )
    resultado["tempo_primeira_resposta_horas"] = (
        (resultado["primeira_resposta"] - resultado["aberto_em"])
        .dt.total_seconds()
        .div(3600)
    )
    return resultado
