# Requirements Traceability Matrix (RTM) - Northwind Data Pipeline

Este documento garante que todos os requisitos funcionais e não funcionais, componentes e estratégias de validação batch.

## Matriz de Rastreabilidade

| ID | Tipo | Stakeholder | Camada Medalhão | Fluxo Crítico | Risco Mitigado | Componente | Teste (TC) | Status |
| :--- | :--- | :--- | :--- | :--- | :--- | :--- | :--- | :--- |
| **RF-01** | RF | Time de Dados, SRE | Inbound | Batch Ingest | Malformed Input | Ingestor | TC-01 (Inbound Schema) | Coberto |
| **RF-02** | RF | Time de Dados, SRE | Landing Zone | Storage | Perda de dado bruto | MinIO | TC-02 (Object Persistence) | Coberto |
| **RF-03** | RF | Time de Dados | Bronze | Raw Load | Histórico corrompido | Bronze Loader | TC-26 (Bronze Accuracy) | Coberto |
| **RF-04** | RF | Time de Dados | Silver | Transformation | Dados não unificados | Silver Transf. | TC-27 (Silver Integration) | Coberto |
| **RF-05** | RF | Negócio, Consumidores | Gold | Aggregation | Indicadores incorretos | Gold Aggr. | TC-28 (Gold Consistency) | Coberto |
| **RF-06** | RF | Time de Dados, Negócio | Todas | Idempotency | Duplicidade em camadas | Loader | TC-04 (Multi-layer Idemp.) | Coberto |
| **RF-07** | RF | Plataforma / SRE | Todas | Telemetria | Falha batch silenciosa | Obs Agent | TC-07 (JSON Log Audit) | Coberto |
| **RF-08** | RF | Time de Dados, Negócio | Todas | Replay | Incapacidade de recovery | Replay Mgr | TC-08 (Batch Replay) | Coberto |
| **RF-09** | RF | Time de Dados | Silver | Data Quality | Strings sujas/Nulos | Silver Transf. | TC-09 (Sanitization) | Coberto |
| **RF-10** | RF | Plataforma / SRE | Silver/Gold | Audit | Perda de linhagem | Loader | TC-10 (Audit Metadata) | Coberto |
| **RNF-01** | RNF | Time de Dados, Negócio | Todas | Reconciliation | Diferença CSV vs DB | Loader | TC-11 (Layer Recon) | Coberto |
| **RNF-02** | RNF | Time de Dados, SRE | Todas | Throughput | Gargalo no lote diário | Batch Mgr | TC-12 (E2E Batch Time) | Coberto |
| **RNF-03** | RNF | Plataforma / SRE | Inbound/Bronze | Protocol Check | Lock-in de storage | Ingestor | TC-13 (S3/Native CH) | Coberto |
| **RNF-04** | RNF | Consumidores, Negócio | Gold | UI Performance | Dashboard lento | Dashboard | TC-14 (Gold Query Perf) | Coberto |
| **RNF-05** | RNF | Plataforma / SRE | Todas | Observability | Erro não reportado | Obs Agent | TC-15 (Log Error Capture) | Coberto |
| **RNF-06** | RNF | SRE, Time de Dados | Silver/Gold | Data Integrity | Carga parcial visível | Loader | TC-16 (Atomic Staging) | Coberto |
| **RNF-11** | RNF | Plataforma / SRE | Landing Zone | Retention | Disco cheio | MinIO | TC-21 (7-day Retention) | Coberto |

## Lacunas Detectadas
- **Orquestração Sequential:** A RTM assume que o `Batch Manager` dispara as camadas Bronze -> Silver -> Gold sequencialmente, mas falhas no meio do processo exigem uma política de "parada total" ou "skip" que deve ser testada.

## Riscos sem Mitigação
- **Consistência Cross-Layer:** Se a camada Bronze for atualizada mas a Silver falhar, haverá um descasque temporal entre as camadas. A mitigação é o Replay manual (RF-08).
