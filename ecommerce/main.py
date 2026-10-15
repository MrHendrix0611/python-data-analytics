"""Ponto de entrada do pipeline de análise comercial."""

from pathlib import Path

from src.coleta import consultar_pedidos, consultar_vendas, ler_tabelas, verificar_integridade
from src.limpar import validar_tabelas
from src.tratar import preparar_pedidos, preparar_vendas
from src.analysis import calcular_indicadores
from src.visualization import gerar_graficos
from src.report import exportar_tabelas, gerar_relatorio

BASE_DIR = Path(__file__).resolve().parent
BANCO = BASE_DIR / "data" / "raw" / "ecommerce.db"
INICIO = "2026-01-01"
FIM = "2026-09-30"


def main() -> None:
    if not BANCO.is_file():
        raise FileNotFoundError(
            f"Base não encontrada: {BANCO}\nExecute: python scripts/gerar_base.py"
        )
    if INICIO > FIM:
        raise ValueError("A data inicial deve ser anterior ou igual à final")

    # 1. Integridade e validação
    verificar_integridade(BANCO)
    tabelas = ler_tabelas(BANCO)
    validar_tabelas(tabelas)

    # 2. Extração SQL: INNER JOIN e filtros parametrizados
    vendas_sql = consultar_vendas(BANCO, INICIO, FIM)
    pedidos_sql = consultar_pedidos(BANCO, INICIO, FIM)

    # 3. Transformação
    vendas = preparar_vendas(vendas_sql)
    pedidos = preparar_pedidos(pedidos_sql)

    # 4. KPIs
    indicadores = calcular_indicadores(vendas, pedidos, tabelas["clientes"])

    # 5. Entregáveis
    gerar_relatorio(indicadores, BASE_DIR / "outputs" / "relatorios" / "relatorio_comercial.txt")
    graficos = gerar_graficos(indicadores, BASE_DIR / "outputs" / "graficos")
    planilhas = exportar_tabelas(indicadores, BASE_DIR / "data" / "processed")
    print(f"\nConcluído: {len(graficos)} gráficos e {len(planilhas)} tabelas exportadas.")


if __name__ == "__main__":
    main()
