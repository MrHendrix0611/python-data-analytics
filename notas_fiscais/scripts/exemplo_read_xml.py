"""Exemplo de extração tabular por XPath com pandas.read_xml."""

from pathlib import Path
import pandas as pd

BASE_DIR = Path(__file__).resolve().parents[1]
arquivo = BASE_DIR / "data" / "raw" / "notas" / "NF-2026-0001.xml"

# Com elementos aninhados, read_xml() não produz automaticamente
# uma tabela plana com todas as informações do produto e impostos.
# Veja src/coleta.py para a extração completa de notas e itens.
itens = pd.read_xml(
    arquivo,
    xpath=".//doc:item",
    namespaces={"doc": "urn:projeto:documentos-fiscais:v1"},
)
print("Itens extraídos diretamente (observe os campos aninhados):")
print(itens.head())

resumo = pd.read_xml(
    arquivo,
    xpath=".//doc:resumo",
    namespaces={"doc": "urn:projeto:documentos-fiscais:v1"},
)
print("\nResumo da nota com campos diretos:")
print(resumo.head())
print("\nPara extrair atributos e campos aninhados, confira src/coleta.py.")
