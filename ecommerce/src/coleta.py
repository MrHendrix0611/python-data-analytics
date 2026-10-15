"""Leitura das tabelas SQLite e consultas SQL parametrizadas."""

from contextlib import contextmanager
from pathlib import Path
import sqlite3

import pandas as pd

TABELAS = ("clientes", "produtos", "pedidos", "itens_pedido")


@contextmanager
def conectar(caminho: str | Path):
    """Cria uma conexão SQLite e garante seu fechamento."""
    arquivo = Path(caminho)
    if not arquivo.is_file():
        raise FileNotFoundError(f"Banco de dados não encontrado: {arquivo}")
    # SQLite criaria silenciosamente um banco vazio se o caminho não existisse.
    conexao = sqlite3.connect(arquivo)
    try:
        conexao.execute("PRAGMA foreign_keys = ON")
        yield conexao
    finally:
        conexao.close()


def ler_tabelas(caminho: str | Path) -> dict[str, pd.DataFrame]:
    with conectar(caminho) as conn:
        return {
            tabela: pd.read_sql_query(f'SELECT * FROM "{tabela}"', conn)
            for tabela in TABELAS
        }


def verificar_integridade(caminho: str | Path) -> None:
    with conectar(caminho) as conn:
        pendencias = conn.execute("PRAGMA foreign_key_check").fetchall()
        if pendencias:
            raise ValueError(f"Violação de chave estrangeira: {pendencias}")
        resultado = conn.execute("PRAGMA integrity_check").fetchone()[0]
        if resultado != "ok":
            raise ValueError(f"Integridade do SQLite: {resultado}")


SQL_VENDAS = """
SELECT
    i.id_item, i.id_pedido, p.id_cliente, c.estado, p.data_pedido,
    i.id_produto, pr.nome_produto, pr.categoria,
    i.quantidade, i.preco_unitario_centavos,
    i.desconto_unitario_centavos, pr.custo_centavos
FROM itens_pedido AS i
INNER JOIN pedidos AS p ON p.id_pedido = i.id_pedido
INNER JOIN clientes AS c ON c.id_cliente = p.id_cliente
INNER JOIN produtos AS pr ON pr.id_produto = i.id_produto
WHERE p.status IN ('Pago', 'Entregue')
  AND p.data_pedido BETWEEN ? AND ?
ORDER BY p.data_pedido, p.id_pedido, i.id_item
"""

SQL_PEDIDOS = """
SELECT id_pedido, id_cliente, data_pedido, status
FROM pedidos
WHERE data_pedido BETWEEN ? AND ?
ORDER BY data_pedido, id_pedido
"""


def consultar_vendas(caminho: str | Path, inicio: str, fim: str) -> pd.DataFrame:
    """Carrega apenas itens de pedidos pagos ou entregues, dentro do período."""
    with conectar(caminho) as conn:
        return pd.read_sql_query(SQL_VENDAS, conn, params=(inicio, fim))


def consultar_pedidos(caminho: str | Path, inicio: str, fim: str) -> pd.DataFrame:
    """Carrega todos os status para estudar cancelamentos e pendências."""
    with conectar(caminho) as conn:
        return pd.read_sql_query(SQL_PEDIDOS, conn, params=(inicio, fim))
