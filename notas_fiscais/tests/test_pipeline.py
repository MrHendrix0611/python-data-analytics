"""Testes de extração XML, consistência e indicadores."""

from pathlib import Path

import pandas as pd
import pytest

from src.analysis import calcular_indicadores
from src.coleta import DOC_NS, carregar_dados, ler_nota
from src.limpar import validar_e_limpar
from src.tratar import preparar_dados
from src.visualization import gerar_graficos

BASE_DIR = Path(__file__).resolve().parents[1]
PASTA_XML = BASE_DIR / "data" / "raw" / "notas"


@pytest.fixture(scope="module")
def tabelas():
    return validar_e_limpar(carregar_dados(PASTA_XML))


@pytest.fixture(scope="module")
def indicadores(tabelas):
    return calcular_indicadores(preparar_dados(tabelas))


def test_arquivos_presentes():
    assert len(list(PASTA_XML.glob("*.xml"))) == 240


def test_leitura_xml_com_namespace_e_atributos():
    nota, itens = ler_nota(PASTA_XML / "NF-2026-0001.xml")
    assert DOC_NS.startswith("urn:")
    assert nota["id_nota"] == "NF-2026-0001"
    assert nota["cliente_id"].startswith("C")
    assert len(itens) >= 1
    assert itens[0]["codigo_produto"].startswith("P")


def test_total_documentos(tabelas):
    assert len(tabelas["notas"]) == 240
    assert len(tabelas["itens"]) > len(tabelas["notas"])


def test_totais_conferem(tabelas, indicadores):
    notas = tabelas["notas"]
    total = notas.loc[notas["situacao"] == "emitida", "valor_nota"].sum()
    assert indicadores["resumo"]["faturamento"] == pytest.approx(total)
    assert indicadores["mensal"]["faturamento"].sum() == pytest.approx(total)
    assert indicadores["por_categoria"]["faturamento"].sum() == pytest.approx(total)


def test_canceladas_fora_do_faturamento(tabelas, indicadores):
    quantidade_cancelada = (tabelas["notas"]["situacao"] == "cancelada").sum()
    assert quantidade_cancelada > 0
    assert indicadores["resumo"]["notas_canceladas"] == quantidade_cancelada
    assert indicadores["resumo"]["notas_emitidas"] + quantidade_cancelada == 240


def test_identificador_duplicado(tabelas):
    alterados = {k: v.copy() for k, v in tabelas.items()}
    alterados["notas"].loc[1, "id_nota"] = alterados["notas"].iloc[0]["id_nota"]
    with pytest.raises(ValueError, match="duplicado"):
        validar_e_limpar(alterados)


def test_total_incorreto(tabelas):
    alterados = {k: v.copy() for k, v in tabelas.items()}
    alterados["itens"].loc[0, "valor_total"] += 10
    with pytest.raises(ValueError, match="inconsistente"):
        validar_e_limpar(alterados)


def test_graficos(indicadores, tmp_path):
    gerar_graficos(indicadores, tmp_path)
    assert len(list(tmp_path.glob("*.png"))) == 5


def test_tipos_normalizados(tabelas):
    assert pd.api.types.is_datetime64_any_dtype(tabelas["notas"]["data_emissao"])
    assert pd.api.types.is_numeric_dtype(tabelas["itens"]["valor_total"])
