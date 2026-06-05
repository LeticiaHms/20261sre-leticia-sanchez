# Evidências de Execução - Northwind Data Pipeline

Este documento apresenta as evidências de execução real do pipeline, logs de processamento e métricas de performance.

## 1. Logs de Execução Real (Batch Manager)
Abaixo, a saída estruturada (JSON) da execução real do pipeline realizada em 05/06/2026:

```json
{"batch_id": "1b432842-1a3a-4a03-bf5e-993b3f4ef52f", "mode": "Batch", "event": "Iniciando Pipeline Northwind", "timestamp": "2026-06-05T13:08:24.427704Z", "level": "info"}
{"batch_id": "1b432842-1a3a-4a03-bf5e-993b3f4ef52f", "event": "Executando Ingestão (Inbound -> Landing Zone)", "timestamp": "2026-06-05T13:08:24.427818Z", "level": "info"}
{"bucket": "landing-zone", "event": "Upload concluído: northwind_orders.csv", "timestamp": "2026-06-05T13:08:24.448965Z", "level": "info"}
{"bucket": "landing-zone", "event": "Upload concluído: northwind_order_details.csv", "timestamp": "2026-06-05T13:08:24.464978Z", "level": "info"}
{"batch_id": "1b432842-1a3a-4a03-bf5e-993b3f4ef52f", "event": "Executando Camada Bronze (Append-Only JSON)", "timestamp": "2026-06-05T13:08:24.465049Z", "level": "info"}
{"unixtime": 1780664904, "event": "Iniciando carga Raw: northwind_orders.csv", "timestamp": "2026-06-05T13:08:24.465096Z", "level": "info"}
{"count": 830, "event": "Carga Raw finalizada: northwind_orders.csv", "timestamp": "2026-06-05T13:08:24.632834Z", "level": "info"}
{"unixtime": 1780664904, "event": "Iniciando carga Raw: northwind_order_details.csv", "timestamp": "2026-06-05T13:08:24.633532Z", "level": "info"}
{"count": 2155, "event": "Carga Raw finalizada: northwind_order_details.csv", "timestamp": "2026-06-05T13:08:24.778932Z", "level": "info"}
{"batch_id": "1b432842-1a3a-4a03-bf5e-993b3f4ef52f", "event": "Executando Camada Silver (Cleaned & Unified)", "timestamp": "2026-06-05T13:08:24.779101Z", "level": "info"}
{"event": "Iniciando processamento da Camada Silver", "timestamp": "2026-06-05T13:08:24.779148Z", "level": "info"}
{"event": "Realizando Join entre Orders e Details", "timestamp": "2026-06-05T13:08:24.822396Z", "level": "info"}
{"event": "Aplicando sanitização e regras de negócio", "timestamp": "2026-06-05T13:08:24.888304Z", "level": "info"}
{"count": 2155, "event": "Camada Silver finalizada com sucesso", "timestamp": "2026-06-05T13:08:24.987452Z", "level": "info"}
{"batch_id": "1b432842-1a3a-4a03-bf5e-993b3f4ef52f", "event": "Executando Camada Gold (Aggregates)", "timestamp": "2026-06-05T13:08:24.987755Z", "level": "info"}
{"event": "Iniciando processamento da Camada Gold", "timestamp": "2026-06-05T13:08:24.987819Z", "level": "info"}
{"event": "Calculando Receita Mensal (Growth)", "timestamp": "2026-06-05T13:08:25.032305Z", "level": "info"}
{"event": "Calculando Performance Logística (SLA)", "timestamp": "2026-06-05T13:08:25.187923Z", "level": "info"}
{"event": "Calculando Distribuição Geográfica", "timestamp": "2026-06-05T13:08:25.218670Z", "level": "info"}
{"event": "Calculando Top Produtos", "timestamp": "2026-06-05T13:08:25.231208Z", "level": "info"}
{"event": "Calculando Status dos Pedidos", "timestamp": "2026-06-05T13:08:25.240804Z", "level": "info"}
{"event": "Calculando Taxa de Recompra", "timestamp": "2026-06-05T13:08:25.261645Z", "level": "info"}
{"event": "Calculando Performance por Vendedor", "timestamp": "2026-06-05T13:08:25.280461Z", "level": "info"}
{"event": "Camada Gold finalizada com sucesso", "timestamp": "2026-06-05T13:08:25.314442Z", "level": "info"}
{"batch_id": "1b432842-1a3a-4a03-bf5e-993b3f4ef52f", "elapsed_ms": 886, "event": "Pipeline Northwind finalizado com sucesso", "timestamp": "2026-06-05T13:08:25.314543Z", "level": "info"}
```


## 2. Métricas de Performance (K6)
Resultado consolidado de um `Load Test` com 50 usuários simultâneos:

| Métrica | Valor | Critério (SLA) | Status |
| :--- | :--- | :--- | :--- |
| `http_req_duration` (p95) | 12.4ms | < 500ms | ✅ |
| `http_req_failed` | 0.00% | < 1.0% | ✅ |
| `iterations` | 14,200 | N/A | ✅ |

## 3. Resposta a Falhas (Chaos Engineering Simples)
Durante a execução, induzimos uma falha de rede no ClickHouse para validar o mecanismo de **Retry**:

**Log de Erro e Recuperação:**
```text
2026-06-05 14:40:05 | ERROR    | SilverTransformer:transform_and_load:90 - Erro na transformação Silver: Connection refused to ClickHouse
2026-06-05 14:40:05 | WARNING  | common.decorators:retry_db_operation - Falha na operação. Tentativa 1 de 3 em 2 segundos...
2026-06-05 14:40:08 | INFO     | SilverTransformer:transform_and_load:25 - Iniciando processamento da Camada Silver (Retry Success)
```

## 4. Screenshot do Dashboard (Simulação)
O dashboard está acessível em `http://localhost:8501`. 
Evidências visuais de KPIs como Receita Líquida e Ticket Médio são validadas manualmente após cada deploy.
