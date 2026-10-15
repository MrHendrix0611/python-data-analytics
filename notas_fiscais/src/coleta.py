"""Leitura de documentos XML e extração de tabelas normalizadas."""

from pathlib import Path
from xml.etree.ElementTree import Element, ParseError

import pandas as pd
from defusedxml import ElementTree as ET

DOC_NS = "urn:projeto:documentos-fiscais:v1"
TRIB_NS = "urn:projeto:tributos-simulados:v1"
NS = {"doc": DOC_NS, "trib": TRIB_NS}


def _texto(elemento: Element, caminho: str) -> str:
    """Obtém texto obrigatório de um elemento dentro do XML."""
    filho = elemento.find(caminho, NS)
    if filho is None or not filho.text or not filho.text.strip():
        raise ValueError(f"Campo obrigatório ausente: {caminho}")
    return filho.text.strip()


def _atributo(elemento: Element, nome: str) -> str:
    valor = elemento.get(nome)
    if valor is None or not valor.strip():
        raise ValueError(f"Atributo obrigatório ausente: {nome}")
    return valor


def ler_nota(caminho: Path) -> tuple[dict, list[dict]]:
    """Retorna o cabeçalho de uma nota e seus itens."""
    raiz = ET.parse(caminho).getroot()
    if raiz.tag != f"{{{DOC_NS}}}nota":
        raise ValueError("Elemento raiz ou namespace inesperado")

    destinatario = raiz.find("doc:destinatario", NS)
    if destinatario is None:
        raise ValueError("Destinatário não encontrado")

    identificador = _atributo(raiz, "id")
    cabecalho = {
        "id_nota": identificador,
        "situacao": _atributo(raiz, "situacao"),
        "data_emissao": _texto(raiz, "doc:emissao"),
        "cliente_id": _atributo(destinatario, "codigo"),
        "cliente": _texto(destinatario, "doc:nome"),
        "uf": _texto(destinatario, "doc:uf"),
        "valor_produtos": _texto(raiz, "doc:resumo/doc:valor_produtos"),
        "valor_nota": _texto(raiz, "doc:resumo/doc:valor_nota"),
        "tributos_simulados": _texto(raiz, "doc:resumo/doc:tributos_simulados"),
    }

    itens = []
    for item in raiz.findall("doc:itens/doc:item", NS):
        produto = item.find("doc:produto", NS)
        if produto is None:
            raise ValueError("Produto não encontrado")
        itens.append({
            "id_nota": identificador,
            "numero_item": _atributo(item, "numero"),
            "codigo_produto": _atributo(produto, "codigo"),
            "categoria": _atributo(produto, "categoria"),
            "produto": _texto(produto, "doc:descricao"),
            "quantidade": _texto(item, "doc:quantidade"),
            "valor_unitario": _texto(item, "doc:valor_unitario"),
            "valor_total": _texto(item, "doc:valor_total"),
            "icms": _texto(item, "trib:tributos/trib:icms"),
            "pis": _texto(item, "trib:tributos/trib:pis"),
            "cofins": _texto(item, "trib:tributos/trib:cofins"),
        })
    if not itens:
        raise ValueError("Nota sem itens")
    return cabecalho, itens


def carregar_dados(diretorio: str | Path) -> dict[str, pd.DataFrame]:
    """Lê todos os arquivos XML do diretório e retorna notas e itens."""
    arquivos = sorted(Path(diretorio).glob("*.xml"))
    if not arquivos:
        raise FileNotFoundError(f"Nenhum arquivo XML em {diretorio}")

    notas, itens = [], []
    for caminho in arquivos:
        try:
            cabecalho, linhas = ler_nota(caminho)
        except (ValueError, ParseError) as erro:
            raise ValueError(f"Erro em {caminho.name}: {erro}") from erro
        notas.append(cabecalho)
        itens.extend(linhas)

    return {"notas": pd.DataFrame(notas), "itens": pd.DataFrame(itens)}
