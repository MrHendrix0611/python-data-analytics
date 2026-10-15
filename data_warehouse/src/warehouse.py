"""Persistência da staging e construção transacional do modelo dimensional."""
import os
from contextlib import closing
from pathlib import Path
import sqlite3
import pandas as pd

STAGES={'pedidos':'stg_pedidos','clientes':'stg_clientes','produtos':'stg_produtos',
        'itens':'stg_itens','pagamentos':'stg_pagamentos','entregas':'stg_entregas'}


def construir_warehouse(dados:dict[str,pd.DataFrame],destino:Path,sql_dir:Path)->dict[str,int]:
    destino.parent.mkdir(parents=True,exist_ok=True)
    temporario=destino.with_name(destino.stem+'.tmp.db')
    if temporario.exists(): temporario.unlink()
    try:
        with closing(sqlite3.connect(temporario)) as con, con:
            con.execute('PRAGMA foreign_keys=ON')
            for origem,staging in STAGES.items():
                dados[origem].to_sql(staging,con,if_exists='fail',index=False)
            con.executescript((sql_dir/'schema.sql').read_text(encoding='utf-8'))
            con.executescript((sql_dir/'carga_dimensional.sql').read_text(encoding='utf-8'))
            if con.execute('PRAGMA foreign_key_check').fetchall():
                raise ValueError('Falha de integridade referencial no warehouse')
            quantidades={tab:con.execute(f'SELECT COUNT(*) FROM {tab}').fetchone()[0]
                         for tab in ['dim_cliente','dim_produto','dim_canal','dim_tempo',
                                     'fato_pedidos','fato_itens_venda']}
            if quantidades['fato_pedidos']!=len(dados['pedidos']) or quantidades['fato_itens_venda']!=len(dados['itens']):
                raise ValueError('Falha na reconciliação de quantidade de registros')
            pago=con.execute('SELECT SUM(valor_pago_centavos) FROM fato_pedidos').fetchone()[0] or 0
            faturado=con.execute('SELECT SUM(receita_liquida_centavos) FROM fato_itens_venda').fetchone()[0] or 0
            if pago!=faturado: raise ValueError(f'Divergência financeira: pagamento={pago}; fato={faturado}')
            con.commit()
        # Mantém a versão anterior intacta em caso de falha no processamento.
        os.replace(temporario,destino)
        return quantidades
    except Exception:
        if temporario.exists(): temporario.unlink()
        raise
