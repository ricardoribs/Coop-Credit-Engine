# 🏦 Coop-Credit Engine: Pipeline de Risco de Crédito com Spark

![CI Status](https://github.com/ricardoribs/coop-credit-engine/actions/workflows/ci.yml/badge.svg)
![Spark](https://img.shields.io/badge/Big%20Data-PySpark-orange?style=for-the-badge&logo=apachespark)
![Airflow](https://img.shields.io/badge/Orchestration-Apache%20Airflow-blue?style=for-the-badge&logo=apacheairflow)
![Tests](https://img.shields.io/badge/Tests-Pytest-green?style=for-the-badge&logo=pytest)

> **Contexto:** Projeto de Engenharia de Dados desenvolvido para automatizar a análise de concessão e risco de crédito em uma Cooperativa, utilizando arquitetura distribuída e boas práticas de Engenharia de Software.

---

## 📌 1. Problema de Negócio

Uma Cooperativa processa milhares de solicitações de empréstimo por dia. O processo manual atrasa aprovações e não escala.

🎯 **Objetivo:** Criar um *Decision Engine* capaz de aprovar ou reprovar crédito em segundos, cruzando renda declarada e restrições de mercado.

---

## ⚙️ 2. Arquitetura do Sistema

Este projeto segue boas práticas de Engenharia de Software aplicadas a dados:
* **Modularização:** Código desacoplado da orquestração.
* **Qualidade:** Testes unitários com Pytest.
* **CI/CD:** Validação contínua via GitHub Actions.
* **Infraestrutura:** Docker com Spark e Airflow integrados.

### Diagrama de Fluxo

```mermaid
graph LR
    A[Cadastro Cooperado] --> C{Cluster Spark}
    B[Bureau Externo] --> C
    C -->|Processamento| D[Motor de Regras]
    D -->|Classificação| E[Aprovado/Reprovado]
    E -->|Carga| F[(Data Warehouse)]
    
    style C fill:#ff9900,color:white
    style F fill:#333,color:white
