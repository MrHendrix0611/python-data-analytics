import pandas as pd

def tratar_dados(df):
    df_tratado = df.copy()

    #Média de avaliações por livro
    df_tratado["avaliacao_media"] = df_tratado["avaliacoes_clientes"].apply(
        lambda lista: round(sum(lista) / len(lista), 2) if isinstance(lista, list) and len(lista) > 0 else 0
    )

    #Métricas financeiras por livro
    df_tratado["receita_total"] = df_tratado["preco_venda"] * df_tratado["unidades_vendidas_mes"]
    df_tratado["custo_total"] = df_tratado["preco_custo"] * df_tratado["unidades_vendidas_mes"]
    df_tratado["lucro_total"] = df_tratado["receita_total"] - df_tratado["custo_total"]

    return df_tratado

