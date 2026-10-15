"""Ponto de entrada do projeto de análise de documentos fiscais."""

from pathlib import Path

from src.analysis import calcular_indicadores
from src.coleta import carregar_dados
from src.limpar import validar_e_limpar
from src.report import gerar_relatorio
from src.tratar import preparar_dados
from src.visualization import gerar_graficos

BASE_DIR = Path(__file__).resolve().parent
ORIGEM = BASE_DIR / "data" / "raw" / "notas"
PROCESSADOS = BASE_DIR / "data" / "processed"
SAIDA = BASE_DIR / "outputs"


def main() -> None:
    print("1/5 - Lendo arquivos XML...")
    brutos = carregar_dados(ORIGEM)

    print("2/5 - Validando os dados...")
    limpos = validar_e_limpar(brutos)

    print("3/5 - Consolidando notas e itens...")
    tratados = preparar_dados(limpos)
    PROCESSADOS.mkdir(parents=True, exist_ok=True)
    tratados["notas_todas"].to_csv(PROCESSADOS / "notas.csv", index=False, encoding="utf-8-sig")
    tratados["itens_todos"].to_csv(PROCESSADOS / "itens.csv", index=False, encoding="utf-8-sig")

    print("4/5 - Calculando indicadores...")
    indicadores = calcular_indicadores(tratados)

    print("5/5 - Gerando gráficos e relatório...\n")
    gerar_graficos(indicadores, SAIDA / "graficos")
    gerar_relatorio(indicadores, SAIDA / "relatorios" / "relatorio.txt")
    print("\nConcluído. Confira data/processed/ e outputs/.")


if __name__ == "__main__":
    main()
