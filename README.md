# Olist Data Pipeline - SRE & Data Engineering

Este repositório foi desenvolvido como parte da disciplina de **SRE (Site Reliability Engineering)** do MBA em Engenharia de Dados. O foco é a aplicação de práticas de confiabilidade, observabilidade e escalabilidade em um pipeline de dados crítico.

## 🎯 Objetivo do Projeto
Resolver o desafio técnico de processar ~100 mil pedidos diários da Olist, garantindo que os dados cheguem ao banco analítico de forma confiável, sem duplicidade e com total observabilidade, evitando o "sofrimento silencioso" do sistema.

## 🏗️ Arquitetura (AWS Event-Driven)
A solução utiliza uma arquitetura moderna na AWS, projetada para ser resiliente e de baixo custo:
- **AWS S3:** Armazenamento estruturado em camadas (`/landing`, `/processed`, `/failed`).
- **AWS Lambda:** Trigger serverless acionado por eventos de upload.
- **AWS ECS Fargate:** Processamento de ETL via containers Docker (Python/Pandas), garantindo isolamento de recursos.
- **AWS RDS Postgres:** Banco de dados analítico utilizando técnicas de `COPY` (Bulk Load) e `UPSERT` (Idempotência).
- **AWS CloudWatch:** Central de telemetria com métricas numéricas e alarmes proativos via SNS.

## 📂 Organização de Documentos
- `documents/`: Base de conhecimento do projeto.
    - `01_functional_requirements.md`: 31 requisitos (Ingestão, ETL, Notificação).
    - `02_non_functional_requirements.md`: 20 requisitos de qualidade (SRE, Segurança, FinOps).
    - `03_architecture.md`: Detalhamento técnico via RM-ODP e registros de decisões (ADRs).
    - `04_rtm.md`: Matriz de Rastreabilidade para garantir 100% de cobertura.
    - `spec/`: Especificação técnica original do problema.

## 🛠️ Pilares de SRE Aplicados
- **Observabilidade:** Métricas de sucesso, falha e latência exportadas em tempo real.
- **Resiliência:** Implementação de *Circuit Breaker* para proteção do banco de dados.
- **Segurança e Conformidade:** Isolamento em rede privada (VPC Endpoints) e mascaramento de dados (PII/LGPD).
- **Automação:** Infraestrutura como Código (Terraform) e versionamento de schema.

---
**Disciplina:** Engenharia de Confiabilidade (SRE)  
**Contexto:** MBA em Engenharia de Dados
