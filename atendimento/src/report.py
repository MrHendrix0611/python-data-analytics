"""Relatório operacional em texto."""

from pathlib import Path

import pandas as pd


def _numero(valor: float, casas: int = 1) -> str:
    if pd.isna(valor):
        return "sem dados"
    return f"{valor:.{casas}f}".replace(".", ",")


def gerar_relatorio(
    indicadores: dict,
    destino: str | Path,
    data_referencia: str = "2026-09-30",
) -> Path:
    """Exibe o resumo e salva um relatório TXT em UTF-8."""
    resumo = indicadores["resumo"]
    categorias = indicadores["por_categoria"]
    agentes = indicadores["por_atendente"]
    recorrencia = indicadores["recorrencia"]

    linhas = [
        "ANÁLISE DE ATENDIMENTO AO CLIENTE",
        "=" * 56,
        f"Data de referência: {pd.Timestamp(data_referencia):%d/%m/%Y}",
        "",
        "INDICADORES GERAIS",
        f"Chamados registrados: {resumo['total_chamados']}",
        f"Resolvidos: {resumo['resolvidos']}",
        f"Pendentes: {resumo['pendentes']}",
        f"Taxa de resolução: {_numero(resumo['taxa_resolucao_pct'])}%",
        f"Tempo médio de resolução: {_numero(resumo['tempo_medio_resolucao_horas'])} horas",
        f"Tempo médio até primeira resposta: {_numero(resumo['tempo_medio_primeira_resposta_horas'])} horas",
        f"Avaliação média: {_numero(resumo['avaliacao_media'], 2)} / 5",
        f"Chamados reabertos: {resumo['chamados_reabertos']}",
        f"Interações registradas: {resumo['total_interacoes']}",
        f"Horas de trabalho registradas: {_numero(resumo['horas_trabalho_registradas'])}",
        "",
        "CATEGORIAS MAIS FREQUENTES",
    ]

    for _, item in categorias.iterrows():
        linhas.append(
            f"- {item['categoria']}: {item['chamados']} chamados "
            f"({_numero(item['taxa_resolucao_pct'])}% resolvidos)"
        )

    linhas.extend(["", "PRODUTIVIDADE POR ATENDENTE"])
    for _, item in agentes.iterrows():
        linhas.append(
            f"- {item['atendente.nome']}: {item['resolvidos']} resolvidos; "
            f"tempo médio {_numero(item['tempo_medio_resolucao_horas'])} h"
        )

    linhas.extend(["", "REINCIDÊNCIA POR CATEGORIA"])
    for _, item in recorrencia.iterrows():
        linhas.append(
            f"- {item['categoria']}: {item['clientes_recorrentes']} de "
            f"{item['clientes_unicos']} clientes "
            f"({_numero(item['taxa_recorrencia_pct'])}%)"
        )

    linhas.extend([
        "",
        "NOTAS DE INTERPRETAÇÃO",
        "- Chamados resolvidos: status 'Resolvido' até a data de referência.",
        "- Tempo de resolução: intervalo da abertura ao fechamento de chamados resolvidos.",
        "- Primeira resposta: primeira interação do tipo 'resposta_atendente'.",
        "- Recorrência: cliente com dois ou mais chamados na mesma categoria.",
        "- Volume por atendente não mede sozinho eficiência ou qualidade.",
        "- Valores sem dados não entram nas médias de avaliação e tempo.",
    ])

    caminho = Path(destino)
    caminho.parent.mkdir(parents=True, exist_ok=True)
    texto = "\n".join(linhas)
    caminho.write_text(texto + "\n", encoding="utf-8")
    print(texto)
    return caminho
