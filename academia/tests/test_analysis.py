
import pandas as pd
import pytest

from src.limpar import validar_e_limpar
from src.tratar import preparar_pagamentos
from src.analysis import calcular_indicadores


def exemplo():
    return {
        "Alunos": pd.DataFrame({
            "id_aluno": ["A1", "A2"],
            "nome_aluno": ["Ana", "Bia"],
            "data_matricula": ["2026-01-01", "2026-01-05"],
            "data_cancelamento": [None, "2026-01-16"],
            "id_plano": [1, 2],
        }),
        "Planos": pd.DataFrame({
            "id_plano": [1, 2],
            "nome_plano": ["Essencial", "Plus"],
            "valor_mensal": [100, 200],
        }),
        "Pagamentos": pd.DataFrame({
            "id_pagamento": ["P1", "P2"],
            "id_aluno": ["A1", "A2"],
            "competencia": ["2026-01-01", "2026-01-01"],
            "data_vencimento": ["2026-01-10", "2026-01-10"],
            "data_pagamento": ["2026-01-09", None],
            "valor_cobrado": [100, 200],
            "valor_pago": [100, 0],
        }),
    }


def test_indicadores():
    dados = validar_e_limpar(exemplo())

    pagamentos = preparar_pagamentos(
        dados,
        "2026-01-31"
    )

    indicadores = calcular_indicadores(
        pagamentos,
        dados["Alunos"]
    )

    resumo = indicadores["resumo"]

    assert resumo["receita_recebida"] == 100
    assert resumo["valor_vencido"] == 200

    assert resumo["taxa_inadimplencia"] == pytest.approx(
        66.6667, rel=1e-4
    )

    assert resumo["alunos_ativos_final"] == 1
    assert resumo["matriculas_periodo"] == 2
    assert resumo["cancelamentos_periodo"] == 1


def test_ids_duplicados():
    dados = exemplo()
    dados["Alunos"].loc[1, "id_aluno"] = "A1"

    with pytest.raises(ValueError, match="duplicada"):
        validar_e_limpar(dados)
