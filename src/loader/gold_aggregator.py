import clickhouse_connect
from common.config import config
from common.logger import logger
from common.decorators import retry_db_operation

class GoldAggregator:
    """Componente responsável pela Camada Gold (Silver -> Gold)."""

    def __init__(self):
        self.client = clickhouse_connect.get_client(
            host=config.CH_HOST,
            port=config.CH_PORT,
            username=config.CH_USER,
            password=config.CH_PASSWORD
        )

    @retry_db_operation(max_retries=3)
    def aggregate_and_load(self):
        """Dispara as queries de agregação para as tabelas Gold."""
        logger.info("Iniciando processamento da Camada Gold")
        
        try:
            # 0. Limpeza para Idempotência (Garantir que não haverá duplicados de execuções anteriores)
            gold_tables = [
                "gold_revenue_monthly", "gold_logistics_performance", 
                "gold_geographic_distribution", "gold_top_products",
                "gold_order_status", "gold_customer_retention", "gold_seller_performance"
            ]
            for table in gold_tables:
                self.client.command(f"TRUNCATE TABLE northwind.{table}")

            # 1. Growth: Receita Mensal
            logger.info("Calculando Receita Mensal (Growth)")
            self.client.command("""
                INSERT INTO northwind.gold_revenue_monthly
                SELECT
                    toStartOfMonth(order_date) as month,
                    ship_country,
                    sum(total_price) as total_revenue,
                    count(DISTINCT order_id) as order_count,
                    now()
                FROM northwind.silver_orders_unified
                GROUP BY month, ship_country
            """)

            # 2. Logística & SLA: Performance de Envio
            # Nota: Precisamos buscar as datas de envio que ficaram na Bronze ou adicionar na Silver
            # Para este MVP, vamos assumir que a Silver tem os dados necessários ou agregar via Join
            logger.info("Calculando Performance Logística (SLA)")
            # Como a Silver atual não tem shipped_date, vamos criar uma query que busca da Bronze
            self.client.command("""
                INSERT INTO northwind.gold_logistics_performance
                SELECT
                    ship_country,
                    avg(dateDiff('day', toDateTime(order_date), toDateTime(shipped_date))) as avg_days_to_ship,
                    avg(dateDiff('day', toDateTime(required_date), toDateTime(shipped_date))) as avg_delay_days,
                    countIf(toDateTime(shipped_date) <= toDateTime(required_date)) / count(*) as on_time_rate,
                    now()
                FROM northwind.bronze_orders
                WHERE shipped_date != '' AND required_date != ''
                GROUP BY ship_country
            """)

            # 3. Geografia: Concentração por Cidade
            logger.info("Calculando Distribuição Geográfica")
            self.client.command("""
                INSERT INTO northwind.gold_geographic_distribution
                SELECT
                    ship_country,
                    ship_city,
                    sum(total_price) as total_revenue,
                    count(DISTINCT customer_id) as unique_customers,
                    now()
                FROM northwind.silver_orders_unified
                GROUP BY ship_country, ship_city
            """)

            # 4. Portfólio: Top Produtos
            logger.info("Calculando Top Produtos")
            self.client.command("""
                INSERT INTO northwind.gold_top_products
                SELECT
                    product_id,
                    sum(total_price) as total_revenue,
                    sum(quantity) as total_quantity,
                    now()
                FROM northwind.silver_orders_unified
                GROUP BY product_id
            """)

            # 5. Operação: Status dos Pedidos
            logger.info("Calculando Status dos Pedidos")
            self.client.command("""
                INSERT INTO northwind.gold_order_status
                SELECT
                    multiIf(shipped_date = '', 'Pending', 'Shipped') as status,
                    count(DISTINCT order_id) as order_count,
                    sum(toDecimal128(freight, 4)) as total_revenue,
                    now()
                FROM northwind.bronze_orders
                GROUP BY status
            """)

            # 6. Retenção: Taxa de Recompra
            logger.info("Calculando Taxa de Recompra")
            self.client.command("""
                INSERT INTO northwind.gold_customer_retention
                WITH customer_orders AS (
                    SELECT customer_id, count(DISTINCT order_id) as orders
                    FROM northwind.silver_orders_unified
                    GROUP BY customer_id
                )
                SELECT
                    count(*) as total_customers,
                    countIf(orders > 1) as repeat_customers,
                    repeat_customers / total_customers as rebuy_rate,
                    now()
                FROM customer_orders
            """)

            # 7. Vendas: Performance por Vendedor
            logger.info("Calculando Performance por Vendedor")
            self.client.command("""
                INSERT INTO northwind.gold_seller_performance
                SELECT
                    employee_id,
                    sum(total_price) as total_revenue,
                    count(DISTINCT silver.order_id) as order_count,
                    now()
                FROM northwind.silver_orders_unified silver
                JOIN northwind.bronze_orders bronze ON silver.order_id = toUInt64(bronze.order_id)
                GROUP BY employee_id
            """)

            logger.info("Camada Gold finalizada com sucesso")
            return True

        except Exception as e:
            logger.error(f"Erro na agregação Gold: {str(e)}")
            raise
