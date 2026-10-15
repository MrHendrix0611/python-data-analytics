"""Gera uma base SQLite sintética e reproduzível para análise comercial."""

import argparse
from datetime import date, timedelta
from pathlib import Path
import random
import sqlite3

RAIZ = Path(__file__).resolve().parents[1]
CAMINHO_PADRAO = RAIZ / "data" / "raw" / "ecommerce.db"

ESQUEMA = """
PRAGMA foreign_keys = ON;
CREATE TABLE clientes (
    id_cliente INTEGER PRIMARY KEY,
    nome TEXT NOT NULL,
    estado TEXT NOT NULL,
    data_cadastro TEXT NOT NULL
);
CREATE TABLE produtos (
    id_produto INTEGER PRIMARY KEY,
    nome_produto TEXT NOT NULL,
    categoria TEXT NOT NULL,
    preco_lista_centavos INTEGER NOT NULL CHECK(preco_lista_centavos > 0),
    custo_centavos INTEGER NOT NULL CHECK(custo_centavos >= 0),
    estoque_atual INTEGER NOT NULL CHECK(estoque_atual >= 0)
);
CREATE TABLE pedidos (
    id_pedido INTEGER PRIMARY KEY,
    id_cliente INTEGER NOT NULL REFERENCES clientes(id_cliente),
    data_pedido TEXT NOT NULL,
    status TEXT NOT NULL CHECK(status IN ('Pendente','Pago','Entregue','Cancelado'))
);
CREATE TABLE itens_pedido (
    id_item INTEGER PRIMARY KEY,
    id_pedido INTEGER NOT NULL REFERENCES pedidos(id_pedido),
    id_produto INTEGER NOT NULL REFERENCES produtos(id_produto),
    quantidade INTEGER NOT NULL CHECK(quantidade > 0),
    preco_unitario_centavos INTEGER NOT NULL CHECK(preco_unitario_centavos > 0),
    desconto_unitario_centavos INTEGER NOT NULL DEFAULT 0
        CHECK(desconto_unitario_centavos >= 0
        AND desconto_unitario_centavos < preco_unitario_centavos),
    UNIQUE(id_pedido, id_produto)
);
CREATE INDEX idx_pedidos_cliente ON pedidos(id_cliente);
CREATE INDEX idx_pedidos_data_status ON pedidos(data_pedido, status);
CREATE INDEX idx_itens_pedido ON itens_pedido(id_pedido);
CREATE INDEX idx_itens_produto ON itens_pedido(id_produto);
"""

CATEGORIAS = {
    "Informática": ["Mouse sem fio", "Teclado compacto", "Webcam HD", "Hub USB", "Suporte notebook", "Mousepad"],
    "Casa": ["Luminária LED", "Organizador", "Garrafa térmica", "Relógio digital", "Almofada", "Porta-retrato"],
    "Papelaria": ["Caderno", "Caneta", "Agenda", "Estojo", "Marca-texto", "Bloco de notas"],
    "Áudio": ["Fone bluetooth", "Caixa de som", "Microfone USB", "Headset", "Adaptador áudio", "Suporte headset"],
    "Esporte": ["Corda", "Colchonete", "Bolsa esportiva", "Squeeze", "Faixa elástica", "Toalha fitness"],
    "Acessórios": ["Mochila", "Carteira", "Nécessaire", "Óculos", "Boné", "Chaveiro"],
    "Livros": ["Livro técnico", "Livro de negócios", "Livro de ficção", "Livro de história", "Livro de design", "Livro de ciências"],
    "Celulares": ["Capa protetora", "Película", "Carregador", "Cabo USB", "Suporte celular", "Power bank"],
    "Cozinha": ["Espátula", "Copo", "Pote hermético", "Jarra", "Tábua de corte", "Balança digital"],
}


def criar_base(caminho: Path = CAMINHO_PADRAO, seed: int = 2026, substituir: bool = False) -> dict:
    """Cria a base de treinamento; impede sobrescrita sem autorização explícita."""
    caminho = Path(caminho)
    caminho.parent.mkdir(parents=True, exist_ok=True)
    if caminho.exists():
        if not substituir:
            raise FileExistsError(f"O banco já existe: {caminho}. Use --force para substituir.")
        caminho.unlink()

    sorteio = random.Random(seed)
    inicio_cadastro = date(2025, 6, 1)
    inicio_pedidos = date(2026, 1, 1)
    fim_pedidos = date(2026, 9, 30)
    estados = ["SP", "RJ", "MG", "PR", "SC", "RS", "BA", "PE", "GO", "DF"]

    try:
        with sqlite3.connect(caminho) as conn:
            conn.executescript(ESQUEMA)
            clientes = []
            for id_cliente in range(1, 241):
                dt = inicio_cadastro + timedelta(days=sorteio.randint(0, 455))
                clientes.append((id_cliente, f"Cliente {id_cliente:03d}", sorteio.choice(estados), dt.isoformat()))
            conn.executemany("INSERT INTO clientes VALUES (?, ?, ?, ?)", clientes)

            produtos = []
            numero = 0
            for categoria, nomes in CATEGORIAS.items():
                for nome in nomes:
                    numero += 1
                    preco = sorteio.randrange(1800, 35001, 100)
                    custo = round(preco * sorteio.uniform(0.43, 0.76))
                    produtos.append((numero, nome, categoria, preco, custo, sorteio.randint(5, 150)))
            conn.executemany("INSERT INTO produtos VALUES (?, ?, ?, ?, ?, ?)", produtos)

            pedidos = []
            itens = []
            for id_pedido in range(1, 1001):
                dia = inicio_pedidos + timedelta(days=sorteio.randint(0, (fim_pedidos - inicio_pedidos).days))
                elegiveis = [c[0] for c in clientes if c[3] <= dia.isoformat()]
                id_cliente = sorteio.choice(elegiveis)
                status = sorteio.choices(
                    ["Pendente", "Pago", "Entregue", "Cancelado"],
                    weights=[10, 30, 52, 8], k=1
                )[0]
                pedidos.append((id_pedido, id_cliente, dia.isoformat(), status))
                for id_produto in sorteio.sample(range(1, len(produtos) + 1), sorteio.randint(1, 4)):
                    preco = produtos[id_produto - 1][3]
                    percentual = sorteio.choices([0, 0.05, 0.10, 0.15], weights=[62, 16, 14, 8], k=1)[0]
                    desconto = round(preco * percentual)
                    itens.append((len(itens) + 1, id_pedido, id_produto, sorteio.randint(1, 3), preco, desconto))
            conn.executemany("INSERT INTO pedidos VALUES (?, ?, ?, ?)", pedidos)
            conn.executemany("INSERT INTO itens_pedido VALUES (?, ?, ?, ?, ?, ?)", itens)
            erros = conn.execute("PRAGMA foreign_key_check").fetchall()
            if erros:
                raise ValueError(f"Relacionamentos inválidos: {erros}")
            conn.commit()
    except Exception:
        caminho.unlink(missing_ok=True)
        raise

    return {"clientes": len(clientes), "produtos": len(produtos), "pedidos": len(pedidos), "itens": len(itens)}


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Gerar dados comerciais de treinamento")
    parser.add_argument("--force", action="store_true", help="Substituir banco existente")
    parser.add_argument("--destino", type=Path, default=CAMINHO_PADRAO, help="Caminho do arquivo SQLite")
    argumentos = parser.parse_args()
    contagens = criar_base(argumentos.destino, substituir=argumentos.force)
    print(f"Base criada em {argumentos.destino}")
    for tabela, quantidade in contagens.items():
        print(f"  {tabela}: {quantidade}")
