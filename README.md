# Northwind Data Pipeline

## 📖 O Problema
O negócio Northwind atua no domínio de distribuição de alimentos e bebidas. Atualmente, a empresa enfrenta um gap significativo entre a geração transacional de pedidos e a visibilidade analítica necessária para a tomada de decisão.

**O Desafio Principal:**
Processar de forma confiável um volume de aproximadamente **100 mil pedidos diários** (`Orders` e `Order Details`), garantindo que o dado chegue a um banco analítico de forma idempotente (sem duplicidade) e observável. O sistema é regido por uma política estrita de "zero falhas silenciosas" (Zero Silent Failures).

---

## 📁 Estrutura de Documentação (`/documents`)
A fase de Engenharia e SRE já foi concluída e está totalmente documentada na pasta `documents/`. Lá você encontrará o planejamento detalhado que guia este repositório:

- **Requisitos (`01_` e `02_`):** Detalhamento de 10 Requisitos Funcionais e 11 Não Funcionais (SLIs/SLOs focados em throughput e resiliência).
- **Arquitetura (`03_`):** Visão RM-ODP e registro de 10 Decisões Arquiteturais (ADRs).
- **Rastreabilidade (`04_rtm.md`):** Matriz RTM garantindo que cada requisito seja coberto por um componente e um teste.
- **Planos de Teste (`05_`, `06_`, `07_`):** Estratégias de validação para Modelagem (Qualidade dos Dados), Carga (Performance/SRE) e Segurança (Integridade).
- **System Design (`08_system_design.md`):** O blueprint técnico detalhando a estrutura do código e os esquemas do banco.
- **Índice (`00_index.md`):** Guia rápido para navegar por todos esses artefatos.

---

## 🏗️ Arquitetura Proposta
O projeto implementa uma pipeline de dados **Batch** adotando o padrão **Arquitetura Medalhão**, orquestrada em containers via Docker.

A stack tecnológica principal é composta por:
1.  **Landing Zone (MinIO):** Atua como storage imutável (API S3) para os arquivos CSV recebidos, garantindo retenção de 7 dias para auditoria e replay.
2.  **ETL & Orquestração (Python):** Aplicação stateless responsável por mover e transformar os dados.
3.  **Banco Analítico (ClickHouse):** Motor OLAP de alta performance estruturado em três camadas:
    - **Bronze:** Dados brutos (espelho da Landing Zone).
    - **Silver:** Dados unificados (Orders + Details), sanitizados e rastreáveis (Audit Trail).
    - **Gold:** Agregados de negócio de alta performance.
4.  **Visualização (Streamlit):** Dashboard interativo lendo diretamente da camada Gold.
5.  **Observabilidade:** Monitoramento SRE passivo, onde 100% da telemetria é baseada em logs JSON estruturados emitidos pelos containers.

*(Nota: O diagrama detalhado da arquitetura (Mermaid), os modelos lógicos/físicos e as instruções de execução via `docker-compose` serão adicionados a este README durante a fase de implementação).*
