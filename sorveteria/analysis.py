import pandas as pd
from pathlib import Path


# ==============================
# LEITURA DOS DADOS
# ==============================

dados = pd.read_csv(Path(__file__).resolve().parent / "sorveteria.csv")


def ler_csv():
    print(dados.head())


def tipos_das_colunas():
    dados.info()


# ==============================
# TRATAMENTO DOS DADOS
# ==============================

def limpar_dados():

    # Verificar valores nulos
    print(dados.isnull().sum())

    # Padronizar sabores
    dados["sabor"] = dados["sabor"].str.strip().str.lower()

    # Padronizar clima
    dados["clima"] = dados["clima"].str.strip().str.lower()


# ==============================
# ANÁLISES
# ==============================

def vendas_diarias():

    vendas_dia = dados.groupby("data").agg({
        "quantidade_vendida": "sum",
        "temperatura_c": "mean",
        "clima": "first",
        "fim_de_semana": "first",
        "feriado": "first"
    }).reset_index()

    return vendas_dia


def vendas_por_sabor():

    vendas_sabor = dados.groupby("sabor")["quantidade_vendida"].sum()

    vendas_sabor = vendas_sabor.sort_values(
        ascending=False
    )

    return vendas_sabor


def temperatura_vs_vendas():

    dados_temperatura = dados.groupby("data").agg({
        "quantidade_vendida": "sum",
        "temperatura_c": "mean"
    }).reset_index()

    return dados_temperatura


def vendas_por_clima():

    dados_diarios = vendas_diarias()

    dados_clima = (
        dados_diarios
        .groupby("clima")["quantidade_vendida"]
        .mean()
        .reset_index()
    )

    dados_clima = dados_clima.sort_values(
        by="quantidade_vendida",
        ascending=False
    )

    return dados_clima


def vendas_por_fim_de_semana():

    dados_diarios = vendas_diarias()

    dados_fim_de_semana = (
        dados_diarios
        .groupby("fim_de_semana")["quantidade_vendida"]
        .mean()
        .reset_index()
    )

    return dados_fim_de_semana


def vendas_por_feriado():

    dados_diarios = vendas_diarias()

    dados_feriado = (
        dados_diarios
        .groupby("feriado")["quantidade_vendida"]
        .mean()
        .reset_index()
    )

    return dados_feriado

