-- Execute estas consultas sobre warehouse/retail_dw.db (NÃO no operacional.db).
-- 1) Faturamento total e quantidade de pedidos concluídos
SELECT SUM(valor_pago_centavos)/100.0 AS receita,
       COUNT(*) AS pedidos
FROM fato_pedidos WHERE status='concluido';

-- 2) Receita por mês (modelo estrela)
SELECT t.ano,t.mes,SUM(f.receita_liquida_centavos)/100.0 AS receita
FROM fato_itens_venda f JOIN dim_tempo t ON t.data_sk=f.data_sk
GROUP BY t.ano,t.mes ORDER BY t.ano,t.mes;

-- 3) Produtos de maior receita
SELECT p.produto,SUM(f.receita_liquida_centavos)/100.0 AS receita
FROM fato_itens_venda f JOIN dim_produto p ON p.produto_sk=f.produto_sk
GROUP BY p.produto ORDER BY receita DESC LIMIT 10;

-- 4) Clientes com mais de três compras concluídas
SELECT c.id_cliente,c.nome,COUNT(*) AS pedidos
FROM fato_pedidos f JOIN dim_cliente c ON c.cliente_sk=f.cliente_sk
WHERE f.status='concluido'
GROUP BY c.id_cliente,c.nome HAVING COUNT(*)>3 ORDER BY pedidos DESC;

-- 5) Reconciliar duas granularidades (esperado: diferença zero)
SELECT
(SELECT SUM(valor_pago_centavos) FROM fato_pedidos)
-
(SELECT SUM(receita_liquida_centavos) FROM fato_itens_venda)
AS diferenca_centavos;
