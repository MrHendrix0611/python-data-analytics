
from pathlib import Path

from src.coleta import carregar_dados
from src.limpar import validar_e_limpar
from src.tratar import preparar_pagamentos
from src.analysis import calcular_indicadores
from src.visualization import gerar_graficos
from src.report import gerar_relatorio


BASE_DIR = Path(__file__).resolve().parent

CAMINHO = BASE_DIR / "data" / "raw" / "academia.xlsx"

DATA_REFERENCIA = "2026-09-30"


def main():

    if not CAMINHO.is_file():
        print(f"Arquivo não encontrado: {CAMINHO}")
        return

    # 1. Coleta
    dados_brutos = carregar_dados(CAMINHO)

    # 2. Limpeza e validação
    dados_limpos = validar_e_limpar(dados_brutos)

    # 3. Tratamento
    pagamentos = preparar_pagamentos(
        dados_limpos,
        DATA_REFERENCIA
    )

    # 4. Análise
    indicadores = calcular_indicadores(
        pagamentos,
        dados_limpos["Alunos"]
    )

    # 5. Relatório
    gerar_relatorio(
        indicadores,
        BASE_DIR / "outputs" / "relatorios" / "relatorio.txt"
    )

    # 6. Visualização
    gerar_graficos(
        indicadores,
        BASE_DIR / "outputs" / "graficos"
    )

    print("\nGráficos salvos em outputs/graficos/")


if __name__ == "__main__":
    main()
