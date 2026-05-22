import clickhouse_connect
from common.config import config
from common.logger import logger

class GoldAggregator:
    """Componente responsável pela Camada Gold (Silver -> Gold)."""

    def __init__(self):
        self.client = clickhouse_connect.get_client(
            host=config.CH_HOST,
            port=config.CH_PORT,
            username=config.CH_USER,
            password=config.CH_PASSWORD
        )

    def aggregate_and_load(self):
        """Dispara as queries de agregação para as tabelas Gold."""
        logger.info("Iniciando processamento da Camada Gold")
        
        try:
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

            logger.info("Camada Gold finalizada com sucesso")
            return True

        except Exception as e:
            logger.error(f"Erro na agregação Gold: {str(e)}")
            raise
