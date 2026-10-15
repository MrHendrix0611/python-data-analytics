"""Gráficos gerados a partir dos data marts analíticos."""
from pathlib import Path
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt


def criar_graficos(tabelas:dict,pasta:Path)->None:
    pasta.mkdir(parents=True,exist_ok=True)
    base=tabelas['mensal']
    fig,ax=plt.subplots(figsize=(10,5))
    ax.plot(base['mes'],base['receita'],marker='o')
    ax.set(title='Receita por mês',xlabel='Mês do pedido',ylabel='R$')
    ax.tick_params(axis='x',rotation=45)
    fig.tight_layout();fig.savefig(pasta/'01_receita_mensal.png',dpi=140);plt.close(fig)

    base=tabelas['categoria']
    fig,ax=plt.subplots(figsize=(9,5))
    ax.barh(base['categoria'],base['receita'])
    ax.invert_yaxis();ax.set(title='Receita por categoria',xlabel='R$')
    fig.tight_layout();fig.savefig(pasta/'02_receita_categoria.png',dpi=140);plt.close(fig)

    base=tabelas['canal']
    fig,ax=plt.subplots(figsize=(9,5))
    ax.bar(base['canal'],base['receita'])
    ax.set(title='Receita por canal',ylabel='R$')
    fig.tight_layout();fig.savefig(pasta/'03_receita_canal.png',dpi=140);plt.close(fig)

    base=tabelas['estado']
    fig,ax=plt.subplots(figsize=(9,5))
    ax.bar(base['uf'],base['receita'])
    ax.set(title='Receita por estado',xlabel='UF',ylabel='R$')
    fig.tight_layout();fig.savefig(pasta/'04_receita_estado.png',dpi=140);plt.close(fig)

    base=tabelas['entregas']
    fig,ax=plt.subplots(figsize=(9,5))
    ax.bar(base['canal'],base['prazo_medio_dias'])
    ax.set(title='Prazo médio de entrega por canal',ylabel='Dias')
    fig.tight_layout();fig.savefig(pasta/'05_prazo_entrega.png',dpi=140);plt.close(fig)
