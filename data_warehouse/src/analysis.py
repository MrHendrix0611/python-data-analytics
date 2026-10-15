"""Consultas analíticas sobre o warehouse dimensional."""
from pathlib import Path
from contextlib import closing
import sqlite3
import pandas as pd

CONSULTAS = {
'mensal': '''
    SELECT printf('%04d-%02d',t.ano,t.mes) AS mes,
           SUM(f.receita_liquida_centavos)/100.0 AS receita,
           SUM(f.custo_centavos)/100.0 AS custo_produtos,
           SUM(f.quantidade_vendida) AS unidades
    FROM fato_itens_venda f JOIN dim_tempo t ON t.data_sk=f.data_sk
    GROUP BY t.ano,t.mes ORDER BY t.ano,t.mes''',
'categoria': '''
    SELECT d.categoria,SUM(f.receita_liquida_centavos)/100.0 AS receita,
           SUM(f.quantidade_vendida) AS unidades
    FROM fato_itens_venda f JOIN dim_produto d ON d.produto_sk=f.produto_sk
    GROUP BY d.categoria ORDER BY receita DESC''',
'canal': '''
    SELECT d.canal,SUM(f.receita_liquida_centavos)/100.0 AS receita,
           COUNT(DISTINCT CASE WHEN f.quantidade_vendida>0 THEN f.id_pedido END) AS pedidos
    FROM fato_itens_venda f JOIN dim_canal d ON d.canal_sk=f.canal_sk
    GROUP BY d.canal ORDER BY receita DESC''',
'estado': '''
    SELECT d.uf,SUM(f.receita_liquida_centavos)/100.0 AS receita
    FROM fato_itens_venda f JOIN dim_cliente d ON d.cliente_sk=f.cliente_sk
    GROUP BY d.uf ORDER BY receita DESC''',
'produtos': '''
    SELECT p.sku,p.produto,SUM(f.quantidade_vendida) AS unidades,
           SUM(f.receita_liquida_centavos)/100.0 AS receita
    FROM fato_itens_venda f JOIN dim_produto p ON p.produto_sk=f.produto_sk
    GROUP BY p.sku,p.produto ORDER BY receita DESC LIMIT 10''',
'pedidos': '''
    SELECT status,COUNT(*) AS quantidade,
           SUM(valor_pago_centavos)/100.0 AS receita
    FROM fato_pedidos GROUP BY status ORDER BY status''',
'clientes': '''
    SELECT d.id_cliente,d.nome,COUNT(*) AS pedidos_concluidos,
           SUM(f.valor_pago_centavos)/100.0 AS gasto_total
    FROM fato_pedidos f JOIN dim_cliente d ON d.cliente_sk=f.cliente_sk
    WHERE f.status='concluido'
    GROUP BY d.id_cliente,d.nome ORDER BY gasto_total DESC LIMIT 10''',
'entregas': '''
    SELECT ca.canal,COUNT(*) AS entregas,
           ROUND(AVG(f.prazo_entrega_dias),2) AS prazo_medio_dias,
           SUM(f.frete_centavos)/100.0 AS custo_frete
    FROM fato_pedidos f JOIN dim_canal ca ON ca.canal_sk=f.canal_sk
    WHERE f.status='concluido' GROUP BY ca.canal ORDER BY ca.canal'''
}


def executar_analises(caminho_warehouse:Path)->tuple[dict[str,pd.DataFrame],dict]:
    with closing(sqlite3.connect(caminho_warehouse)) as con:
        tabelas={nome:pd.read_sql_query(sql,con) for nome,sql in CONSULTAS.items()}
        linha=con.execute('''
            SELECT COUNT(*) AS pedidos,
                   SUM(CASE WHEN status='concluido' THEN 1 ELSE 0 END) AS concluidos,
                   SUM(CASE WHEN status='cancelado' THEN 1 ELSE 0 END) AS cancelados,
                   SUM(valor_pago_centavos) AS total_recebido_centavos,
                   SUM(frete_centavos) AS frete_total_centavos,
                   AVG(CASE WHEN status='concluido' THEN prazo_entrega_dias END) AS prazo_medio
            FROM fato_pedidos''').fetchone()
        custo=con.execute('SELECT SUM(custo_centavos) FROM fato_itens_venda').fetchone()[0] or 0
        n_clientes=con.execute('SELECT COUNT(DISTINCT cliente_sk) FROM fato_pedidos WHERE status=\'concluido\'').fetchone()[0]
    pedidos,concluidos,cancelados,total_cents,frete_cents,prazo=linha
    receita=(total_cents or 0)/100
    custo_produtos=custo/100
    frete=(frete_cents or 0)/100
    resumo={
        'pedidos':int(pedidos), 'concluidos':int(concluidos),'cancelados':int(cancelados),
        'taxa_cancelamento':(cancelados/pedidos*100) if pedidos else 0,
        'receita':receita,'ticket_medio':(receita/concluidos) if concluidos else 0,
        'custo_produtos':custo_produtos, 'frete':frete,
        'margem_contribuicao':receita-custo_produtos-frete,
        'margem_pct':((receita-custo_produtos-frete)/receita*100) if receita else 0,
        'prazo_medio_dias':float(prazo or 0), 'clientes_com_compra':int(n_clientes)
    }
    return tabelas,resumo
