from pyspark.sql import DataFrame
from pyspark.sql.functions import col, when, lit

def aplicar_regras_credito(df: DataFrame) -> DataFrame:
    """
    Aplica as regras de concessão de crédito (Business Logic).
    Esta função é Pura: recebe dados, aplica regras e retorna dados.
    
    Regras:
    1. Limite de Parcela = 30% da Renda.
    2. Status = NEGADO se tiver restrição ou dívida > 10x renda.
    """
    
    # Regra 1: Calcular Capacidade de Pagamento (30% da renda)
    # Cria uma nova coluna 'limite_parcela_segura'
    df = df.withColumn(
        "limite_parcela_segura", 
        col("renda_mensal") * 0.30
    )

    # Regra 2: Motor de Decisão (Decision Engine)
    df = df.withColumn(
        "status_analise",
        when(
            (col("restricao_spc") == "S") | 
            (col("divida_total_mercado") > (col("renda_mensal") * 10)), 
            lit("REPROVADO_RISCO")
        ).otherwise(lit("APROVADO"))
    )
    
    return df