# Arquitetura do Sistema - Northwind Data Pipeline (Modelo Medalhão)

Este documento descreve a arquitetura do Northwind Data Pipeline focada em processamento **Batch** e na **Arquitetura Medalhão**, utilizando o framework RM-ODP.

## 1. RM-ODP Viewpoints

### 1.1 Enterprise Viewpoint
- **Objetivo:** Processamento confiável de grandes volumes em batch.
- **Políticas:** 
    - Arquitetura Medalhão (Bronze -> Silver -> Gold).
    - Monitoramento 100% via Logs (Sem notificações externas).
    - Idempotência em todas as camadas.

### 1.2 Information Viewpoint
Define o ciclo de vida do dado nas camadas Medalhão:
- **Landing Zone (MinIO):** Arquivos CSV originais e imutáveis.
- **Bronze (ClickHouse):** Tabelas espelho do CSV. Preserva histórico bruto para auditoria.
- **Silver (ClickHouse):** Dados limpos, tipados e enriquecidos. Joins realizados.
- **Gold (ClickHouse):** Tabelas de performance e agregados de negócio (Data Marts).

### 1.3 Computational Viewpoint
- **Batch Orchestrator:** Gerencia a execução sequencial das camadas.
- **Bronze Loader:** Move dados do MinIO para o ClickHouse (Bronze).
- **Silver Transformer:** Processa limpeza e unificação (Silver).
- **Gold Aggregator:** Gera visões de negócio (Gold).
- **Log Monitor:** Centraliza a telemetria JSON de todos os estágios.

### 1.4 Engineering Viewpoint
- **Processamento:** Containers Python stateless escaláveis para lotes volumosos.
- **Banco Analítico:** ClickHouse organizado em múltiplos bancos de dados ou esquemas para representar as camadas Medalhão.
- **Observability:** Logs JSON redirecionados para o stdout do Docker para coleta passiva.

---

## 2. ADRs (Architecture Decision Records)

### ADR 01: Uso do ClickHouse como Banco Analítico (OLAP)
- **Contexto:** Necessidade de processar e consultar ~100k registros diários com alta performance agregada.
- **Decisão:** Adotar o ClickHouse como motor principal para as camadas Medalhão.
- **Consequências:** Alta performance em queries analíticas, mas exige gerenciamento rigoroso de idempotência em sistemas batch.

### ADR 02: Arquitetura Medalhão (Bronze, Silver, Gold)
- **Contexto:** Necessidade de rastreabilidade, qualidade de dados e separação entre dados brutos e analíticos.
- **Decisão:** Estruturar o banco de dados em camadas Bronze (Raw), Silver (Cleaned/Unified) e Gold (Aggregated).
- **Consequências:** Clareza na linhagem de dados e facilidade de reprocessamento, com custo incremental de storage.

### ADR 03: Landing Zone no MinIO com Retenção de 7 Dias
- **Contexto:** Garantir a integridade dos dados originais e permitir Replay (RF-08) sem esgotar o storage.
- **Decisão:** Persistir CSVs brutos no MinIO por 7 dias fixos antes do expurgo automático.
- **Consequências:** Permite auditoria e recuperação de falhas recentes de forma eficiente.

### ADR 04: Monitoramento Exclusivo via Logs Estruturados (Log-only)
- **Contexto:** Simplificação da infraestrutura e foco em observabilidade SRE passiva.
- **Decisão:** Não utilizar notificações externas (Slack/Email). Toda a telemetria será via logs JSON.
- **Consequências:** Reduz complexidade no código, mas exige ferramentas de parsing para monitoramento de saúde.

### ADR 05: Processamento Stateless na Camada Silver
- **Contexto:** Suportar picos de carga e garantir o SLO de processamento de 2h através de escalabilidade horizontal.
- **Decisão:** O componente de transformação (Silver) deve ser stateless, processando lotes de forma isolada.
- **Consequências:** Facilita o uso de múltiplos workers Docker, movendo o controle de unicidade para o Loader/ClickHouse.

### ADR 06: Injeção de Audit Trail em Camadas
- **Contexto:** Necessidade de rastrear a linhagem (Audit Trail) desde o arquivo de origem até o KPI final (RF-10).
- **Decisão:** Adicionar colunas `source_file`, `batch_id` e `loaded_at` nas camadas Silver e Gold.
- **Consequências:** Facilita troubleshooting e auditoria de dados, com custo marginal de storage.

### ADR 07: Python 3.11+ para Lógica de Orquestração Batch
- **Contexto:** Necessidade de linguagem versátil com suporte a processamento de dados e APIs de storage/DB.
- **Decisão:** Utilizar Python 3.11+ para o Batch Manager e componentes ETL.
- **Consequências:** Desenvolvimento ágil e vasta biblioteca de integração disponível.

### ADR 08: MinIO (S3 API) para Abstração de Storage
- **Contexto:** Garantir portabilidade entre ambientes locais (Docker) e nuvem (AWS S3).
- **Decisão:** Utilizar o MinIO como Landing Zone via API S3.
- **Consequências:** O código de integração permanece o mesmo em qualquer ambiente compatível com S3.

### ADR 09: Docker Compose para Padronização de Ambiente
- **Contexto:** Garantir que o pipeline funcione de forma idêntica em desenvolvimento e produção local (SRE).
- **Decisão:** Utilizar Docker Compose para orquestrar os containers das camadas Medalhão.
- **Consequências:** Ambiente reprodutível e isolado, facilitando testes de integração e fumaça.

### ADR 10: Estratégia de Carga via Staging Tables (Atomic Load)
- **Contexto:** Evitar dados parciais ou corrompidos na tabela final durante falhas no meio do lote batch.
- **Decisão:** Carregar dados em uma tabela `staging` antes do swap ou merge atômico para a produção.
- **Consequências:** Garante a integridade da camada analítica e evita o "sofrimento silencioso".
