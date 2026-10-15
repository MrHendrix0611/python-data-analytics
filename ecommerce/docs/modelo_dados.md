# Modelo relacional — e-commerce

## Entidades

```text
clientes (1) ─── (N) pedidos (1) ─── (N) itens_pedido (N) ─── (1) produtos
```

| Tabela | Chave primária | Referências | Conteúdo |
|---|---|---|---|
| `clientes` | `id_cliente` | — | cadastro, estado, data de entrada |
| `produtos` | `id_produto` | — | nome, categoria, preço, custo, estoque |
| `pedidos` | `id_pedido` | `id_cliente` | data e status |
| `itens_pedido` | `id_item` | `id_pedido`, `id_produto` | quantidades e preços históricos |

Os valores monetários são armazenados em **centavos inteiros**. Por exemplo, `12990` corresponde a R$ 129,90.

O campo `preco_unitario_centavos` em `itens_pedido` mantém o preço efetivamente praticado, evitando alterar o histórico de vendas caso o preço de catálogo do produto mude. O custo atualmente é lido do cadastro de produtos; para análise de lucro histórico real, seria necessário registrar o custo no momento da venda.

## Regras de indicadores

- **Pedido válido para receita:** `status IN ('Pago', 'Entregue')`.
- **Receita bruta de produtos:** soma de `quantidade × preco_unitario_centavos`.
- **Desconto:** soma de `quantidade × desconto_unitario_centavos`.
- **Receita líquida de produtos:** receita bruta menos descontos; frete, impostos e devoluções não são modelados.
- **Lucro bruto estimado:** receita líquida menos custo dos produtos. Não corresponde ao lucro operacional nem ao lucro líquido contábil.
- **Ticket médio:** receita líquida ÷ número de pedidos válidos (contagem distinta de pedidos, não de itens).
- **Taxa de recompra:** compradores com dois ou mais pedidos válidos ÷ compradores com um ou mais pedidos válidos.
- **Taxa de cancelamento:** pedidos cancelados ÷ total de pedidos de todos os status no intervalo.

## Boas práticas presentes no projeto

- `FOREIGN KEY` para integridade referencial; SQLite deve receber `PRAGMA foreign_keys = ON` em cada conexão.
- `CHECK` para impedir valores negativos e status desconhecidos.
- Índices para consultas por cliente, pedido e data.
- Consultas com parâmetros `?` em vez de concatenação direta de filtros.
- Checagem de existência do banco antes de conectar. O SQLite, caso contrário, pode criar um arquivo vazio sem aviso.
- Gerador de dados em `scripts/`, separado da aplicação principal.

## Limitações dos dados sintéticos

Não há pagamentos parciais, devoluções, impostos, custos logísticos, frete ou mudanças históricas de custo. A base é educativa; quaisquer indicadores devem ser interpretados dentro dessas hipóteses.
