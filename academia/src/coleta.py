import pandas as pd

def carregar_dados(caminho: str) -> dict:
    """
    Carrega todas as abas de um arquivo Excel.

    Args:
        caminho: Caminho do arquivo XLSX.

    Returns:
        Dicionário contendo as abas e seus DataFrames.
    """

    try:
        dados = pd.read_excel(
            caminho, 
            sheet_name = None
        )

        return dados
    
    except FileNotFoundError:
        print(f"Arquivo não encontrado: {caminho}")
        raise

    except Exception as erro:
        print(f"Erro ao carregar dados: {erro}")
        raise

    
