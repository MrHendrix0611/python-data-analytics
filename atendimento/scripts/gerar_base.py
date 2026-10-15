"""Gera a base fictícia de clientes e chamados com resultados reproduzíveis."""

import json
import random
from datetime import datetime, timedelta
from pathlib import Path

SEMENTE = 2026
CORTE = datetime(2026, 9, 30, 23, 59, 59)
INICIO = datetime(2026, 1, 3, 8, 0)
ATENDENTES = [
    ("AT-01", "Camila"),
    ("AT-02", "Bruno"),
    ("AT-03", "Lara"),
    ("AT-04", "Diego"),
    ("AT-05", "Rafaela"),
    ("AT-06", "Pedro"),
]
CATEGORIAS = [
    "Acesso e login", "Cobrança", "Erro na plataforma",
    "Cadastro", "Integração", "Solicitação de recurso",
]
PRIORIDADES = ["Baixa", "Média", "Alta", "Crítica"]
CANAIS = ["Chat", "E-mail", "Portal", "Telefone"]


def sortear_abertura(gerador: random.Random) -> datetime:
    margem = int((CORTE - INICIO - timedelta(days=3)).total_seconds())
    return INICIO + timedelta(seconds=gerador.randrange(margem))


def gerar_base() -> dict:
    rng = random.Random(SEMENTE)
    clientes = []
    proximo_chamado = 1

    for indice in range(1, 91):
        chamadas = []
        categorias_anteriores = []
        quantidade = rng.choices([1, 2, 3, 4, 5], weights=[14, 27, 28, 22, 9])[0]

        for _ in range(quantidade):
            categoria = (
                rng.choice(categorias_anteriores)
                if categorias_anteriores and rng.random() < 0.52
                else rng.choice(CATEGORIAS)
            )
            categorias_anteriores.append(categoria)
            aberto = sortear_abertura(rng)
            duracao = timedelta(hours=rng.randint(5, 90), minutes=rng.randint(0, 59))
            previsto = aberto + duracao
            resolvido = previsto <= CORTE and rng.random() < 0.81
            status = "Resolvido" if resolvido else rng.choice(["Aberto", "Em andamento"])
            fechado = previsto if resolvido else None
            agente = rng.choice(ATENDENTES) if status != "Aberto" or rng.random() < 0.65 else None
            agente_obj = (
                {"id_atendente": agente[0], "nome": agente[1]}
                if agente else None
            )
            canal = rng.choice(CANAIS)
            interacoes = [{
                "data": (aberto + timedelta(minutes=rng.randint(0, 15))).isoformat(),
                "tipo": "mensagem_cliente",
                "canal": canal,
                "tempo_gasto_minutos": 0,
            }]

            if agente:
                resposta = aberto + timedelta(
                    hours=rng.randint(0, 3), minutes=rng.randint(0, 59)
                )
                if resposta <= CORTE and (fechado is None or resposta < fechado):
                    interacoes.append({
                        "data": resposta.isoformat(),
                        "tipo": "resposta_atendente",
                        "canal": canal,
                        "tempo_gasto_minutos": rng.randint(4, 28),
                    })
                    if fechado is not None:
                        nota = resposta + (fechado - resposta) / 2
                        interacoes.append({
                            "data": nota.isoformat(),
                            "tipo": "nota_interna",
                            "canal": "Portal",
                            "tempo_gasto_minutos": rng.randint(3, 16),
                        })
                        interacoes.append({
                            "data": (fechado - timedelta(minutes=5)).isoformat(),
                            "tipo": "resposta_atendente",
                            "canal": canal,
                            "tempo_gasto_minutos": rng.randint(2, 12),
                        })

            interacoes.sort(key=lambda item: item["data"])
            reaberto = bool(resolvido and rng.random() < 0.09)
            avaliacao = (
                rng.choices([1, 2, 3, 4, 5], weights=[4, 7, 13, 36, 40])[0]
                if resolvido and rng.random() < 0.86 else None
            )

            chamadas.append({
                "id_chamado": f"CH-{proximo_chamado:04d}",
                "categoria": categoria,
                "prioridade": rng.choices(PRIORIDADES, weights=[23, 48, 23, 6])[0],
                "status": status,
                "aberto_em": aberto.isoformat(),
                "fechado_em": fechado.isoformat() if fechado else None,
                "atendente": agente_obj,
                "avaliacao": avaliacao,
                "reaberto": reaberto,
                "interacoes": interacoes,
            })
            proximo_chamado += 1

        clientes.append({
            "id_cliente": f"CLI-{indice:03d}",
            "nome": f"Cliente {indice:03d}",
            "segmento": rng.choices(
                ["Pessoa Física", "Microempresa", "Empresa"],
                weights=[50, 32, 18],
            )[0],
            "chamados": chamadas,
        })

    return {
        "empresa": "Suporte Exemplo",
        "data_referencia": "2026-09-30",
        "descricao": "Registros fictícios de atendimento ao cliente",
        "clientes": clientes,
    }


def main():
    destino = Path(__file__).resolve().parents[1] / "data" / "raw" / "chamados.json"
    destino.parent.mkdir(parents=True, exist_ok=True)
    destino.write_text(
        json.dumps(gerar_base(), ensure_ascii=False, indent=2) + "\n",
        encoding="utf-8",
    )
    print(f"Base gravada em: {destino}")


if __name__ == "__main__":
    main()
