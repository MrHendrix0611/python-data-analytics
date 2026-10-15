import pandas as pd

def limpar_dados(df):
    #Removendo duplicatas
    df = df.drop_duplicates(subset=["id_livro"]).copy()

    #conversão de tipos numéricos
    df["preco_custo"] = pd.to_numeric(df["preco_custo"], errors="coerce")
    df["preco_venda"] = pd.to_numeric(df["preco_venda"], errors="coerce")
    df["estoque_atual"] = pd.to_numeric(df["estoque_atual"], errors="coerce").fillna(0)
    df["unidades_vendidas_mes"] = pd.to_numeric(df["unidades_vendidas_mes"], errors="coerce").fillna(0)

    return df