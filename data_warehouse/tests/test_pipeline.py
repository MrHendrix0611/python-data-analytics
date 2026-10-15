"""Testes de ingestão, qualidade e reconciliação do warehouse."""
from pathlib import Path
import sqlite3
import pandas as pd
import pytest

from src.coleta import carregar_fontes
from src.qualidade import validar_fontes
from src.warehouse import construir_warehouse
from src.analysis import executar_analises

ROOT=Path(__file__).resolve().parents[1]


@pytest.fixture(scope='module')
def fontes():
    return carregar_fontes(ROOT/'data'/'raw')


def clone(fontes):
    return {chave:df.copy(deep=True) for chave,df in fontes.items()}


def test_ingestao_dos_cinco_formatos(fontes):
    assert len(fontes)==6  # SQLite fornece duas tabelas
    assert len(fontes['pedidos'])==600
    assert len(fontes['clientes'])==200
    assert len(fontes['produtos'])==40
    assert len(fontes['itens'])==1504
    assert len(fontes['entregas'])==521


def test_json_aninhado_normalizado(fontes):
    assert {'segmento','origem','uf','cidade'}.issubset(fontes['clientes'].columns)


def test_xml_namespace_e_atributos(fontes):
    assert fontes['entregas']['id_pedido'].str.startswith('PED').all()
    assert (fontes['entregas']['status_entrega']=='entregue').all()


def test_qualidade_aceita_fontes_validas(fontes):
    dados=validar_fontes(fontes)
    assert dados['itens']['quantidade'].dtype.kind in 'iu'


def test_rejeita_chave_duplicada(fontes):
    entrada=clone(fontes)
    entrada['pedidos'].loc[1,'id_pedido']=entrada['pedidos'].loc[0,'id_pedido']
    with pytest.raises(ValueError,match='duplicada'):
        validar_fontes(entrada)


def test_rejeita_produto_inexistente(fontes):
    entrada=clone(fontes)
    entrada['itens'].loc[0,'sku']='SKU_DESCONHECIDO'
    with pytest.raises(ValueError,match='produto inexistente'):
        validar_fontes(entrada)


def test_rejeita_divergencia_de_pagamento(fontes):
    entrada=clone(fontes)
    entrada['pagamentos'].loc[0,'valor_pago_centavos']+=1
    with pytest.raises(ValueError,match='Divergência'):
        validar_fontes(entrada)


def test_rejeita_pedido_sem_cliente(fontes):
    entrada=clone(fontes)
    entrada['pedidos'].loc[0,'id_cliente']='C_INEXISTENTE'
    with pytest.raises(ValueError,match='cliente inexistente'):
        validar_fontes(entrada)


def test_rejeita_datas_de_entrega_invalidas(fontes):
    entrada=clone(fontes)
    entrada['entregas'].loc[0,'data_entrega']='2025-01-01'
    with pytest.raises(ValueError,match='Datas de entrega'):
        validar_fontes(entrada)


def test_warehouse_modelo_estrela_e_conciliacao(fontes,tmp_path):
    dados=validar_fontes(fontes)
    caminho=tmp_path/'teste_dw.db'
    contagem=construir_warehouse(dados,caminho,ROOT/'sql')
    assert contagem['dim_cliente']==200
    assert contagem['dim_produto']==40
    assert contagem['fato_pedidos']==600
    assert contagem['fato_itens_venda']==1504
    with sqlite3.connect(caminho) as con:
        valor_pedidos=con.execute('SELECT SUM(valor_pago_centavos) FROM fato_pedidos').fetchone()[0]
        valor_itens=con.execute('SELECT SUM(receita_liquida_centavos) FROM fato_itens_venda').fetchone()[0]
        frete_pedidos=con.execute('SELECT SUM(frete_centavos) FROM fato_pedidos').fetchone()[0]
        assert valor_pedidos==valor_itens
        assert valor_pedidos==39479587
        assert frete_pedidos>0
        assert con.execute('PRAGMA foreign_key_check').fetchall()==[]
    tabelas,resumo=executar_analises(caminho)
    assert len(tabelas)==8
    assert resumo['concluidos']==521
    assert resumo['cancelados']==79
    assert resumo['receita']==pytest.approx(394795.87)
    assert tabelas['mensal']['receita'].sum()==pytest.approx(resumo['receita'])


def test_reprocessamento_idempotente(fontes,tmp_path):
    dados=validar_fontes(fontes)
    caminho=tmp_path/'retail_dw.db'
    c1=construir_warehouse(dados,caminho,ROOT/'sql')
    c2=construir_warehouse(dados,caminho,ROOT/'sql')
    assert c1==c2
    with sqlite3.connect(caminho) as con:
        assert con.execute('SELECT COUNT(*) FROM fato_pedidos').fetchone()[0]==600
