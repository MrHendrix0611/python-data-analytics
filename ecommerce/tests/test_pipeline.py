"""Testes unitários e de integração do pipeline SQLite -> Pandas."""

from pathlib import Path

import pandas as pd
import pytest

from scripts.gerar_base import criar_base
from src.analysis import calcular_indicadores
from src.coleta import consultar_pedidos, consultar_vendas, ler_tabelas, verificar_integridade
from src.limpar import validar_tabelas
from src.tratar import preparar_pedidos, preparar_vendas


@pytest.fixture
def banco(tmp_path):
    caminho = tmp_path / "ecommerce.db"
    criar_base(caminho, seed=2026)
    return caminho


def test_gerador_cria_tabelas_e_relacionamentos(banco):
    tabelas = ler_tabelas(banco)
    assert len(tabelas["clientes"]) == 240
    assert len(tabelas["produtos"]) == 54
    assert len(tabelas["pedidos"]) == 1000
    assert len(tabelas["itens_pedido"]) >= 1000
    verificar_integridade(banco)
    validar_tabelas(tabelas)


def test_gerador_nao_sobrescreve_sem_force(banco):
    with pytest.raises(FileExistsError):
        criar_base(banco)


def test_dados_sao_reproduziveis(tmp_path):
    a = tmp_path / "a.db"
    b = tmp_path / "b.db"
    criar_base(a, seed=2026)
    criar_base(b, seed=2026)
    for tabela in ("clientes", "produtos", "pedidos", "itens_pedido"):
        pd.testing.assert_frame_equal(ler_tabelas(a)[tabela], ler_tabelas(b)[tabela])


def test_banco_inexistente_nao_e_criado(tmp_path):
    caminho = tmp_path / "ausente.db"
    with pytest.raises(FileNotFoundError):
        ler_tabelas(caminho)
    assert not caminho.exists()


def test_consulta_exclui_cancelados_e_pendentes(banco):
    linhas = consultar_vendas(banco, "2026-01-01", "2026-09-30")
    tabelas = ler_tabelas(banco)
    validos = set(tabelas["pedidos"].loc[
        tabelas["pedidos"]["status"].isin(["Pago", "Entregue"]), "id_pedido"
    ])
    assert set(linhas["id_pedido"]).issubset(validos)
    assert linhas["id_pedido"].nunique() == len(validos)


def test_filtro_de_periodo_por_sql(banco):
    linhas = consultar_vendas(banco, "2026-03-01", "2026-03-31")
    datas = pd.to_datetime(linhas["data_pedido"])
    assert (datas >= pd.Timestamp("2026-03-01")).all()
    assert (datas <= pd.Timestamp("2026-03-31")).all()


def test_calculo_unitario_em_centavos():
    linhas = pd.DataFrame([{
        "id_item": 1, "id_pedido": 10, "id_cliente": 100, "estado": "SP",
        "data_pedido": "2026-01-02", "id_produto": 2, "nome_produto": "Mouse",
        "categoria": "Informática", "quantidade": 3,
        "preco_unitario_centavos": 999, "desconto_unitario_centavos": 99,
        "custo_centavos": 500,
    }])
    resultado = preparar_vendas(linhas).iloc[0]
    assert resultado["receita_bruta_centavos"] == 2997
    assert resultado["desconto_centavos"] == 297
    assert resultado["receita_liquida_centavos"] == 2700
    assert resultado["lucro_bruto_centavos"] == 1200


def test_indicadores_nao_duplicam_pedido():
    # Dois itens no pedido 1, mais um pedido do mesmo cliente.
    vendas = pd.DataFrame([
        [1, 1, 10, "SP", "2026-01-04", 1, "Mouse", "Informática", 2, 1000, 100, 400],
        [2, 1, 10, "SP", "2026-01-04", 2, "Caderno", "Papelaria", 1, 2000, 0, 900],
        [3, 2, 10, "SP", "2026-01-10", 1, "Mouse", "Informática", 1, 1000, 0, 400],
    ], columns=["id_item", "id_pedido", "id_cliente", "estado", "data_pedido", "id_produto",
                "nome_produto", "categoria", "quantidade", "preco_unitario_centavos",
                "desconto_unitario_centavos", "custo_centavos"])
    pedidos = pd.DataFrame([
        [1, 10, "2026-01-04", "Pago"],
        [2, 10, "2026-01-10", "Entregue"],
        [3, 11, "2026-01-12", "Cancelado"],
    ], columns=["id_pedido", "id_cliente", "data_pedido", "status"])
    clientes = pd.DataFrame({
        "id_cliente": [10, 11], "nome": ["Ana", "Bia"], "estado": ["SP", "RJ"]
    })
    ind = calcular_indicadores(preparar_vendas(vendas), preparar_pedidos(pedidos), clientes)
    r = ind["resumo"]
    assert r["pedidos_validos"] == 2
    assert r["pedidos_totais"] == 3
    assert r["receita_liquida_reais"] == 48.0
    assert r["ticket_medio_reais"] == 24.0
    assert r["clientes_com_compra"] == 1
    assert r["clientes_sem_compra"] == 1
    assert r["taxa_recompra_pct"] == 100.0
    assert r["pedidos_cancelados"] == 1
    assert r["taxa_cancelamento_pct"] == pytest.approx(100/3)


def test_valida_chaves_duplicadas(banco):
    tabelas = ler_tabelas(banco)
    tabelas["clientes"].loc[1, "id_cliente"] = 1
    with pytest.raises(ValueError, match="Chave primária inválida"):
        validar_tabelas(tabelas)


def test_valida_referencia_inexistente(banco):
    tabelas = ler_tabelas(banco)
    tabelas["itens_pedido"].loc[0, "id_produto"] = -123
    with pytest.raises(ValueError, match="produto inexistente"):
        validar_tabelas(tabelas)


def test_pipeline_completo(banco):
    tabelas = ler_tabelas(banco)
    validar_tabelas(tabelas)
    vendas = preparar_vendas(consultar_vendas(banco, "2026-01-01", "2026-09-30"))
    pedidos = preparar_pedidos(consultar_pedidos(banco, "2026-01-01", "2026-09-30"))
    resultado = calcular_indicadores(vendas, pedidos, tabelas["clientes"])
    assert resultado["resumo"]["receita_liquida_reais"] > 0
    assert resultado["resumo"]["pedidos_validos"] <= 1000
    assert len(resultado["mensal"]) == 9
    assert len(resultado["categorias"]) == 9
    assert resultado["mensal"]["receita_centavos"].sum() == vendas["receita_liquida_centavos"].sum()
