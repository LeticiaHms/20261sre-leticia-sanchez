# Documentação da Camada Gold - Northwind Analytics

Este documento detalha os esquemas físicos das tabelas na camada Gold, focadas em Business Intelligence e suporte à decisão.

## 1. Growth & Forecasting (`gold_revenue_monthly`)
Tabela para análise de tendência de receita e volume de pedidos por mês e país.

| Coluna | Tipo | Descrição |
| :--- | :--- | :--- |
| `month` | Date | Primeiro dia do mês de referência. |
| `ship_country` | String | País de destino dos pedidos. |
| `total_revenue` | Decimal(18, 4) | Soma do valor líquido dos pedidos. |
| `order_count` | UInt32 | Contagem de pedidos únicos. |
| `loaded_at` | DateTime | Timestamp de carga na camada Gold. |

## 2. Logística & SLA (`gold_logistics_performance`)
Métricas de eficiência de entrega e aderência ao SLA (shipped_date <= required_date).

| Coluna | Tipo | Descrição |
| :--- | :--- | :--- |
| `ship_country` | String | País de destino. |
| `avg_days_to_ship` | Float64 | Média de dias entre o pedido e o envio. |
| `avg_delay_days` | Float64 | Média de dias de atraso (shipped - required). |
| `on_time_rate` | Float64 | Porcentagem de pedidos entregues no prazo (0-1). |

## 3. Geografia (`gold_geographic_distribution`)
Concentração de mercado por cidade.

| Coluna | Tipo | Descrição |
| :--- | :--- | :--- |
| `ship_country` | String | País. |
| `ship_city` | String | Cidade. |
| `total_revenue` | Decimal(18, 4) | Receita total acumulada. |
| `unique_customers` | UInt32 | Quantidade de clientes únicos que compraram. |

## 4. Portfólio (`gold_top_products`)
Ranking de produtos por faturamento.

| Coluna | Tipo | Descrição |
| :--- | :--- | :--- |
| `product_id` | UInt32 | ID do produto. |
| `total_revenue` | Decimal(18, 4) | Faturamento bruto. |
| `total_quantity` | UInt32 | Volume total de unidades vendidas. |

## 5. Operação (`gold_order_status`)
Visão operacional de pedidos pendentes vs enviados.

| Coluna | Tipo | Descrição |
| :--- | :--- | :--- |
| `status` | String | 'Shipped' ou 'Pending'. |
| `order_count` | UInt32 | Volume de pedidos. |
| `total_revenue` | Decimal(18, 4) | Soma do frete (proxy de custo logístico). |

## 6. Retenção (`gold_customer_retention`)
Saúde da base de clientes e taxa de fidelidade.

| Coluna | Tipo | Descrição |
| :--- | :--- | :--- |
| `total_customers` | UInt32 | Base total de clientes. |
| `repeat_customers` | UInt32 | Clientes com mais de 1 pedido. |
| `rebuy_rate` | Float64 | Taxa de recompra (repeat / total). |

## 7. Vendas (`gold_seller_performance`)
Produtividade da força de vendas.

| Coluna | Tipo | Descrição |
| :--- | :--- | :--- |
| `employee_id` | String | ID do funcionário. |
| `total_revenue` | Decimal(18, 4) | Receita gerada pelo vendedor. |
| `order_count` | UInt32 | Quantidade de pedidos fechados. |
