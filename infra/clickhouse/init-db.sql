-- Habilitar suporte experimental para JSON se necessário (em versões recentes)
SET allow_experimental_object_type = 1;

-- 0. CAMADA RAW (APPEND-ONLY)
CREATE DATABASE IF NOT EXISTS northwind_raw;

CREATE TABLE IF NOT EXISTS northwind_raw.ingestion
(
    unixtime Int64,
    data     String, -- Armazenado como String (JSON) para máxima compatibilidade
    tag      LowCardinality(String)
)
ENGINE = MergeTree
ORDER BY (tag, unixtime);

-- Create Northwind Analytical Database
CREATE DATABASE IF NOT EXISTS northwind;

--------------------------------------------------------------------------------
-- 1. CAMADA BRONZE (EMERGENT VIEWS)
-- Views que expõem a execução mais recente da camada Raw como tabelas lógicas
--------------------------------------------------------------------------------

CREATE OR REPLACE VIEW bronze_orders AS
WITH (SELECT max(unixtime) FROM northwind_raw.ingestion WHERE tag = 'northwind_orders.csv') AS latest_batch
SELECT
    JSONExtractString(data, 'order_id') as order_id,
    JSONExtractString(data, 'customer_id') as customer_id,
    JSONExtractString(data, 'employee_id') as employee_id,
    JSONExtractString(data, 'order_date') as order_date,
    JSONExtractString(data, 'required_date') as required_date,
    JSONExtractString(data, 'shipped_date') as shipped_date,
    JSONExtractString(data, 'ship_via') as ship_via,
    JSONExtractString(data, 'freight') as freight,
    JSONExtractString(data, 'ship_name') as ship_name,
    JSONExtractString(data, 'ship_address') as ship_address,
    JSONExtractString(data, 'ship_city') as ship_city,
    JSONExtractString(data, 'ship_region') as ship_region,
    JSONExtractString(data, 'ship_postal_code') as ship_postal_code,
    JSONExtractString(data, 'ship_country') as ship_country,
    tag as source_file,
    toDateTime(latest_batch) as ingested_at
FROM northwind_raw.ingestion
WHERE tag = 'northwind_orders.csv' AND unixtime = latest_batch;

CREATE OR REPLACE VIEW bronze_order_details AS
WITH (SELECT max(unixtime) FROM northwind_raw.ingestion WHERE tag = 'northwind_order_details.csv') AS latest_batch
SELECT
    JSONExtractString(data, 'order_id') as order_id,
    JSONExtractString(data, 'product_id') as product_id,
    JSONExtractString(data, 'unit_price') as unit_price,
    JSONExtractString(data, 'quantity') as quantity,
    JSONExtractString(data, 'discount') as discount,
    tag as source_file,
    toDateTime(latest_batch) as ingested_at
FROM northwind_raw.ingestion
WHERE tag = 'northwind_order_details.csv' AND unixtime = latest_batch;

--------------------------------------------------------------------------------
-- 2. CAMADA SILVER (UNIFIED & CLEANED)
-- Dados unificados, tipados e com idempotência garantida
--------------------------------------------------------------------------------

CREATE TABLE IF NOT EXISTS silver_orders_unified (
    order_id UInt64,
    customer_id String,
    order_date DateTime,
    product_id UInt32,
    unit_price Decimal(12, 4),
    quantity UInt16,
    discount Float32,
    freight Decimal(12, 4),
    total_price Decimal(12, 4), -- unit_price * quantity * (1 - discount)
    ship_country String,
    ship_city String,
    -- Audit Trail
    batch_id String,
    source_file String,
    silver_loaded_at DateTime DEFAULT now()
) ENGINE = ReplacingMergeTree(silver_loaded_at)
ORDER BY (order_id, product_id);

--------------------------------------------------------------------------------
-- 3. CAMADA GOLD (BUSINESS INTELLIGENCE)
-- Tabelas agregadas para responder eixos de decisão de negócio
--------------------------------------------------------------------------------

-- 1. Growth & Forecasting: Receita mensal por país e categoria (inferida por product_id)
CREATE TABLE IF NOT EXISTS gold_revenue_monthly (
    month Date,
    ship_country String,
    total_revenue Decimal(18, 4),
    order_count UInt32,
    loaded_at DateTime DEFAULT now()
) ENGINE = MergeTree()
ORDER BY (month, ship_country);

-- 2. Logística & SLA: Tempo médio de envio vs SLA prometido
-- Diferença entre shipped_date e required_date
CREATE TABLE IF NOT EXISTS gold_logistics_performance (
    ship_country String,
    avg_days_to_ship Float64, -- order_date -> shipped_date
    avg_delay_days Float64,   -- shipped_date -> required_date (atraso)
    on_time_rate Float64,     -- % de pedidos enviados antes do required_date
    loaded_at DateTime DEFAULT now()
) ENGINE = MergeTree()
ORDER BY ship_country;

-- 3. Expansão Regional: Concentração por País e Cidade
CREATE TABLE IF NOT EXISTS gold_geographic_distribution (
    ship_country String,
    ship_city String,
    total_revenue Decimal(18, 4),
    unique_customers UInt32,
    loaded_at DateTime DEFAULT now()
) ENGINE = MergeTree()
ORDER BY (ship_country, total_revenue);

-- 4. Portfólio: Top Produtos por Receita
CREATE TABLE IF NOT EXISTS gold_top_products (
    product_id UInt32,
    total_revenue Decimal(18, 4),
    total_quantity UInt32,
    loaded_at DateTime DEFAULT now()
) ENGINE = MergeTree()
ORDER BY total_revenue;

-- 5. Operação: Volume de Pedidos por Status
CREATE TABLE IF NOT EXISTS gold_order_status (
    status String,
    order_count UInt32,
    total_revenue Decimal(18, 4),
    loaded_at DateTime DEFAULT now()
) ENGINE = MergeTree()
ORDER BY status;

-- 6. Retenção: Taxa de Recompra
CREATE TABLE IF NOT EXISTS gold_customer_retention (
    total_customers UInt32,
    repeat_customers UInt32,
    rebuy_rate Float64,
    loaded_at DateTime DEFAULT now()
) ENGINE = MergeTree()
ORDER BY loaded_at;

-- 7. Vendas: Performance por Vendedor
CREATE TABLE IF NOT EXISTS gold_seller_performance (
    employee_id String,
    total_revenue Decimal(18, 4),
    order_count UInt32,
    loaded_at DateTime DEFAULT now()
) ENGINE = MergeTree()
ORDER BY total_revenue;
