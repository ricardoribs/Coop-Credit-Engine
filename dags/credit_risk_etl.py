from airflow import DAG
from airflow.operators.python import PythonOperator
from airflow.providers.postgres.hooks.postgres import PostgresHook
from datetime import datetime
import pandas as pd
import random
# Importando o Spark (A tecnologia do Databricks)
from pyspark.sql import SparkSession
from pyspark.sql.functions import col, when, lit

# --- FUNÇÕES ---

def gerar_dados_simulados():
    """
    PASSO 1: Simula os sistemas da Cooperativa.
    Gera dois arquivos CSV: Clientes (Renda) e Bureau (Dívidas).
    """
    # 1. Dados Internos (Cooperativa)
    clientes = []
    for i in range(1, 200): # 200 Clientes
        clientes.append({
            "cliente_id": i,
            "nome": f"Cooperado {i}",
            "renda_mensal": round(random.uniform(3000, 20000), 2),
            "tempo_relacionamento_anos": random.randint(1, 20)
        })
    pd.DataFrame(clientes).to_csv("/tmp/clientes_interno.csv", index=False)

    # 2. Dados Externos (Bureau de Crédito / Serasa Mock)
    dividas = []
    for i in range(1, 200):
        # 20% dos clientes terão restrição no nome (Nome Sujo)
        tem_restricao = "S" if random.random() > 0.8 else "N"
        divida = round(random.uniform(500, 50000), 2) if random.random() > 0.5 else 0
        
        dividas.append({
            "cliente_id": i,
            "divida_total_mercado": divida,
            "restricao_spc": tem_restricao
        })
    pd.DataFrame(dividas).to_csv("/tmp/bureau_externo.csv", index=False)
    print("Dados brutos gerados com sucesso!")

def processar_com_spark():
    """
    PASSO 2: O MOTOR DE RISCO (PySpark).
    Cruza os dados e decide quem ganha crédito.
    """
    # Inicia o Spark (Mini Cluster dentro do Docker)
    spark = SparkSession.builder \
        .appName("MotorCredito") \
        .config("spark.driver.memory", "1g") \
        .getOrCreate()

    # Leitura dos CSVs usando Spark (Performático)
    df_clientes = spark.read.csv("/tmp/clientes_interno.csv", header=True, inferSchema=True)
    df_bureau = spark.read.csv("/tmp/bureau_externo.csv", header=True, inferSchema=True)

    # JOIN (Cruzamento de dados)
    df_completo = df_clientes.join(df_bureau, on="cliente_id", how="left")

    # --- REGRAS DE NEGÓCIO (Credit Scoring) ---
    
    # Regra 1: Calcular Capacidade de Pagamento (30% da renda)
    df_calculado = df_completo.withColumn(
        "limite_parcela_segura", 
        col("renda_mensal") * 0.30
    )

    # Regra 2: Motor de Decisão (Aprovado ou Reprovado)
    # Se tiver restrição SPC OU Dívida maior que 10x a Renda -> REPROVA
    df_decisao = df_calculado.withColumn(
        "status_analise",
        when(
            (col("restricao_spc") == "S") | 
            (col("divida_total_mercado") > (col("renda_mensal") * 10)), 
            lit("REPROVADO_RISCO")
        ).otherwise(lit("APROVADO"))
    )

    # Salva o resultado processado
    # (Transformamos em Pandas apenas no final para facilitar a carga no Postgres local)
    resultado_final = df_decisao.toPandas()
    resultado_final.to_csv("/tmp/analise_concluida.csv", index=False)
    
    spark.stop()
    print("Análise de Risco finalizada via Spark!")

def carga_data_warehouse():
    """
    PASSO 3: Carga no Banco de Dados para o Analista ver.
    """
    pg_hook = PostgresHook(postgres_conn_id='airflow_db')
    engine = pg_hook.get_sqlalchemy_engine()
    
    df = pd.read_csv("/tmp/analise_concluida.csv")
    # Salva na tabela 'analise_credito'
    df.to_sql('analise_credito', engine, if_exists='replace', index=False)
    print("Tabela de Decisão carregada no DW!")

# --- DAG ---
with DAG(
    dag_id="coop_credit_pipeline",
    start_date=datetime(2024, 1, 1),
    schedule_interval=None,
    catchup=False,
) as dag:

    t1 = PythonOperator(task_id="gerar_dados", python_callable=gerar_dados_simulados)
    t2 = PythonOperator(task_id="motor_spark", python_callable=processar_com_spark)
    t3 = PythonOperator(task_id="carga_dw", python_callable=carga_data_warehouse)

    t1 >> t2 >> t3