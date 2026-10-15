"""Leitura de arquivos JSON e normalização dos registros de atendimento."""

import json
from pathlib import Path

import pandas as pd


def carregar_json(caminho: str | Path) -> dict:
    """Lê um arquivo JSON e retorna seu conteúdo como dicionário."""
    with Path(caminho).open("r", encoding="utf-8") as arquivo:
        dados = json.load(arquivo)

    if not isinstance(dados, dict) or not isinstance(dados.get("clientes"), list):
        raise ValueError("O JSON deve conter um objeto com a lista 'clientes'.")

    return dados


def extrair_tabelas(dados: dict) -> dict[str, pd.DataFrame]:
    """Transforma clientes e chamados aninhados em dois DataFrames."""
    if not dados["clientes"]:
        raise ValueError("A base não contém clientes.")

    clientes = pd.json_normalize(dados["clientes"], sep=".")
    clientes = clientes.drop(columns=["chamados"], errors="ignore")

    chamados = pd.json_normalize(
        dados,
        record_path=["clientes", "chamados"],
        meta=[
            ["clientes", "id_cliente"],
            ["clientes", "nome"],
            ["clientes", "segmento"],
        ],
        sep=".",
    )

    if chamados.empty:
        raise ValueError("A base não contém chamados.")

    return {"clientes": clientes, "chamados": chamados}
