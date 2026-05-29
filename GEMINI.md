# GEMINI.md - Project Operating Guide: Northwind Data Pipeline

## 1. Project Context
The Northwind Data Pipeline is a Site Reliability Engineering (SRE) and Data Engineering project designed to bridge the gap between transactional order generation and analytical visibility for a food and beverage distribution business. The system must handle a high volume of daily transactions with strict reliability and observability requirements.

## 2. Business Goals & Engineering Constraints

| Business Goal | Engineering Constraint |
| :--- | :--- |
| **High Volume:** Process ~100k daily orders. | Pipeline must be optimized for a throughput of ~1.2 records/second (avg) and handle potential burst loads. |
| **Data Reliability:** Ensure data arrives at the analytical DB without loss. | All data ingestion steps must include integrity validation (e.g., CSV schema checks). |
| **Uniqueness:** Prevent data duplication. | Database loads MUST be **idempotent**. Use `UPSERT` logic or staging tables with atomic transfers to guarantee unicidade. |
| **Observability:** No "silent failures"; proactive anomaly detection. | Every component must emit real-time logs and metrics. Any error must be caught and reported proactively to the SRE/Platform team. |
| **Consistency:** Standardized environments. | The entire stack MUST be containerized using **Docker** for portability across environments. |

## 3. Stakeholders
- **Northwind Operation (Business):** Primary owners, interested in data availability for decision-making.
- **Data Team:** Responsible for ETL logic and data quality.
- **Dashboard Consumers:** End-users of the analytical layer.
- **Plataforma / SRE:** Responsible for system uptime, observability, and infrastructure.

## 4. Critical Flows
1.  **Ingestion:** Receiving CSV files (`northwind_orders.csv`, `northwind_order_details.csv`) and performing integrity/schema validation.
2.  **Storage:** Persistence of raw/landing data in **MinIO**.
3.  **ETL Processing:** Transformation of raw data into analytical formats.
4.  **Analytical Loading:** Idempotent insertion into **ClickHouse**.
5.  **Visualization:** Data presentation via **Streamlit** dashboards.
6.  **Telemetry Pipeline:** Real-time generation and collection of logs and metrics for all above steps.

## 5. Architecture Expectations
- **Stack:** MinIO (Storage) -> ETL (Python/Processing) -> ClickHouse (Analytical DB) -> Streamlit (Visualization).
- **Modeling:** Must deliver Conceptual, Logical, and Physical models for the Northwind dataset (Orders and Order Details).
- **Documentation:** Architecture diagrams must be rendered using **Mermaid** directly in the `README.md`.

## 6. Risks & Failure Modes
- **Risk: Silent Failure.** 
    - *Mitigation:* Mandatory telemetry and proactive alerting for any processing anomaly.
- **Risk: Data Duplication.** 
    - *Mitigation:* Implementation of idempotent load patterns in ClickHouse.
- **Risk: Environment Inconsistency.** 
    - *Mitigation:* Strict adherence to Docker-based deployment.
- **Failure Mode: Malformed Input.** 
    - *Action:* Ingestion flow must reject invalid CSVs and log the specific integrity violation.
- **Failure Mode: Resource Exhaustion.** 
    - *Action:* Monitoring of MinIO/ClickHouse capacity and ETL container resources.

## 7. Required Deliverables
- [ ] **GEMINI.md:** (This document).
- [ ] **Data Models:** Conceptual, Logical, and Physical schemas.
- [ ] **Architecture Diagram:** Mermaid-based diagram in `README.md`.
- [ ] **Infrastructure/ETL Code:** Containerized solution (Docker).
- [ ] **Decision Log:** Section in `README.md` documenting trade-offs and discarded alternatives.

## 8. Assumptions
- The source data consists of two relational entities: `Orders` and `Order Details`.
- Input files are provided in CSV format.
- Daily volume is approximately 100,000 orders.
- The system will run in a containerized environment (Docker).

## 9. Open Questions (Ambiguities)
- [ ] **Data Types:** What are the specific SQL types and constraints for fields like `freight` (Decimal precision?) or `order_date` (Timezone?)?
- [ ] **Observability Stack:** While telemetry is required, which specific tools are preferred for log aggregation and metric visualization (e.g., Prometheus/Grafana or ClickHouse-native)?
- [ ] **SLA/SLO:** What is the maximum acceptable latency between order generation and visibility in Streamlit?
- [ ] **Retention:** How long should raw files be kept in MinIO before archival?

## 10. Self-Critique
- **Derived from spec/00_problem.md:** Every constraint and goal is mapped directly to the problem statement.
- **No Hallucinations:** Technologies like AWS (found in the existing `documents/GEMINI.md`) were ignored in favor of the requested MinIO/ClickHouse stack.
- **Measurable Criteria:** Converted vague "high volume" into specific throughput estimates.

## 11. Execution Checklist
1. [ ] Validate `northwind_orders.csv` and `northwind_order_details.csv` schemas.
2. [ ] Design Conceptual and Logical Data Models.
3. [ ] Set up local development environment with Docker (MinIO, ClickHouse, Streamlit).
4. [ ] Implement CSV Ingestion with integrity checks.
5. [ ] Develop ETL transformation logic.
6. [ ] Implement Idempotent Load to ClickHouse.
7. [ ] Build Streamlit Dashboard.
8. [ ] Integrate Telemetry (logs/metrics) across all components.
9. [ ] Document architecture and trade-offs in `README.md`.
