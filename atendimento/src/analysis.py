"""Indicadores operacionais dos atendimentos."""

import pandas as pd


def _recorrencia_por_categoria(chamados: pd.DataFrame) -> pd.DataFrame:
    """Clientes recorrentes: clientes com dois ou mais chamados na mesma categoria."""
    frequencia = (
        chamados.groupby(["categoria", "clientes.id_cliente"])
        .size()
        .reset_index(name="quantidade_cliente")
    )
    recorrencia = (
        frequencia.groupby("categoria", as_index=False)
        .agg(
            clientes_unicos=("clientes.id_cliente", "nunique"),
            clientes_recorrentes=("quantidade_cliente", lambda s: int(s.ge(2).sum())),
        )
    )
    recorrencia["taxa_recorrencia_pct"] = (
        100 * recorrencia["clientes_recorrentes"] / recorrencia["clientes_unicos"]
    )
    return recorrencia.sort_values("taxa_recorrencia_pct", ascending=False)


def calcular_indicadores(
    chamados: pd.DataFrame,
    interacoes: pd.DataFrame,
    data_referencia: str = "2026-09-30",
) -> dict:
    """Agrega métricas de volume, resolução, equipe e recorrência."""
    if chamados.empty:
        raise ValueError("Não há chamados para analisar.")

    resolvido = chamados["status"].eq("Resolvido")
    encerrados = chamados.loc[resolvido]
    total = len(chamados)
    concluidos = len(encerrados)

    resumo = {
        "total_chamados": total,
        "resolvidos": concluidos,
        "pendentes": total - concluidos,
        "taxa_resolucao_pct": round(100 * concluidos / total, 2),
        "tempo_medio_resolucao_horas": float(
            encerrados["tempo_resolucao_horas"].mean()
        ),
        "tempo_medio_primeira_resposta_horas": float(
            chamados["tempo_primeira_resposta_horas"].mean()
        ),
        "avaliacao_media": float(encerrados["avaliacao"].mean()),
        "chamados_reabertos": int(encerrados["reaberto"].sum()),
        "total_interacoes": len(interacoes),
        "horas_trabalho_registradas": float(
            interacoes["tempo_gasto_minutos"].sum() / 60
        ),
    }

    por_categoria = (
        chamados.assign(resolvido=resolvido)
        .groupby("categoria", as_index=False)
        .agg(
            chamados=("id_chamado", "size"),
            resolvidos=("resolvido", "sum"),
            tempo_medio_resolucao_horas=("tempo_resolucao_horas", "mean"),
        )
        .sort_values("chamados", ascending=False)
    )
    por_categoria["taxa_resolucao_pct"] = (
        100 * por_categoria["resolvidos"] / por_categoria["chamados"]
    )

    por_atendente = (
        encerrados.groupby("atendente.nome", as_index=False)
        .agg(
            resolvidos=("id_chamado", "size"),
            tempo_medio_resolucao_horas=("tempo_resolucao_horas", "mean"),
            avaliacao_media=("avaliacao", "mean"),
        )
        .sort_values("resolvidos", ascending=False)
    )

    inicio = chamados["mes_abertura"].min()
    fim = pd.Timestamp(data_referencia).to_period("M").to_timestamp()
    meses = pd.date_range(inicio, fim, freq="MS")
    abertos = chamados.groupby("mes_abertura").size().reindex(meses, fill_value=0)
    fechamentos = (
        encerrados["fechado_em"].dt.to_period("M").dt.to_timestamp()
    )
    concluidos_por_mes = (
        fechamentos.value_counts().reindex(meses, fill_value=0)
    )
    evolucao = pd.DataFrame({
        "mes": meses,
        "abertos": abertos.to_numpy(),
        "resolvidos": concluidos_por_mes.to_numpy(),
    })

    por_canal = (
        interacoes.groupby("canal", as_index=False)
        .agg(interacoes=("id_chamado", "size"))
        .sort_values("interacoes", ascending=False)
    )

    return {
        "resumo": resumo,
        "por_categoria": por_categoria,
        "por_atendente": por_atendente,
        "recorrencia": _recorrencia_por_categoria(chamados),
        "evolucao": evolucao,
        "por_canal": por_canal,
    }
