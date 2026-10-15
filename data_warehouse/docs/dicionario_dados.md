# Dicionário de dados

## Fontes de entrada

| Fonte | Formato | Entidade | Identificador | Finalidade |
|---|---|---|---|---|
| `data/raw/pedidos.csv` | CSV | Pedidos | `id_pedido` | Datas, clientes, canais e status |
| `data/raw/clientes.json` | JSON | Clientes | `id_cliente` | Segmento, origem, estado e cidade |
| `data/raw/catalogo_produtos.xlsx` | XLSX | Produtos | `sku` | Produto, categoria, fornecedor, preço e custo |
| `data/raw/entregas.xml` | XML | Entregas | atributo `pedido` | Prazos, status e custo de frete |
| `data/raw/operacional.db` | SQLite | Itens e pagamentos | `id_item` / `id_pedido` | Transações e pagamentos |

## Staging

As tabelas `stg_pedidos`, `stg_clientes`, `stg_produtos`, `stg_itens`, `stg_pagamentos` e `stg_entregas` representam cópias tipadas e normalizadas das fontes. A extração não elimina registros sem avisar.

## Dimensões

- `dim_tempo`: chave de data em `AAAAMMDD`, ano, mês e trimestre.
- `dim_cliente`: chave surrogate `cliente_sk` e atributos descritivos do cliente.
- `dim_produto`: chave surrogate `produto_sk`, categoria, fornecedor, custo de referência.
- `dim_canal`: chave surrogate `canal_sk`, canal de venda.

## Fatos e granularidade

- `fato_pedidos`: **uma linha por pedido**. Possui status, valor pago, frete e prazo; o frete deve ser somado nessa granularidade.
- `fato_itens_venda`: **uma linha por item de pedido**. Possui receita, desconto, quantidade e custo de produtos. Itens cancelados mantêm rastreabilidade, mas `receita_liquida_centavos` e `quantidade_vendida` são zero.
- Valores monetários: centavos inteiros. Para exibir em reais, dividir por 100.

## Regras de negócio

- Apenas pedidos `concluido` entram na receita.
- Pedido concluído exige um pagamento e uma entrega.
- Receita líquida de item = quantidade × preço unitário − desconto.
- Margem simplificada = receita líquida − custo de mercadoria − custo de frete.
- Ticket médio = receita / quantidade de pedidos concluídos.
- Rejeitar chaves duplicadas, referências inexistentes e divergência de pagamento.
- Tempo de entrega em dias = data de entrega − data do pedido.
- Dimensões são snapshots da base atual; histórico SCD tipo 2 fica fora do escopo inicial.
