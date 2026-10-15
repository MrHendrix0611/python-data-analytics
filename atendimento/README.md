# Análise de Atendimento ao Cliente

Projeto de análise exploratória de chamados de suporte registrados em um arquivo JSON com estruturas aninhadas. A aplicação normaliza os registros com Pandas, valida a integridade da base, calcula indicadores operacionais e gera gráficos e um relatório textual.

## Requisitos

- Python 3.10 ou superior
- Bibliotecas do `requirements.txt`

## Executar no Windows (PowerShell)

```powershell
py -m venv .venv
.\.venv\Scripts\python.exe -m pip install -r requirements.txt
.\.venv\Scripts\python.exe main.py
.\.venv\Scripts\python.exe -m pytest -q
```

No Linux/macOS, use `python3 -m venv .venv`, `./.venv/bin/python -m pip install -r requirements.txt` e `./.venv/bin/python main.py`.

## Estrutura

```text
atendimento/
├── data/
│   ├── raw/chamados.json
│   └── processed/                 # CSVs normalizados, gerados na execução
├── src/
│   ├── coleta.py                  # Leitura do JSON e json_normalize
│   ├── limpar.py                  # Validação e tipos
│   ├── tratar.py                  # explode e tempos de atendimento
│   ├── analysis.py                # Agregações e indicadores
│   ├── visualization.py           # Gráficos
│   └── report.py                  # Relatório textual
├── tests/test_pipeline.py
├── scripts/gerar_base.py           # Gera a base de demonstração
├── outputs/
│   ├── graficos/
│   └── relatorios/
├── main.py
├── requirements.txt
└── README.md
```

## Formato dos dados

O arquivo `data/raw/chamados.json` contém uma lista de clientes. Cada cliente possui uma lista de chamados; cada chamado contém o atendente como objeto e as interações como lista.

```json
{
  "clientes": [
    {
      "id_cliente": "CLI-001",
      "nome": "Cliente 001",
      "segmento": "Microempresa",
      "chamados": [
        {
          "id_chamado": "CH-0001",
          "categoria": "Cobrança",
          "status": "Resolvido",
          "atendente": {"id_atendente": "AT-01", "nome": "Camila"},
          "aberto_em": "2026-03-12T08:30:00",
          "fechado_em": "2026-03-13T10:00:00",
          "avaliacao": 5,
          "reaberto": false,
          "interacoes": [
            {"data": "2026-03-12T08:35:00", "tipo": "mensagem_cliente", "canal": "Chat", "tempo_gasto_minutos": 0},
            {"data": "2026-03-12T09:00:00", "tipo": "resposta_atendente", "canal": "Chat", "tempo_gasto_minutos": 12}
          ]
        }
      ]
    }
  ]
}
```

O fragmento acima ilustra a estrutura; a base distribuída contém mais registros.

### Operações de normalização

- `json.load()`: lê objetos e listas do JSON como estruturas Python.
- `pd.json_normalize()`: cria linhas para cada chamado, preservando o identificador do cliente e expandindo o objeto do atendente em colunas.
- `explode("interacoes")`: cria uma linha por interação, mantendo o identificador do chamado.
- `pd.to_datetime()`: converte datas para calcular intervalos de atendimento.

## Indicadores

| Indicador | Definição |
|---|---|
| Taxa de resolução | Chamados com status `Resolvido` / total de chamados |
| Tempo médio de resolução | Média do intervalo entre abertura e fechamento dos chamados resolvidos |
| Tempo até primeira resposta | Média do intervalo entre abertura e primeira resposta do atendente, apenas onde houver resposta |
| Produtividade por atendente | Quantidade de chamados resolvidos atribuídos a cada atendente |
| Recorrência por categoria | Percentual dos clientes de uma categoria que registraram dois ou mais chamados nessa categoria |
| Satisfação | Média das avaliações informadas nos chamados resolvidos |

**Data de referência:** 30/09/2026. **Origem:** base fictícia, gerada especificamente para testes e estudo. Os indicadores não devem ser interpretados como desempenho de uma empresa real.

## Arquivos gerados

- `data/processed/chamados.csv`: chamados normalizados.
- `data/processed/interacoes.csv`: interações normalizadas.
- `outputs/relatorios/relatorio.txt`: resumo dos indicadores.
- `outputs/graficos/`: cinco gráficos PNG.

## Perguntas para analisar

1. Quais categorias concentram mais chamados?
2. Qual é o tempo médio de resolução dos problemas?
3. Quais atendentes encerraram mais chamados?
4. Quais categorias têm maior proporção de clientes recorrentes?
5. Os chamados abertos e resolvidos aumentam ou diminuem ao longo do período?

## Observações

A produtividade depende também da complexidade e da distribuição dos chamados. Por isso, a contagem de resoluções não deve ser usada isoladamente para avaliar pessoas. A média de primeira resposta exclui chamados sem resposta registrada, e a satisfação considera apenas avaliações disponíveis.
