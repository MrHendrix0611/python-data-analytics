"""Relatório executivo com indicadores obtidos da análise."""

from pathlib import Path


def reais(valor: float) -> str:
    return "R$ " + f"{valor:,.2f}".replace(",", "X").replace(".", ",").replace("X", ".")


def gerar_relatorio(indicadores: dict, destino: str | Path) -> None:
    resumo = indicadores["resumo"]
    top = indicadores["por_produto"].iloc[0]
    uf = indicadores["por_uf"].iloc[0]
    categoria = indicadores["por_categoria"].iloc[0]
    mensal = indicadores["mensal"]

    linhas = [
        "ANÁLISE DE DOCUMENTOS FISCAIS — RELATÓRIO",
        "=" * 43,
        f"Período: {mensal['mes'].min():%m/%Y} a {mensal['mes'].max():%m/%Y}",
        f"Documentos encontrados: {resumo['notas_total']}",
        f"Documentos emitidos: {resumo['notas_emitidas']}",
        f"Documentos cancelados: {resumo['notas_canceladas']}",
        f"Faturamento (somente emitidos): {reais(resumo['faturamento'])}",
        f"Ticket médio por nota: {reais(resumo['ticket_medio'])}",
        f"Unidades vendidas: {resumo['quantidade_itens']}",
        f"Clientes únicos: {resumo['clientes_unicos']}",
        f"Soma de tributos simulados: {reais(resumo['tributos_simulados'])}",
        "",
        "FATURAMENTO POR MÊS",
    ]
    for _, linha in mensal.iterrows():
        linhas.append(f"{linha['mes']:%m/%Y} — {reais(linha['faturamento'])} ({linha['quantidade_notas']} notas)")

    linhas.extend([
        "",
        "OBSERVAÇÕES BASEADAS NOS DADOS",
        f"- Maior faturamento por produto: {top['produto']} ({reais(top['faturamento'])}).",
        f"- Categoria com maior faturamento: {categoria['categoria']} ({reais(categoria['faturamento'])}).",
        f"- UF com maior faturamento: {uf['uf']} ({reais(uf['faturamento'])}).",
        "",
        "METODOLOGIA",
        "- Valores calculados por data de emissão do documento.",
        "- Documentos cancelados não entram no faturamento nem nos tributos.",
        "- Valor da nota representa exclusivamente a soma dos produtos no cenário fictício.",
        "- Tributos são números simulados para fins didáticos, sem validade fiscal.",
        "- Os dados não representam operações, clientes ou documentos reais.",
    ])
    texto = "\n".join(linhas)
    caminho = Path(destino)
    caminho.parent.mkdir(parents=True, exist_ok=True)
    caminho.write_text(texto + "\n", encoding="utf-8")
    print(texto)
    print(f"\nRelatório gravado em: {caminho}")
