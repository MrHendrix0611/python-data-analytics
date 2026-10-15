"""Leitura de fontes heterogêneas para tabelas de staging."""
from pathlib import Path
from contextlib import closing
import json
import sqlite3

from defusedxml import ElementTree as ET
import pandas as pd

NS = {'ent':'urn:varejo:entregas:v1'}


def carregar_fontes(raw: Path) -> dict[str,pd.DataFrame]:
    # CSV: registros tabulares de pedidos
    pedidos = pd.read_csv(raw / 'pedidos.csv',dtype={'id_pedido':str,'id_cliente':str})

    # XLSX: catálogo de produtos com valores monetários expressos em centavos
    produtos = pd.read_excel(raw / 'catalogo_produtos.xlsx',sheet_name='Catalogo')

    # JSON: perfis e endereços aninhados
    with (raw / 'clientes.json').open(encoding='utf-8') as arq:
        payload=json.load(arq)
    clientes = pd.json_normalize(payload['clientes'],sep='_').rename(columns={
        'perfil_segmento':'segmento','perfil_origem':'origem',
        'endereco_uf':'uf','endereco_cidade':'cidade'})

    # SQLite operacional: tabelas transacionais, distintas do banco analítico
    with closing(sqlite3.connect(raw / 'operacional.db')) as con:
        itens = pd.read_sql_query('SELECT * FROM itens_pedido',con)
        pagamentos = pd.read_sql_query('SELECT * FROM pagamentos',con)

    # XML: elementos e atributos com namespace
    raiz = ET.parse(raw / 'entregas.xml').getroot()
    remessas=[]
    for elemento in raiz.findall('ent:entrega',NS):
        remessas.append({
            'id_pedido': elemento.attrib['pedido'],
            'data_envio': elemento.findtext('ent:data_envio',namespaces=NS),
            'data_entrega': elemento.findtext('ent:data_entrega',namespaces=NS),
            'frete_centavos': elemento.findtext('ent:frete_centavos',namespaces=NS),
            'status_entrega': elemento.findtext('ent:status',namespaces=NS)
        })
    entregas = pd.DataFrame(remessas,columns=[
        'id_pedido','data_envio','data_entrega','frete_centavos','status_entrega'])

    return {'pedidos':pedidos,'clientes':clientes,'produtos':produtos,
            'itens':itens,'pagamentos':pagamentos,'entregas':entregas}
