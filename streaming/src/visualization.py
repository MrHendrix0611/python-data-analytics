import matplotlib.pyplot as plt
import seaborn as sns
import pandas as pd

def gerar_graficos(df: pd.DataFrame) -> None:
    """Gera e exibe as visualizações gráficas da análise."""
    sns.set_theme(style="whitegrid")
    
    fig, axes = plt.subplots(1, 2, figsize=(14, 5))

    # Gráfico 1: Motivos de Cancelamento
    df_churned = df[df['churn'] == 1]
    sns.countplot(
        data=df_churned, 
        y='motivo_cancelamento', 
        hue='motivo_cancelamento',
        ax=axes[0], 
        palette='Reds_r',
        legend=False,
        order=df_churned['motivo_cancelamento'].value_counts().index
    )
    axes[0].set_title('Distribuição dos Motivos de Cancelamento')
    axes[0].set_xlabel('Quantidade de Cancelamentos')
    axes[0].set_ylabel('Motivo')

    # Gráfico 2: Tempo de Uso por Plano x Churn
    sns.barplot(
        data=df, 
        x='plano_contratado', 
        y='tempo_uso_diario_min', 
        hue='churn', 
        ax=axes[1], 
        palette='Set1'
    )
    axes[1].set_title('Tempo Diário Médio (min) por Plano vs Churn')
    axes[1].set_xlabel('Plano Contratado')
    axes[1].set_ylabel('Tempo Diário Médio (min)')
    axes[1].legend(title='Status', labels=['Ativo (0)', 'Cancelado (1)'])

    plt.tight_layout()
    plt.show()