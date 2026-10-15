PRAGMA foreign_keys = ON;
CREATE TABLE dim_tempo (
    data_sk INTEGER PRIMARY KEY, data_iso TEXT NOT NULL UNIQUE,
    ano INTEGER NOT NULL, mes INTEGER NOT NULL, trimestre INTEGER NOT NULL
);
CREATE TABLE dim_cliente (
    cliente_sk INTEGER PRIMARY KEY AUTOINCREMENT,
    id_cliente TEXT NOT NULL UNIQUE, nome TEXT NOT NULL,
    segmento TEXT NOT NULL, origem TEXT NOT NULL, uf TEXT NOT NULL, cidade TEXT NOT NULL
);
CREATE TABLE dim_produto (
    produto_sk INTEGER PRIMARY KEY AUTOINCREMENT,
    sku TEXT NOT NULL UNIQUE, produto TEXT NOT NULL,
    categoria TEXT NOT NULL, fornecedor TEXT NOT NULL,
    preco_tabela_centavos INTEGER NOT NULL, custo_unit_centavos INTEGER NOT NULL
);
CREATE TABLE dim_canal (
    canal_sk INTEGER PRIMARY KEY AUTOINCREMENT, canal TEXT NOT NULL UNIQUE
);
-- Grão: uma linha por pedido, mesmo quando há vários itens.
CREATE TABLE fato_pedidos (
    id_pedido TEXT PRIMARY KEY, data_sk INTEGER NOT NULL,
    cliente_sk INTEGER NOT NULL, canal_sk INTEGER NOT NULL,
    status TEXT NOT NULL CHECK(status IN ('concluido','cancelado')),
    quantidade_itens INTEGER NOT NULL, valor_pago_centavos INTEGER NOT NULL,
    frete_centavos INTEGER NOT NULL, metodo_pagamento TEXT,
    prazo_entrega_dias INTEGER,
    FOREIGN KEY(data_sk) REFERENCES dim_tempo(data_sk),
    FOREIGN KEY(cliente_sk) REFERENCES dim_cliente(cliente_sk),
    FOREIGN KEY(canal_sk) REFERENCES dim_canal(canal_sk)
);
-- Grão: uma linha por item do pedido (não somar frete aqui!).
CREATE TABLE fato_itens_venda (
    id_item TEXT PRIMARY KEY, id_pedido TEXT NOT NULL,
    data_sk INTEGER NOT NULL, cliente_sk INTEGER NOT NULL,
    produto_sk INTEGER NOT NULL, canal_sk INTEGER NOT NULL,
    quantidade_pedida INTEGER NOT NULL, quantidade_vendida INTEGER NOT NULL,
    receita_bruta_centavos INTEGER NOT NULL, desconto_centavos INTEGER NOT NULL,
    receita_liquida_centavos INTEGER NOT NULL, custo_centavos INTEGER NOT NULL,
    FOREIGN KEY(id_pedido) REFERENCES fato_pedidos(id_pedido),
    FOREIGN KEY(data_sk) REFERENCES dim_tempo(data_sk),
    FOREIGN KEY(cliente_sk) REFERENCES dim_cliente(cliente_sk),
    FOREIGN KEY(produto_sk) REFERENCES dim_produto(produto_sk),
    FOREIGN KEY(canal_sk) REFERENCES dim_canal(canal_sk)
);
CREATE INDEX idx_fato_itens_tempo ON fato_itens_venda(data_sk);
CREATE INDEX idx_fato_itens_produto ON fato_itens_venda(produto_sk);
CREATE INDEX idx_fato_pedidos_cliente ON fato_pedidos(cliente_sk);
