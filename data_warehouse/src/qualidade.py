"""Contrato de dados: falhar explicitamente em inconsistências de origem."""
import pandas as pd

ESQUEMAS={
    'pedidos':{'id_pedido','data_pedido','id_cliente','canal','status'},
    'clientes':{'id_cliente','nome','segmento','origem','uf','cidade'},
    'produtos':{'sku','produto','categoria','fornecedor','preco_centavos','custo_centavos'},
    'itens':{'id_item','id_pedido','sku','quantidade','preco_unit_centavos','desconto_centavos'},
    'pagamentos':{'id_pedido','metodo','valor_pago_centavos','data_pagamento'},
    'entregas':{'id_pedido','data_envio','data_entrega','frete_centavos','status_entrega'},
}
CHAVES={'pedidos':'id_pedido','clientes':'id_cliente','produtos':'sku',
        'itens':'id_item','pagamentos':'id_pedido','entregas':'id_pedido'}


def validar_fontes(originais:dict[str,pd.DataFrame])->dict[str,pd.DataFrame]:
    dados={}
    for nome,obrigatorias in ESQUEMAS.items():
        if nome not in originais: raise ValueError(f'Fonte ausente: {nome}')
        df=originais[nome].copy()
        faltantes=obrigatorias-set(df.columns)
        if faltantes: raise ValueError(f'{nome}: colunas ausentes {sorted(faltantes)}')
        chave=CHAVES[nome]
        if df[chave].isna().any() or df[chave].duplicated().any():
            raise ValueError(f'{nome}: chave {chave} nula ou duplicada')
        if df[list(obrigatorias)].isna().any().any():
            raise ValueError(f'{nome}: campos obrigatórios nulos')
        dados[nome]=df

    for coluna in ['preco_centavos','custo_centavos']:
        dados['produtos'][coluna]=pd.to_numeric(dados['produtos'][coluna],errors='raise').astype('int64')
    for coluna in ['quantidade','preco_unit_centavos','desconto_centavos']:
        dados['itens'][coluna]=pd.to_numeric(dados['itens'][coluna],errors='raise').astype('int64')
    dados['pagamentos']['valor_pago_centavos']=pd.to_numeric(
        dados['pagamentos']['valor_pago_centavos'],errors='raise').astype('int64')
    dados['entregas']['frete_centavos']=pd.to_numeric(
        dados['entregas']['frete_centavos'],errors='raise').astype('int64')

    if not dados['pedidos']['id_cliente'].isin(dados['clientes']['id_cliente']).all():
        raise ValueError('Pedido com cliente inexistente')
    if not dados['itens']['id_pedido'].isin(dados['pedidos']['id_pedido']).all():
        raise ValueError('Item com pedido inexistente')
    if not dados['itens']['sku'].isin(dados['produtos']['sku']).all():
        raise ValueError('Item com produto inexistente')
    for nome in ['pagamentos','entregas']:
        if not dados[nome]['id_pedido'].isin(dados['pedidos']['id_pedido']).all():
            raise ValueError(f'{nome}: pedido inexistente')
    if not set(dados['pedidos']['status']).issubset({'concluido','cancelado'}):
        raise ValueError('Status de pedido desconhecido')
    if not set(dados['entregas']['status_entrega']).issubset({'entregue'}):
        raise ValueError('Status de entrega desconhecido')

    produtos=dados['produtos'];itens=dados['itens']
    if (produtos[['preco_centavos','custo_centavos']]<0).any().any():
        raise ValueError('Preço ou custo negativo')
    if (produtos['custo_centavos']>produtos['preco_centavos']).any():
        raise ValueError('Custo acima do preço de tabela')
    if ((itens['quantidade']<=0)|(itens['preco_unit_centavos']<=0)|(itens['desconto_centavos']<0)
        |(itens['desconto_centavos']>itens['quantidade']*itens['preco_unit_centavos'])).any():
        raise ValueError('Itens com valores inválidos')
    if (dados['pagamentos']['valor_pago_centavos']<0).any() or (dados['entregas']['frete_centavos']<0).any():
        raise ValueError('Valores monetários negativos')

    # A receita dos itens deve conciliar integralmente com os pagamentos.
    totals=(itens.assign(total=itens['quantidade']*itens['preco_unit_centavos']-itens['desconto_centavos'])
            .groupby('id_pedido')['total'].sum())
    pagos=dados['pagamentos'].set_index('id_pedido')['valor_pago_centavos']
    concluidos=set(dados['pedidos'].loc[dados['pedidos']['status']=='concluido','id_pedido'])
    cancelados=set(dados['pedidos'].loc[dados['pedidos']['status']=='cancelado','id_pedido'])
    if set(pagos.index)!=concluidos or set(dados['entregas']['id_pedido'])!=concluidos:
        raise ValueError('Pedidos concluídos precisam ter um pagamento e uma entrega; cancelados não')
    if not concluidos.issubset(set(totals.index)) or any(pagos[p]!=totals[p] for p in concluidos):
        raise ValueError('Divergência entre itens e pagamentos')
    if any(p in cancelados for p in pagos.index):
        raise ValueError('Pedido cancelado com pagamento')
    for tabela,colunas in [('pedidos',['data_pedido']),('pagamentos',['data_pagamento']),
                           ('entregas',['data_envio','data_entrega'])]:
        for col in colunas:
            dados[tabela][col]=pd.to_datetime(dados[tabela][col],errors='raise').dt.strftime('%Y-%m-%d')
    entrega_join=(dados['entregas'].merge(dados['pedidos'][['id_pedido','data_pedido']],on='id_pedido',validate='one_to_one'))
    if ((entrega_join['data_envio']<entrega_join['data_pedido']) |
        (entrega_join['data_entrega']<entrega_join['data_envio'])).any():
        raise ValueError('Datas de entrega inconsistentes')
    return dados
