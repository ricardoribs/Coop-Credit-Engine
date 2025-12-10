import sys
import os
# Adiciona a pasta raiz ao Python Path para o Airflow achar o 'src'
sys.path.insert(0, os.path.abspath(os.path.dirname(__file__) + "/.."))

from airflow import DAG
from airflow.operators.python import PythonOperator
from airflow.providers.postgres.hooks.postgres import PostgresHook
from datetime import datetime
import pandas as pd
import random
from pyspark.sql import SparkSession
# Importando a lógica profissional da pasta SRC
from src.transformations import aplicar_regras_credito

# --- FUNÇÕES ---

def gerar_dados_simulados():
    """Gera arquivos CSV simulados (Clientes e Bureau)"""
    clientes = []
    for i in range(1, 200):
        clientes.append({
            "cliente_id": i,
            "nome": f"Cooperado {i}",
            "renda_mensal": round(random.uniform(3000, 20000), 2),
            "tempo_relacionamento_anos": random.randint(1, 20)
        })
    pd.DataFrame(clientes).to_csv("/tmp/clientes_interno.csv", index=False)

    dividas = []
    for i in range(1, 200):
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
    Motor de Crédito Modularizado.
    """
    spark = SparkSession.builder \
        .appName("MotorCredito") \
        .config("spark.driver.memory", "1g") \
        .getOrCreate()

    # Leitura
    df_clientes = spark.read.csv("/tmp/clientes_interno.csv", header=True, inferSchema=True)
    df_bureau = spark.read.csv("/tmp/bureau_externo.csv", header=True, inferSchema=True)

    # Join
    df_completo = df_clientes.join(df_bureau, on="cliente_id", how="left")

    # --- AQUI ESTÁ A MUDANÇA: Chamamos a função externa ---
    df_decisao = aplicar_regras_credito(df_completo)
    # -----------------------------------------------------

    # Salva
    resultado_final = df_decisao.toPandas()
    resultado_final.to_csv("/tmp/analise_concluida.csv", index=False)
    spark.stop()

def carga_data_warehouse():
    """Carga no Postgres"""
    pg_hook = PostgresHook(postgres_conn_id='airflow_db')
    engine = pg_hook.get_sqlalchemy_engine()
    df = pd.read_csv("/tmp/analise_concluida.csv")
    df.to_sql('analise_credito', engine, if_exists='replace', index=False)

# --- DAG ---
with DAG(
    dag_id="coop_credit_pipeline_v2", # Mudei o nome para V2
    start_date=datetime(2024, 1, 1),
    schedule_interval=None,
    catchup=False,
) as dag:

    t1 = PythonOperator(task_id="gerar_dados", python_callable=gerar_dados_simulados)
    t2 = PythonOperator(task_id="motor_spark_modular", python_callable=processar_com_spark)
    t3 = PythonOperator(task_id="carga_dw", python_callable=carga_data_warehouse)

    t1 >> t2 >> t3