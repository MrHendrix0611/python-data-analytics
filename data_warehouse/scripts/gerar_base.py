"""Gera fontes operacionais sintéticas; o catálogo XLSX é mantido como entrada separada."""
from __future__ import annotations
import csv
from contextlib import closing
from datetime import date, timedelta
import json
from pathlib import Path
import random
import sqlite3
import sys
import xml.etree.ElementTree as ET

import pandas as pd

ROOT = Path(__file__).resolve().parents[1]
RAW = ROOT / 'data' / 'raw'
SEED = 2026
NS = 'urn:varejo:entregas:v1'


def gerar_base() -> dict[str, int]:
    RAW.mkdir(parents=True, exist_ok=True)
    rng = random.Random(SEED)
    produtos = pd.read_excel(RAW / 'catalogo_produtos.xlsx', sheet_name='Catalogo')
    registros = produtos.to_dict('records')
    ufs = [('SP','Sao Paulo'),('RJ','Rio de Janeiro'),('MG','Belo Horizonte'),('PR','Curitiba'),('BA','Salvador')]
    clientes = []
    for n in range(1, 201):
        uf, cidade = ufs[(n*7)%len(ufs)]
        clientes.append({
            'id_cliente':f'C{n:04d}', 'nome':f'Cliente {n:04d}',
            'perfil':{'segmento':['Novo','Recorrente','Premium'][n%3], 'origem':['Site','Indicacao','Redes sociais'][n%3]},
            'endereco':{'uf':uf,'cidade':cidade}
        })
    (RAW / 'clientes.json').write_text(json.dumps({'clientes':clientes},indent=2,ensure_ascii=False),encoding='utf-8')

    inicio = date(2026,1,1)
    pedidos=[]; itens=[]; pagamentos=[]; entregas=[]
    for n in range(1,601):
        idp=f'PED{n:05d}'
        data_pedido = inicio + timedelta(days=rng.randrange(273))
        status='cancelado' if rng.random()<0.115 else 'concluido'
        cliente=rng.choice(clientes)['id_cliente']
        canal=rng.choice(['Site','Aplicativo','Marketplace'])
        pedidos.append({'id_pedido':idp,'data_pedido':data_pedido.isoformat(), 'id_cliente':cliente,'canal':canal,'status':status})
        n_itens=rng.randint(1,4)
        total=0
        for k,produto in enumerate(rng.sample(registros, n_itens),start=1):
            qtd=rng.randint(1,3)
            price=int(produto['preco_centavos'])
            desconto=(price*qtd*rng.choice([0,0,0,5,10]))//100
            total+=price*qtd-desconto
            itens.append((f'IT{n:05d}{k:02d}', idp,produto['sku'],qtd,price,desconto))
        if status=='concluido':
            pago=data_pedido+timedelta(days=rng.randint(0,3))
            pagamentos.append((idp, rng.choice(['Pix','Cartao','Boleto']),total,pago.isoformat()))
            envio=data_pedido+timedelta(days=rng.randint(0,2))
            entrega=envio+timedelta(days=rng.randint(2,9))
            entregas.append({'id_pedido':idp,'data_envio':envio.isoformat(), 'data_entrega':entrega.isoformat(),
                             'frete_centavos':rng.randint(900,3600),'status':'entregue'})

    with (RAW/'pedidos.csv').open('w',newline='',encoding='utf-8') as arq:
        writer=csv.DictWriter(arq,fieldnames=list(pedidos[0]));writer.writeheader();writer.writerows(pedidos)

    caminho_db=RAW/'operacional.db'
    if caminho_db.exists(): caminho_db.unlink()
    with closing(sqlite3.connect(caminho_db)) as con, con:
        con.executescript('''
        PRAGMA foreign_keys=ON;
        CREATE TABLE itens_pedido (
            id_item TEXT PRIMARY KEY, id_pedido TEXT NOT NULL, sku TEXT NOT NULL,
            quantidade INTEGER NOT NULL, preco_unit_centavos INTEGER NOT NULL,
            desconto_centavos INTEGER NOT NULL
        );
        CREATE TABLE pagamentos (
            id_pedido TEXT PRIMARY KEY, metodo TEXT NOT NULL,
            valor_pago_centavos INTEGER NOT NULL, data_pagamento TEXT NOT NULL
        );
        ''')
        con.executemany('INSERT INTO itens_pedido VALUES (?,?,?,?,?,?)',itens)
        con.executemany('INSERT INTO pagamentos VALUES (?,?,?,?)',pagamentos)

    ET.register_namespace('ent',NS)
    raiz=ET.Element(f'{{{NS}}}entregas',{'versao':'1.0'})
    for obj in entregas:
        el=ET.SubElement(raiz,f'{{{NS}}}entrega',{'pedido':obj['id_pedido']})
        for chave in ['data_envio','data_entrega','frete_centavos','status']:
            ET.SubElement(el,f'{{{NS}}}{chave}').text=str(obj[chave])
    ET.ElementTree(raiz).write(RAW/'entregas.xml',encoding='utf-8',xml_declaration=True)
    return {'clientes':len(clientes),'produtos':len(registros),'pedidos':len(pedidos),'itens':len(itens),
            'pagamentos':len(pagamentos),'entregas':len(entregas)}


if __name__=='__main__':
    print('Fontes operacionais geradas:',gerar_base())
