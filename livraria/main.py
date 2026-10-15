from coleta import carregar_dados
from limpar import limpar_dados
from tratar import tratar_dados
from analysis import(
    analises
) 
from visualization import(
    gerar_graficos
)

def main():
    df_raw = carregar_dados()
    df_clean = limpar_dados(df_raw)
    df_processed = tratar_dados(df_clean)

    analises(df_processed)
    gerar_graficos(df_processed)

if __name__ == "__main__":
    main()