# Northwind Data Pipeline 🚀

[![CI](https://github.com/LeticiaHms/mba-project-sre/actions/workflows/ci.yml/badge.svg)](https://github.com/LeticiaHms/mba-project-sre/actions/workflows/ci.yml)

## 6.1 Objeto do Projeto
Este projeto automatiza o fluxo de dados da Northwind, uma distribuidora de alimentos e bebidas, para resolver o atraso entre a realização de vendas e a visibilidade gerencial. Utilizando o dataset clássico de pedidos e detalhes de pedidos (Orders e Order Details), a solução processa um volume de aproximadamente 100 mil transações diárias, garantindo que gestores tenham acesso a indicadores de faturamento, performance de vendedores e eficiência logística em tempo real, eliminando processos manuais e falhas de conciliação de dados.

## 6.2 Arquitetura Adotada
O sistema adota o padrão **Arquitetura Medalhão** (Bronze/Silver/Gold) para garantir rastreabilidade e qualidade analítica.

```mermaid
graph LR
    subgraph Inbound[Fontes de Dados]
        CSV[CSVs Locais] --> MINIO[MinIO Landing Zone]
    end
    
    subgraph Processing[ETL Engine - Python]
        MINIO --> BRONZE[Bronze Loader]
        BRONZE --> SILVER[Silver Transformer]
        SILVER --> GOLD[Gold Aggregator]
    end
    
    subgraph Storage[Analytical DB - ClickHouse]
        BRONZE -.-> T_RAW[Raw/Bronze JSON]
        SILVER -.-> T_SILV[Silver Unified Table]
        GOLD -.-> T_GOLD[Gold Business Marts]
    end
    
    subgraph Viz[Observabilidade & BI]
        T_GOLD --> DASH[Streamlit Dashboard]
        PROMETHEUS[Logs/Metrics] -.-> SRE[Alerting System]
    end
```

### Componentes e Táticas de Engenharia (Bass & ATAM)
- **MinIO (Landing Zone):** Storage compatível with S3 that acts as an immutable landing zone for CSV files.
- **Bronze Loader (JSON Append-Only):** Persists raw data in ClickHouse; uses **Resource Management (Chunksize)** tactics to avoid memory overflow under massive load.
- **Silver Transformer (ReplacingMergeTree):** Unifies and types data; implements **Idempotency** tactics to guarantee uniqueness even in case of reprocessing.
- **Gold Aggregator (Business Marts):** Generates BI aggregates; uses **Retry with Backoff** via decorator for database connection resilience.
- **Streamlit Dashboard:** Visualization interface that uses **Caching** (`@st.cache_data`) to reduce query latency.

## 6.3 Execução em Ambiente Local (Quick Start)
### Pré-requisitos
- Docker & Docker Compose instalados.
- 4GB de RAM livre para os containers.

### Comando Único de Provisionamento
```bash
# Sobe MinIO, ClickHouse e Streamlit + Executa o Pipeline de Dados
docker-compose up -d && sleep 5 && docker-compose run --rm etl-engine python src/batch_manager.py
```
**Estimativa de tempo:** < 5 minutos para o ambiente estar 100% funcional.

## 6.4 Validação do Funcionamento
### Verificação do Pipeline
- **Logs e Métricas Reais:** Consulte as [Evidências de Execução](documents/EXECUTION_EVIDENCE.md) para ver logs e resultados de performance.
- **Badge de CI:** O status do build no topo deste README confirma a integridade do código.

### Acesso aos Serviços
- **Dashboard Streamlit:** [http://localhost:8501](http://localhost:8501)
- **MinIO Console:** [http://localhost:9001](http://localhost:9001)
- **ClickHouse Client:** `docker exec -it clickhouse clickhouse-client`

### Testes de Performance (SRE)
```bash
# Executar bateria de testes de carga (K6)
npm run test:load
```

## 6.5 Aprendizados e Trade-offs
### Decisões e Alternativas
- **ClickHouse vs Postgres:** Optamos pelo ClickHouse pela sua capacidade superior de compressão e velocidade em agregações colunares.
- **Medalhão (Bronze/Silver/Gold):** Implementado para permitir o re-processamento total a partir dos dados brutos.

### Dívida Técnica e Melhorias Produtivas
- **Orquestração:** Atualmente o `BatchManager` é manual; em produção, utilizaríamos **Apache Airflow**.
- **Monitoramento:** A simulação de alertas deve ser substituída por uma integração real com **Grafana**.
- **Segurança:** As credenciais estão simplificadas; em produção, seria obrigatório o uso de um **Secret Manager**.

---

## 📂 Central de Documentação
Para acessar o detalhamento completo dos requisitos, modelagem, planos de teste e arquitetura, clique no link abaixo:

👉 **[Acesse aqui o Índice de Documentação Técnica](documents/00_index.md)**

---
*Mantido por SRE/Data Engineering Team*
