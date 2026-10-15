from analysis import (
    vendas_diarias,
    vendas_por_sabor,
    temperatura_vs_vendas,
    vendas_por_clima,
    vendas_por_fim_de_semana,
    vendas_por_feriado,
    limpar_dados
)

from visualization import (
    visualizar_vendas_por_sabor,
    visualizar_temperatura_vs_vendas,
    visualizar_vendas_por_clima,
    visualizar_vendas_por_fim_de_semana,
    visualizar_vendas_por_feriado,
    visualizar_vendas_diarias
)


def inicio(tarefa):

    limpar_dados()

    match tarefa:

        case 1:
            vendas_sabor = vendas_por_sabor()

            visualizar_vendas_por_sabor(vendas_sabor)

        case 2:
            dados_temperatura = temperatura_vs_vendas()

            visualizar_temperatura_vs_vendas(dados_temperatura)

        case 3:
            dados_clima = vendas_por_clima()

            visualizar_vendas_por_clima(dados_clima)

        case 4:
            dados_fim_de_semana = vendas_por_fim_de_semana()

            visualizar_vendas_por_fim_de_semana(dados_fim_de_semana)

        case 5:
            dados_feriado = vendas_por_feriado()

            visualizar_vendas_por_feriado(dados_feriado)

        case 6:
            print("Análises encerradas!")

            return

        case _:
            print("O valor não está entre as opções!")


while True:

    print('''

        Você foi contratado por uma sorveteria,
        pois o gerente deseja compreender:

        (1) Quais sabores são mais vendidos e quais são menos vendidos?

        (2) A temperatura influencia a quantidade de sorvetes vendidos?

        (3) O clima — ensolarado, nublado ou chuvoso —
            interfere nas vendas?

        (4) Vendemos mais nos finais de semana
            do que durante a semana?

        (5) Feriados possuem impacto significativo nas vendas?

        (6) Encerrar análises?

    ''')

    tarefa = int(input("Qual pergunta deseja analisar primeiro? "))

    inicio(tarefa)

    if tarefa == 6:
        break
