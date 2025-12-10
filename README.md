











---
## ⚙️ Regras de Concessão (Lógica de Negócio)
O motor de decisão aplica lógicas de negócio diretamente em Dataframes Spark:
 **1. Cálculo de Capacidade:** O limite da parcela não pode exceder 30% da renda mensal.

 **2. Hard Rules (Reprovação Automática):**

    • Cliente com restrição ativa no Bureau Externo (SPC/Serasa).

    • Endividamento total de mercado superior a 10x a renda mensal.

 **Exemplo de Código Modularizado (src/transformations.py)**

def aplicar_regras_credito(df):
    return df.withColumn(
        "status_analise",
        when(
            (col("restricao_spc") == "S") | 
            (col("divida_total_mercado") > (col("renda_mensal") * 10)), 
            lit("REPROVADO_RISCO")
        ).otherwise(lit("APROVADO"))
    )

## 📂 Estrutura do Projeto Profissional

coop-credit-engine/
├── .github/workflows/   # Pipeline de CI/CD (GitHub Actions)
├── dags/                # Orquestração do Airflow
├── docs/                # Documentação e ADRs
├── src/                 # Código Fonte (Lógica Pura Spark)
├── tests/               # Testes Unitários Automatizados
├── docker-compose.yaml  # Infraestrutura como Código
├── Makefile             # Automação de comandos
└── README.md            # Documentação Geral

## 📸 Evidências de Execução

### 1. Pipeline de Dados (Airflow)
Fluxo completo de ingestão, processamento Spark e carga no DW executado com sucesso.
![Fluxo Airflow](https://github.com/ricardoribs/Coop-Credit-Engine/blob/main/airflow.PNG)

### 2. Resultado da Análise (Data Warehouse)
Consulta final demonstrando a aplicação das regras. Note que clientes com dívidas altas ou restrições foram automaticamente classificados como `REPROVADO_RISCO`.
![Tabela SQL](https://github.com/ricardoribs/Coop-Credit-Engine/blob/main/resultado.PNG)        


## 🚀 Como Executar

**1. Pré-requisitos**
 • Docker & Docker Compose

**2. Rodar o Pipeline Completo**
 docker-compose up --build

Acesse:
👉 Airflow: http://localhost:8080

Login/Senha: airflow / airflow

**3. Rodar Testes sem Docker**
pip install -r requirements.txt
pytest tests/ -v

