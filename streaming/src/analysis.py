import pandas as pd

def calcular_metricas(df: pd.DataFrame) -> dict:
    total_clientes = len(df)
    total_churn = df["churn"].sum() #cancelamentos
    taxa_churn = (total_churn / total_clientes) * 100

    # Tempo médio de uso por status
    tempo_medio = df.groupby("churn")["tempo_uso_diario_min"].mean().to_dict()

    # Suporte chamadas por status
    suporte_medio = df.groupby("churn")["suporte_chamados"].mean().to_dict()

    # Taxa de cancelamento por plano
    churn_por_plano = df.groupby("plano_contratado")["churn"].mean() * 100

    # Frequência de motivos de cancelamento 
    motivos_count = df[df["churn"] == 1]["motivo_cancelamento"].value_counts()

    return {
        "taxa_churn": taxa_churn,
        "tempo_medio": tempo_medio,
        "suporte_medio": suporte_medio,
        "churn_por_plano": churn_por_plano,
        "motivos_count": motivos_count
    }

def exibir_relatorio(metricas: dict) -> None:
    print(f"\n============ RELATÓRIO DE ANÁLISE DE CHURN =============")
    print(f"Taxa Global de Churn: {metricas['taxa_churn']:.2f}%")
    print(f"\nTempo Médio de Uso Diário (min): ")
    print(f" - Clientes Ativos (0): {metricas['tempo_medio'][0]:.1f} min")
    print(f" - Cliente Cancelados (1): {metricas['tempo_medio'][1]:.2f} min")

    print("\nTaxa de Churn por Plano:")
    for plano, taxa in metricas['churn_por_plano'].items():
            print(f" = {plano}: {taxa:.2f}%")

    print("\nPrincipais Motivos de Cancelamento:")
    for motivo, qtd in metricas['motivos_count'].items():
        print(f" - {motivo}: {qtd} clientes")
    print("===========================================================\n")

