# System Design - Northwind Data Pipeline

Este blueprint detalha a implementação técnica da arquitetura Medalhão processada em lote.

## 1. Estratégia de Camadas no ClickHouse

| Camada | Tabela Exemplo | Engine ClickHouse | Descrição |
| :--- | :--- | :--- | :--- |
| **Bronze** | `bronze_orders` | `MergeTree` | Dados brutos do CSV + `ingested_at`. |
| **Silver** | `silver_orders_unified` | `ReplacingMergeTree` | Dados limpos, tipados, `Orders` + `Details` unidos. |
| **Gold** | `gold_daily_sales` | `SummingMergeTree` | Agregados pré-calculados para o dashboard. |

## 2. Componentes e Fluxo de Código

### 2.1 Batch Manager (`src/batch_manager.py`)
Controlador central que dispara a execução das camadas em ordem:
1. `Ingestor -> MinIO (Landing)`
2. `BronzeLoader -> ClickHouse (Bronze)`
3. `SilverTransformer -> ClickHouse (Silver)`
4. `GoldAggregator -> ClickHouse (Gold)`

### 2.2 Logging Estruturado (`src/common/logger.py`)
Utiliza `structlog` para garantir que cada etapa batch registre:
- `batch_id`: Identificador único do lote.
- `layer`: Bronze, Silver ou Gold.
- `records_processed`: Quantidade de linhas.
- `status`: SUCCESS/ERROR.

## 3. Esquema de Dados Detalhado (Silver)

A camada Silver é o coração da linhagem:
- `order_id`, `product_id` (PK Composta)
- `unit_price`, `quantity`, `discount`
- `total_price` (Calculado)
- `customer_id`, `order_date`, `ship_country`
- `source_file` (Audit Trail)
- `silver_loaded_at` (Audit Trail)

## 4. Estratégia de Idempotência
Para garantir que o processamento batch possa ser repetido:
- **Bronze:** `TRUNCATE` da partição ou do lote antes do `INSERT`.
- **Silver/Gold:** Uso de `ReplacingMergeTree` baseado na chave primária de negócio, garantindo que a versão mais recente do dado prevaleça.
