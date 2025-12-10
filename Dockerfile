FROM apache/airflow:2.9.1
USER root

# 1. Instalando Java (Obrigatório para o Spark funcionar)
RUN apt-get update && \
    apt-get install -y default-jdk && \
    apt-get clean

# 2. Configurando onde o Java está
ENV JAVA_HOME /usr/lib/jvm/default-java

USER airflow

# 3. Instalando PySpark e bibliotecas de dados
RUN pip install --no-cache-dir apache-airflow-providers-postgres pandas pyspark psycopg2-binary