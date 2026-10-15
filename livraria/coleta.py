import json
import pandas as pd
from pathlib import Path

def carregar_dados(caminho="livraria_vendas.json"):
    with open(Path(__file__).resolve().parent / caminho, "r", encoding="utf-8") as file:
        dados = json.load(file)

    df = pd.DataFrame(dados["catalogo_de_vendas"])
    return df