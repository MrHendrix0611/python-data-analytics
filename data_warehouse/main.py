"""Pipeline local: fontes -> staging -> warehouse dimensional -> relatórios."""
from pathlib import Path
from src.coleta import carregar_fontes
from src.qualidade import validar_fontes
from src.warehouse import construir_warehouse
from src.analysis import executar_analises
from src.visualization import criar_graficos
from src.report import gerar_relatorio,real

ROOT=Path(__file__).resolve().parent


def main()->None:
    print('[1/6] Extraindo dados CSV, XLSX, JSON, XML e SQLite...')
    fontes=carregar_fontes(ROOT/'data'/'raw')

    print('[2/6] Aplicando contrato de qualidade e integridade...')
    dados=validar_fontes(fontes)

    print('[3/6] Publicando staging e modelo estrela no warehouse...')
    warehouse=ROOT/'warehouse'/'retail_dw.db'
    contagens=construir_warehouse(dados,warehouse,ROOT/'sql')

    print('[4/6] Executando consultas de análise...')
    tabelas,resumo=executar_analises(warehouse)

    print('[5/6] Exportando data marts CSV e relatório...')
    processed=ROOT/'data'/'processed';processed.mkdir(parents=True,exist_ok=True)
    for nome,df in tabelas.items():
        df.to_csv(processed/f'mart_{nome}.csv',index=False,encoding='utf-8-sig')
    gerar_relatorio(resumo,tabelas,ROOT/'outputs'/'relatorios'/'relatorio_gerencial.md')

    print('[6/6] Criando gráficos...')
    criar_graficos(tabelas,ROOT/'outputs'/'graficos')

    print('\nPIPELINE FINALIZADO')
    print('Warehouse:',warehouse)
    print('Tabelas dimensionais/fatos:',contagens)
    print('Pedidos:',resumo['pedidos'],'| concluídos:',resumo['concluidos'])
    print('Receita:',real(resumo['receita']))
    print('Margem simplificada:',real(resumo['margem_contribuicao']))
    print('Exportações:',len(tabelas),'data marts CSV + 5 gráficos + relatório Markdown')

if __name__=='__main__':
    main()
