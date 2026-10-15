"""Cria documentos XML fictícios e reproduzíveis para testes e estudo."""

from __future__ import annotations

import argparse
from datetime import datetime, timedelta
from decimal import Decimal, ROUND_HALF_UP
from pathlib import Path
from random import Random
from xml.etree import ElementTree as ET

DOC_NS = "urn:projeto:documentos-fiscais:v1"
TRIB_NS = "urn:projeto:tributos-simulados:v1"
ET.register_namespace("doc", DOC_NS)
ET.register_namespace("trib", TRIB_NS)

BASE_DIR = Path(__file__).resolve().parents[1]

# Código, descrição, categoria e preço unitário fictício.
PRODUTOS = [
    ("P001", "Caderno A5", "Papelaria", "26.90"),
    ("P002", "Caneta esferográfica", "Papelaria", "4.50"),
    ("P003", "Bloco de notas", "Papelaria", "12.90"),
    ("P004", "Marcador de texto", "Papelaria", "8.40"),
    ("P005", "Mouse sem fio", "Informática", "79.90"),
    ("P006", "Teclado compacto", "Informática", "129.00"),
    ("P007", "Suporte para notebook", "Informática", "89.50"),
    ("P008", "Hub USB", "Informática", "56.90"),
    ("P009", "Organizador de mesa", "Organização", "39.90"),
    ("P010", "Pasta sanfonada", "Organização", "24.90"),
    ("P011", "Caixa organizadora", "Organização", "49.90"),
    ("P012", "Etiqueta adesiva", "Organização", "17.50"),
]
ESTADOS = ["SP", "SP", "SP", "RJ", "MG", "PR", "BA", "SC"]


def dinheiro(valor: Decimal) -> Decimal:
    return valor.quantize(Decimal("0.01"), rounding=ROUND_HALF_UP)


def subelemento(pai: ET.Element, namespace: str, tag: str, texto: object) -> ET.Element:
    filho = ET.SubElement(pai, f"{{{namespace}}}{tag}")
    filho.text = str(texto)
    return filho


def criar_nota(indice: int, rng: Random) -> ET.ElementTree:
    """Monta um documento fictício; não corresponde ao leiaute oficial da NF-e."""
    raiz = ET.Element(f"{{{DOC_NS}}}nota", {
        "id": f"NF-2026-{indice:04d}",
        "situacao": "cancelada" if rng.random() < 0.08 else "emitida",
    })
    inicio = datetime(2026, 1, 1, 8, 0)
    data = inicio + timedelta(days=rng.randrange(273), hours=rng.randrange(10), minutes=rng.randrange(60))
    subelemento(raiz, DOC_NS, "emissao", data.isoformat(timespec="seconds"))
    emitente = ET.SubElement(raiz, f"{{{DOC_NS}}}emitente", {"codigo": "EMP001"})
    subelemento(emitente, DOC_NS, "nome", "Comercial Exemplo")

    cliente = rng.randrange(1, 46)
    destinatario = ET.SubElement(raiz, f"{{{DOC_NS}}}destinatario", {"codigo": f"C{cliente:03d}"})
    subelemento(destinatario, DOC_NS, "nome", f"Cliente {cliente:03d}")
    subelemento(destinatario, DOC_NS, "uf", rng.choice(ESTADOS))

    itens = ET.SubElement(raiz, f"{{{DOC_NS}}}itens")
    total_produtos = Decimal("0")
    total_icms = Decimal("0")
    total_pis = Decimal("0")
    total_cofins = Decimal("0")

    for numero, (codigo, descricao, categoria, preco) in enumerate(
        rng.sample(PRODUTOS, k=rng.randint(1, 5)), start=1
    ):
        quantidade = rng.randint(1, 8)
        valor_unitario = Decimal(preco)
        valor_total = dinheiro(valor_unitario * quantidade)
        # Alíquotas escolhidas exclusivamente para exercício matemático.
        icms = dinheiro(valor_total * Decimal("0.12"))
        pis = dinheiro(valor_total * Decimal("0.0165"))
        cofins = dinheiro(valor_total * Decimal("0.076"))

        item = ET.SubElement(itens, f"{{{DOC_NS}}}item", {"numero": str(numero)})
        produto = ET.SubElement(item, f"{{{DOC_NS}}}produto", {
            "codigo": codigo,
            "categoria": categoria,
        })
        subelemento(produto, DOC_NS, "descricao", descricao)
        subelemento(item, DOC_NS, "quantidade", quantidade)
        subelemento(item, DOC_NS, "valor_unitario", f"{valor_unitario:.2f}")
        subelemento(item, DOC_NS, "valor_total", f"{valor_total:.2f}")
        tributos = ET.SubElement(item, f"{{{TRIB_NS}}}tributos")
        subelemento(tributos, TRIB_NS, "icms", f"{icms:.2f}")
        subelemento(tributos, TRIB_NS, "pis", f"{pis:.2f}")
        subelemento(tributos, TRIB_NS, "cofins", f"{cofins:.2f}")

        total_produtos += valor_total
        total_icms += icms
        total_pis += pis
        total_cofins += cofins

    resumo = ET.SubElement(raiz, f"{{{DOC_NS}}}resumo")
    subelemento(resumo, DOC_NS, "valor_produtos", f"{total_produtos:.2f}")
    subelemento(resumo, DOC_NS, "valor_nota", f"{total_produtos:.2f}")
    subelemento(resumo, DOC_NS, "tributos_simulados", f"{total_icms + total_pis + total_cofins:.2f}")
    return ET.ElementTree(raiz)


def gerar_base(destino: Path, quantidade: int = 240, semente: int = 2026) -> int:
    if quantidade <= 0:
        raise ValueError("A quantidade precisa ser maior que zero")
    destino.mkdir(parents=True, exist_ok=True)
    rng = Random(semente)
    for indice in range(1, quantidade + 1):
        arvore = criar_nota(indice, rng)
        arvore.write(destino / f"NF-2026-{indice:04d}.xml", encoding="utf-8", xml_declaration=True)
    return quantidade


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Gera notas fiscais fictícias em XML")
    parser.add_argument("--quantidade", type=int, default=240)
    parser.add_argument("--semente", type=int, default=2026)
    parser.add_argument("--destino", type=Path, default=BASE_DIR / "data" / "raw" / "notas")
    args = parser.parse_args()
    total = gerar_base(args.destino, args.quantidade, args.semente)
    print(f"{total} documentos XML criados em {args.destino}")
