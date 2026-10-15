"""Relatório executivo e tabelas derivadas para uso externo."""

from pathlib import Path
import pandas as pd


def reais(valor: float) -> str:
    return "R$ " + f"{valor:,.2f}".replace(",", "_").replace(".", ",").replace("_", ".")


def gerar_relatorio(indicadores: dict, destino: str | Path) -> Path:
    resumo = indicadores["resumo"]
    mensal = indicadores["mensal"]
    categorias = indicadores["categorias"]
    produtos = indicadores["produtos"]
    linhas = [
        "INTELIGÊNCIA COMERCIAL — E-COMMERCE",
        "=" * 47,
        f"Período de vendas: {mensal['mes'].min()} a {mensal['mes'].max()}",
        f"Receita bruta de produtos: {reais(resumo['receita_bruta_reais'])}",
        f"Descontos concedidos: {reais(resumo['descontos_reais'])}",
        f"Receita líquida de produtos: {reais(resumo['receita_liquida_reais'])}",
        f"Lucro bruto estimado: {reais(resumo['lucro_bruto_reais'])}",
        f"Margem bruta estimada: {resumo['margem_bruta_pct']:.2f}%",
        f"Pedidos pagos/entregues: {resumo['pedidos_validos']}",
        f"Pedidos em todos os status: {resumo['pedidos_totais']}",
        f"Unidades vendidas: {resumo['unidades_vendidas']}",
        f"Ticket médio: {reais(resumo['ticket_medio_reais'])}",
        f"Clientes compradores: {resumo['clientes_com_compra']}",
        f"Clientes sem compras: {resumo['clientes_sem_compra']}",
        f"Clientes com 2+ pedidos: {resumo['clientes_recorrentes']}",
        f"Taxa de recompra: {resumo['taxa_recompra_pct']:.2f}%",
        f"Pedidos cancelados: {resumo['pedidos_cancelados']}",
        f"Taxa de cancelamento: {resumo['taxa_cancelamento_pct']:.2f}%",
        "",
        "RECEITA POR CATEGORIA",
        "-" * 47,
    ]
    for linha in categorias.itertuples():
        linhas.append(f"{linha.categoria}: {reais(linha.receita_reais)} ({linha.unidades} unidades)")
    linhas.extend(["", "TOP 5 PRODUTOS", "-" * 47])
    for linha in produtos.head(5).itertuples():
        linhas.append(f"{linha.nome_produto}: {reais(linha.receita_reais)}")
    linhas.extend([
        "", "REGRAS DE CÁLCULO", "-" * 47,
        "- Receita considera apenas pedidos pagos ou entregues.",
        "- Pendente e cancelado não entram na receita nem no ticket médio.",
        "- Receita líquida = quantidade x (preço unitário - desconto unitário).",
        "- Valores financeiros são agregados em centavos antes de converter para reais.",
        "- Lucro bruto estimado = receita líquida - custo dos produtos; não inclui impostos, frete ou despesas.",
        "- Taxa de recompra = compradores com >= 2 pedidos válidos / compradores com >= 1 pedido válido.",
        "- Taxa de cancelamento = pedidos cancelados / total de pedidos no período.",
        "- Números inteiramente sintéticos, não representam uma operação real.",
    ])
    destino = Path(destino)
    destino.parent.mkdir(parents=True, exist_ok=True)
    texto = "\n".join(linhas) + "\n"
    destino.write_text(texto, encoding="utf-8")
    print(texto)
    return destino


def exportar_tabelas(indicadores: dict, pasta: str | Path) -> list[Path]:
    pasta = Path(pasta)
    pasta.mkdir(parents=True, exist_ok=True)
    arquivos = []
    for nome in ("mensal", "categorias", "produtos", "estados", "status", "clientes"):
        destino = pasta / f"{nome}.csv"
        indicadores[nome].to_csv(destino, sep=";", decimal=",", index=False, encoding="utf-8-sig")
        arquivos.append(destino)
    return arquivos
