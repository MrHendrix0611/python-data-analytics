"""Testes de leitura, normalização e indicadores dos atendimentos."""

import json

import pandas as pd
import pytest

from src.coleta import carregar_json, extrair_tabelas
from src.limpar import validar_e_limpar
from src.tratar import normalizar_interacoes, preparar_chamados
from src.analysis import calcular_indicadores
from src.visualization import gerar_graficos
from src.report import gerar_relatorio


def base_exemplo():
    return {
        "clientes": [
            {
                "id_cliente": "CLI-001",
                "nome": "Cliente 001",
                "segmento": "Pessoa Física",
                "chamados": [
                    {
                        "id_chamado": "CH-0001",
                        "categoria": "Cobrança",
                        "prioridade": "Média",
                        "status": "Resolvido",
                        "aberto_em": "2026-04-01T09:00:00",
                        "fechado_em": "2026-04-01T12:00:00",
                        "atendente": {"id_atendente": "AT-01", "nome": "Camila"},
                        "avaliacao": 5,
                        "reaberto": False,
                        "interacoes": [
                            {"data": "2026-04-01T09:10:00", "tipo": "mensagem_cliente", "canal": "Chat", "tempo_gasto_minutos": 0},
                            {"data": "2026-04-01T10:00:00", "tipo": "resposta_atendente", "canal": "Chat", "tempo_gasto_minutos": 8},
                        ],
                    },
                    {
                        "id_chamado": "CH-0002",
                        "categoria": "Cobrança",
                        "prioridade": "Alta",
                        "status": "Resolvido",
                        "aberto_em": "2026-04-02T10:00:00",
                        "fechado_em": "2026-04-02T14:00:00",
                        "atendente": {"id_atendente": "AT-02", "nome": "Bruno"},
                        "avaliacao": 3,
                        "reaberto": True,
                        "interacoes": [
                            {"data": "2026-04-02T10:01:00", "tipo": "mensagem_cliente", "canal": "E-mail", "tempo_gasto_minutos": 0},
                            {"data": "2026-04-02T11:00:00", "tipo": "resposta_atendente", "canal": "E-mail", "tempo_gasto_minutos": 10},
                        ],
                    },
                ],
            },
            {
                "id_cliente": "CLI-002",
                "nome": "Cliente 002",
                "segmento": "Microempresa",
                "chamados": [
                    {
                        "id_chamado": "CH-0003",
                        "categoria": "Acesso e login",
                        "prioridade": "Baixa",
                        "status": "Aberto",
                        "aberto_em": "2026-04-03T08:00:00",
                        "fechado_em": None,
                        "atendente": None,
                        "avaliacao": None,
                        "reaberto": False,
                        "interacoes": [
                            {"data": "2026-04-03T08:05:00", "tipo": "mensagem_cliente", "canal": "Portal", "tempo_gasto_minutos": 0},
                        ],
                    }
                ],
            },
        ]
    }


def executar_exemplo():
    tabelas = validar_e_limpar(extrair_tabelas(base_exemplo()))
    interacoes = normalizar_interacoes(tabelas["chamados"])
    chamados = preparar_chamados(tabelas["chamados"], interacoes, "2026-04-30")
    indicadores = calcular_indicadores(chamados, interacoes, "2026-04-30")
    return chamados, interacoes, indicadores


def test_json_aninhado_vira_tabelas():
    tabelas = extrair_tabelas(base_exemplo())
    assert len(tabelas["clientes"]) == 2
    assert len(tabelas["chamados"]) == 3
    assert "atendente.nome" in tabelas["chamados"].columns
    assert tabelas["chamados"].loc[0, "clientes.id_cliente"] == "CLI-001"


def test_explode_preserva_relacionamento():
    chamados, interacoes, _ = executar_exemplo()
    assert len(chamados) == 3
    assert len(interacoes) == 5
    assert set(interacoes["id_chamado"]) == {"CH-0001", "CH-0002", "CH-0003"}


def test_metricas_e_recorrencia():
    chamados, interacoes, indicadores = executar_exemplo()
    resumo = indicadores["resumo"]
    assert resumo["total_chamados"] == 3
    assert resumo["resolvidos"] == 2
    assert resumo["pendentes"] == 1
    assert resumo["taxa_resolucao_pct"] == pytest.approx(66.67)
    assert resumo["tempo_medio_resolucao_horas"] == pytest.approx(3.5)
    assert resumo["tempo_medio_primeira_resposta_horas"] == pytest.approx(1.0)
    assert resumo["avaliacao_media"] == pytest.approx(4.0)
    assert resumo["chamados_reabertos"] == 1
    linha = indicadores["recorrencia"].set_index("categoria").loc["Cobrança"]
    assert linha["clientes_recorrentes"] == 1
    assert linha["taxa_recorrencia_pct"] == pytest.approx(100.0)


def test_duplicacao_de_identificador_eh_rejeitada():
    tabelas = extrair_tabelas(base_exemplo())
    tabelas["chamados"].loc[1, "id_chamado"] = "CH-0001"
    with pytest.raises(ValueError, match="duplicado"):
        validar_e_limpar(tabelas)


def test_interacao_fora_do_intervalo_eh_rejeitada():
    tabelas = validar_e_limpar(extrair_tabelas(base_exemplo()))
    tabelas["chamados"].at[0, "interacoes"] = [{
        "data": "2026-04-05T12:00:00", "tipo": "resposta_atendente",
        "canal": "Chat", "tempo_gasto_minutos": 5,
    }]
    with pytest.raises(ValueError, match="posteriores ao fechamento"):
        normalizar_interacoes(tabelas["chamados"])


def test_json_invalido(tmp_path):
    caminho = tmp_path / "chamados.json"
    caminho.write_text('{"clientes": [}', encoding="utf-8")
    with pytest.raises(json.JSONDecodeError):
        carregar_json(caminho)


def test_relatorio_e_cinco_graficos(tmp_path):
    _, _, indicadores = executar_exemplo()
    caminhos = gerar_graficos(indicadores, tmp_path / "graficos")
    assert len(caminhos) == 5
    assert all(caminho.stat().st_size > 1000 for caminho in caminhos)
    destino = gerar_relatorio(indicadores, tmp_path / "relatorio.txt", "2026-04-30")
    assert "66,7%" in destino.read_text(encoding="utf-8")
