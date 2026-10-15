"""Relatório de indicadores em Markdown, legível no VS Code ou GitHub."""
from pathlib import Path


def real(x:float)->str:
    return 'R$ '+f'{x:,.2f}'.replace(',','_').replace('.',',').replace('_','.')


def gerar_relatorio(resumo:dict,tabelas:dict,destino:Path)->None:
    destino.parent.mkdir(parents=True,exist_ok=True)
    linhas=[
      '# Relatório gerencial — Retail Data Warehouse',
      '', 'Período analisado: janeiro a setembro de 2026. Dados sintéticos.',
      '', '## Indicadores', '',
      f'- Pedidos: **{resumo["pedidos"]}**',
      f'- Pedidos concluídos: **{resumo["concluidos"]}**',
      f'- Pedidos cancelados: **{resumo["cancelados"]}** ({resumo["taxa_cancelamento"]:.2f}%)',
      f'- Receita: **{real(resumo["receita"])}**',
      f'- Ticket médio por pedido concluído: **{real(resumo["ticket_medio"])}**',
      f'- Custo de produtos: **{real(resumo["custo_produtos"])}**',
      f'- Custo logístico: **{real(resumo["frete"])}**',
      f'- Margem de contribuição simplificada: **{real(resumo["margem_contribuicao"])}** ({resumo["margem_pct"]:.2f}%)',
      f'- Prazo médio de entrega: **{resumo["prazo_medio_dias"]:.2f} dias**',
      f'- Clientes com compra concluída: **{resumo["clientes_com_compra"]}**',
      '', '## Receita mensal', '', '| Mês | Receita (R$) | Unidades vendidas |','|---|---:|---:|',
    ]
    for _,r in tabelas['mensal'].iterrows():
        linhas.append(f'| {r["mes"]} | {r["receita"]:,.2f} | {int(r["unidades"])} |')
    linhas.extend(['','## Metodologia','',
        '- Receita considera apenas pedidos concluídos e exclui descontos. Agrupamento pelo mês do pedido.',
        '- O frete é custo operacional, não cobrado ao cliente nesta simulação.',
        '- A margem de contribuição é simplificada: receita menos custo dos produtos e frete; não inclui impostos, taxas e despesas fixas.',
        '- A tabela de itens tem grão de um item por pedido; a tabela de pedidos tem grão de um pedido.',
        '- Os resultados são cenários fictícios, não projeções de uma operação real.',
    ])
    destino.write_text('\n'.join(linhas)+'\n',encoding='utf-8')
