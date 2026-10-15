-- Execute com um cliente SQLite ou extensão SQLite do editor.
-- 1) Relacionar as quatro tabelas (JOIN)
SELECT p.id_pedido, c.nome AS cliente, c.estado,
       pr.nome_produto AS produto, i.quantidade,
       i.quantidade * (i.preco_unitario_centavos - i.desconto_unitario_centavos) AS receita_centavos
FROM pedidos p
JOIN clientes c ON c.id_cliente = p.id_cliente
JOIN itens_pedido i ON i.id_pedido = p.id_pedido
JOIN produtos pr ON pr.id_produto = i.id_produto
WHERE p.status IN ('Pago', 'Entregue')
ORDER BY p.data_pedido, p.id_pedido
LIMIT 20;

-- 2) Faturamento líquido por categoria (pedidos válidos)
SELECT pr.categoria,
       SUM(i.quantidade * (i.preco_unitario_centavos - i.desconto_unitario_centavos))/100.0 AS faturamento_reais
FROM itens_pedido i
JOIN pedidos p ON p.id_pedido = i.id_pedido
JOIN produtos pr ON pr.id_produto = i.id_produto
WHERE p.status IN ('Pago', 'Entregue')
GROUP BY pr.categoria
ORDER BY faturamento_reais DESC;

-- 3) Top 10 clientes por número de pedidos concluídos
SELECT c.id_cliente, c.nome,
       COUNT(DISTINCT p.id_pedido) AS pedidos_validos
FROM clientes c
LEFT JOIN pedidos p
  ON p.id_cliente = c.id_cliente
 AND p.status IN ('Pago', 'Entregue')
GROUP BY c.id_cliente, c.nome
ORDER BY pedidos_validos DESC, c.id_cliente
LIMIT 10;

-- 4) Clientes sem pedido concluído (LEFT JOIN)
SELECT c.id_cliente, c.nome, c.estado
FROM clientes c
LEFT JOIN pedidos p
  ON p.id_cliente = c.id_cliente
 AND p.status IN ('Pago', 'Entregue')
WHERE p.id_pedido IS NULL
ORDER BY c.id_cliente;

-- 5) Receita mensal por pedido realizado
SELECT substr(p.data_pedido, 1, 7) AS mes,
       COUNT(DISTINCT p.id_pedido) AS pedidos,
       SUM(i.quantidade * (i.preco_unitario_centavos - i.desconto_unitario_centavos))/100.0 AS receita_reais
FROM pedidos p
JOIN itens_pedido i ON i.id_pedido = p.id_pedido
WHERE p.status IN ('Pago', 'Entregue')
GROUP BY substr(p.data_pedido, 1, 7)
ORDER BY mes;

-- 6) Recompra utilizando CTE
WITH compras AS (
    SELECT id_cliente, COUNT(*) AS qtd_pedidos
    FROM pedidos
    WHERE status IN ('Pago', 'Entregue')
    GROUP BY id_cliente
)
SELECT COUNT(*) AS compradores,
       SUM(CASE WHEN qtd_pedidos >= 2 THEN 1 ELSE 0 END) AS recorrentes,
       ROUND(100.0 * SUM(CASE WHEN qtd_pedidos >= 2 THEN 1 ELSE 0 END)/COUNT(*), 2) AS taxa_recompra_pct
FROM compras;

-- 7) Integridade referencial
PRAGMA foreign_key_check;
