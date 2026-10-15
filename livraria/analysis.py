def analises(df):
    print("=" * 50)
    print("RELATÓRIO DE ANÁLISE DE VENDAS E ESTOQUE")
    print("=" * 50)
    
    # 1. Receita Bruta Total
    receita_total = df["receita_total"].sum()
    print(f"\n1. Receita Bruta Total: R$ {receita_total:,.2f}")
    
    # 2. Lucro Total e Margem Geral
    lucro_total = df["lucro_total"].sum()
    custo_total = df["custo_total"].sum()
    margem_geral = (lucro_total / receita_total) * 100 if receita_total > 0 else 0
    print(f"2. Lucro Total: R$ {lucro_total:,.2f} | Margem Geral: {margem_geral:.2f}%")
    
    # 3. Desempenho por Categoria
    cat_desempenho = df.groupby("categoria").agg(
        receita=("receita_total", "sum"),
        lucro=("lucro_total", "sum")
    )
    top_receita = cat_desempenho["receita"].idxmax()
    top_lucro = cat_desempenho["lucro"].idxmax()
    print(f"3. Categoria com Maior Receita: {top_receita} (R$ {cat_desempenho.loc[top_receita, 'receita']:,.2f})")
    print(f"   Categoria com Maior Lucro: {top_lucro} (R$ {cat_desempenho.loc[top_lucro, 'lucro']:,.2f})")
    
    # 4. Alerta de Estoque Crítico (< 10)
    estoque_critico = df[df["estoque_atual"] < 10][["titulo", "estoque_atual"]]
    print(f"\n4. Alerta de Estoque Crítico ({len(estoque_critico)} livros):")
    print(estoque_critico.to_string(index=False))
    
    # 5. Avaliação x Vendas
    correlacao = df["avaliacao_media"].corr(df["unidades_vendidas_mes"])
    print(f"\n5. Correlação entre Nota Média e Vendas: {correlacao:.2f}")
    print("=" * 50)