# Plano de Teste de Carga e Performance

Focado na performance do pipeline Northwind operando em lotes diários de 100.000 registros.

## 1. Objetivos do Teste
- Medir o tempo de processamento end-to-end (Lote -> Gold).
- Validar o impacto de performance na transição entre camadas no ClickHouse.
- Garantir que a geração de logs JSON não introduza overhead significativo.

## 2. Cenários de Teste Batch

### 2.1 Performance E2E (SRE Throughput)
- **TC-12: Ciclo Completo Medalhão**
    - **Cenário:** Processamento de 100k registros do Ingestor até a Camada Gold.
    - **SLO:** Total < 120 minutos.
    - **Perfil:** 
        - Bronze Load: ~10 min.
        - Silver Transform: ~60 min (CPU intensive).
        - Gold Aggregation: ~10 min.
    - **Evidência:** Timestamps nos logs estruturados de início e fim de cada camada.

### 2.2 Escalabilidade de Transformação
- **TC-19: Paralelização Silver**
    - **Cenário:** Executar a camada Silver com 1 vs 3 workers.
    - **Objetivo:** Validar se a limpeza e unificação de 100k linhas escala linearmente.
    - **SLO:** Eficiência > 80%.

### 2.3 Performance de Consulta (UI Experience)
- **TC-14: Dashboard Response (Gold Access)**
    - **Cenário:** Streamlit consultando a camada Gold pré-agregada com 1M+ registros.
    - **SLO:** < 5 segundos de carregamento.

## 3. Observabilidade e Telemetria
- **Logs:** Auditoria dos campos `layer`, `batch_id` e `duration_ms` para identificar gargalos em camadas específicas.
- **Resources:** Monitoramento de uso de memória do container ETL durante o processamento da camada Silver.
