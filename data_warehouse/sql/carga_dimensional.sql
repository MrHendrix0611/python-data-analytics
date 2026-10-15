-- Staging -> modelo estrela
INSERT INTO dim_cliente(id_cliente,nome,segmento,origem,uf,cidade)
SELECT id_cliente,nome,segmento,origem,uf,cidade FROM stg_clientes ORDER BY id_cliente;

INSERT INTO dim_produto(sku,produto,categoria,fornecedor,preco_tabela_centavos,custo_unit_centavos)
SELECT sku,produto,categoria,fornecedor,preco_centavos,custo_centavos FROM stg_produtos ORDER BY sku;

INSERT INTO dim_canal(canal)
SELECT DISTINCT canal FROM stg_pedidos ORDER BY canal;

INSERT INTO dim_tempo(data_sk,data_iso,ano,mes,trimestre)
SELECT DISTINCT CAST(REPLACE(data_pedido,'-','') AS INTEGER),data_pedido,
       CAST(strftime('%Y',data_pedido) AS INTEGER),
       CAST(strftime('%m',data_pedido) AS INTEGER),
       (CAST(strftime('%m',data_pedido) AS INTEGER)+2)/3
FROM stg_pedidos ORDER BY data_pedido;

INSERT INTO fato_pedidos(
    id_pedido,data_sk,cliente_sk,canal_sk,status,quantidade_itens,
    valor_pago_centavos,frete_centavos,metodo_pagamento,prazo_entrega_dias
)
SELECT p.id_pedido,t.data_sk,c.cliente_sk,ca.canal_sk,p.status,
       (SELECT COALESCE(SUM(i.quantidade),0) FROM stg_itens i WHERE i.id_pedido=p.id_pedido),
       COALESCE(pg.valor_pago_centavos,0),COALESCE(e.frete_centavos,0),pg.metodo,
       CASE WHEN e.data_entrega IS NULL THEN NULL
            ELSE CAST(julianday(e.data_entrega)-julianday(p.data_pedido) AS INTEGER) END
FROM stg_pedidos p
JOIN dim_tempo t ON t.data_iso=p.data_pedido
JOIN dim_cliente c ON c.id_cliente=p.id_cliente
JOIN dim_canal ca ON ca.canal=p.canal
LEFT JOIN stg_pagamentos pg ON pg.id_pedido=p.id_pedido
LEFT JOIN stg_entregas e ON e.id_pedido=p.id_pedido;

INSERT INTO fato_itens_venda(
    id_item,id_pedido,data_sk,cliente_sk,produto_sk,canal_sk,
    quantidade_pedida,quantidade_vendida,receita_bruta_centavos,
    desconto_centavos,receita_liquida_centavos,custo_centavos
)
SELECT i.id_item,p.id_pedido,f.data_sk,f.cliente_sk,dp.produto_sk,f.canal_sk,
       i.quantidade,CASE WHEN p.status='concluido' THEN i.quantidade ELSE 0 END,
       CASE WHEN p.status='concluido' THEN i.quantidade*i.preco_unit_centavos ELSE 0 END,
       CASE WHEN p.status='concluido' THEN i.desconto_centavos ELSE 0 END,
       CASE WHEN p.status='concluido' THEN i.quantidade*i.preco_unit_centavos-i.desconto_centavos ELSE 0 END,
       CASE WHEN p.status='concluido' THEN i.quantidade*dp.custo_unit_centavos ELSE 0 END
FROM stg_itens i
JOIN stg_pedidos p ON p.id_pedido=i.id_pedido
JOIN fato_pedidos f ON f.id_pedido=p.id_pedido
JOIN dim_produto dp ON dp.sku=i.sku;
