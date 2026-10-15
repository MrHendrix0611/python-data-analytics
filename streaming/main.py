from pathlib import Path
from src.coleta import carregar_dados
from src.limpar import verificar_nulos_e_duplicados
from src.tratar import tratar_dados
from src.analysis import calcular_metricas, exibir_relatorio
from src.visualization import gerar_graficos

def main():
    caminho = Path(__file__).resolve().parent / "data" / "streaming_churn.csv"

    df_raw = carregar_dados(caminho)
    verificar_nulos_e_duplicados(df_raw)
    df_tratado = tratar_dados(df_raw)
    metricas = calcular_metricas(df_tratado)
    exibir_relatorio(metricas)
    gerar_graficos(df_tratado)

if __name__ == "__main__":
    main()