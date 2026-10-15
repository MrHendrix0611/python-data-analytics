import pandas as pd

def tratar_dados(df: pd.DataFrame) -> pd.DataFrame:
    df_tratado = df.copy()

    # 1. preenchimento de tempo de uso diário pela mediana
    meidana_tempo = df_tratado["tempo_uso_diario_min"].median()
    df_tratado["tempo_uso_diario_min"] = df_tratado["tempo_uso_diario_min"].fillna(meidana_tempo)

    # 2. Preenchimento de plano_contratado pela moda
    moda_plano = df_tratado["plano_contratado"].mode()[0]
    df_tratado["plano_contratado"] = df_tratado["plano_contratado"].fillna(moda_plano)

    print("[LOG] Tratamento de dados concluido com sucesso.")
    return df_tratado

