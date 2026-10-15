"""Executa o fluxo completo de análise de atendimentos."""

from pathlib import Path

from src.coleta import carregar_json, extrair_tabelas
from src.limpar import validar_e_limpar
from src.tratar import normalizar_interacoes, preparar_chamados
from src.analysis import calcular_indicadores
from src.visualization import gerar_graficos
from src.report import gerar_relatorio

BASE_DIR = Path(__file__).resolve().parent
ARQUIVO_JSON = BASE_DIR / "data" / "raw" / "chamados.json"
DATA_REFERENCIA = "2026-09-30"


def main() -> None:
    dados = carregar_json(ARQUIVO_JSON)
    tabelas = validar_e_limpar(extrair_tabelas(dados))

    interacoes = normalizar_interacoes(tabelas["chamados"])
    chamados = preparar_chamados(
        tabelas["chamados"], interacoes, DATA_REFERENCIA
    )

    indicadores = calcular_indicadores(
        chamados, interacoes, DATA_REFERENCIA
    )

    pasta_processados = BASE_DIR / "data" / "processed"
    pasta_processados.mkdir(parents=True, exist_ok=True)
    chamados.to_csv(pasta_processados / "chamados.csv", index=False)
    interacoes.to_csv(pasta_processados / "interacoes.csv", index=False)

    arquivo_relatorio = gerar_relatorio(
        indicadores,
        BASE_DIR / "outputs" / "relatorios" / "relatorio.txt",
        DATA_REFERENCIA,
    )
    graficos = gerar_graficos(
        indicadores, BASE_DIR / "outputs" / "graficos"
    )
    print(f"\nRelatório salvo em: {arquivo_relatorio}")
    print(f"Gráficos gerados: {len(graficos)}")
    print("Tabelas normalizadas: data/processed/")


if __name__ == "__main__":
    main()
