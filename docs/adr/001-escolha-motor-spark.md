# ADR 001: Adoção do Apache Spark para Motor de Crédito

**Status:** Aceito  
**Data:** 10-12-2025  
**Contexto:** Vaga de Crédito / Databricks

## O Problema
O processamento de crédito envolve o cruzamento de grandes volumes de dados (transações internas + bureau externo). A solução precisa ser escalável para milhões de clientes sem gargalos de memória.

## A Decisão
Optamos por utilizar **Apache Spark (PySpark)** em vez de Pandas puro.

## Motivação
1.  **Escalabilidade:** O Spark processa em cluster (distribuído), enquanto o Pandas é limitado à memória de uma única máquina.
2.  **Alinhamento com Databricks:** A sintaxe utilizada (`df.withColumn`, `when/col`) é nativa do ambiente Databricks, facilitando a migração para a nuvem.
3.  **Performance:** O Spark utiliza *Lazy Evaluation* e otimizadores (Catalyst) que tornam regras de negócio complexas mais eficientes.

## Consequências
* **Positivo:** Código pronto para Big Data; Testes unitários rápidos com Spark Local.
* **Negativo:** Necessidade de instalar JVM (Java) no ambiente de desenvolvimento (Docker).