import pytest
from pyspark.sql import SparkSession
# Importa a função que criamos na pasta src
from src.transformations import aplicar_regras_credito

# Isso cria um "Mini Spark" só para o teste (Fixtures do Pytest)
@pytest.fixture(scope="session")
def spark():
    return SparkSession.builder \
        .master("local[1]") \
        .appName("TesteUnitario") \
        .getOrCreate()

def test_aprovacao_cliente_bom(spark):
    """
    CENÁRIO 1: Cliente ideal.
    Renda: 5000, Dívida: 0, Restrição: N.
    Esperado: APROVADO.
    """
    # 1. Cria dados falsos (Mock)
    dados = [("Cliente Bom", 5000.0, 0.0, "N")]
    cols = ["nome", "renda_mensal", "divida_total_mercado", "restricao_spc"]
    df = spark.createDataFrame(dados, cols)

    # 2. Roda a função
    df_resultado = aplicar_regras_credito(df)
    
    # 3. Pega o resultado
    status = df_resultado.select("status_analise").collect()[0][0]
    limite = df_resultado.select("limite_parcela_segura").collect()[0][0]

    # 4. A Prova Real (Asserts)
    assert status == "APROVADO"
    assert limite == 1500.0 # 30% de 5000

def test_reprovacao_spc(spark):
    """
    CENÁRIO 2: Cliente com nome sujo.
    Renda: 10000, Restrição: S.
    Esperado: REPROVADO_RISCO.
    """
    dados = [("Cliente Ruim", 10000.0, 0.0, "S")]
    cols = ["nome", "renda_mensal", "divida_total_mercado", "restricao_spc"]
    df = spark.createDataFrame(dados, cols)

    df_resultado = aplicar_regras_credito(df)
    status = df_resultado.select("status_analise").collect()[0][0]

    assert status == "REPROVADO_RISCO"

def test_reprovacao_superendividado(spark):
    """
    CENÁRIO 3: Cliente devendo muito.
    Renda: 2000, Dívida: 25000 (> 10x renda).
    Esperado: REPROVADO_RISCO.
    """
    dados = [("Cliente Devedor", 2000.0, 25000.0, "N")]
    cols = ["nome", "renda_mensal", "divida_total_mercado", "restricao_spc"]
    df = spark.createDataFrame(dados, cols)

    df_resultado = aplicar_regras_credito(df)
    status = df_resultado.select("status_analise").collect()[0][0]

    assert status == "REPROVADO_RISCO"