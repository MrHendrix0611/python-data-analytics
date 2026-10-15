import pandas as pd

def verificar_nulos_e_duplicados(df: pd.DataFrame) -> None:
    print("\n---DIAGNÓSTICO DE DADOS---")
    print(f"Linhas duplicadas: {df.duplicated().sum()}")
    print(df.isnull().sum())
    print("-" * 30)