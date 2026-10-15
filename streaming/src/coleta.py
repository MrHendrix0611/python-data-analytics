import pandas as pd

def carregar_dados(caminho : str) -> pd.DataFrame:
    try:
        df = pd.read_csv(caminho)
        print(f"[LOG] Dados carregados com sucesso: {len(df)} registros.")
        return df
    except Exception as e:
        print(f"[ERRO] Falha ao carregar o arquivo: {e}")
        raise

    