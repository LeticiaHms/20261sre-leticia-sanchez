import pandas as pd
import clickhouse_connect
from common.config import config
from common.logger import logger

class SilverTransformer:
    """Transformador responsável pela Camada Silver (Bronze -> Silver)."""

    def __init__(self, batch_id):
        self.client = clickhouse_connect.get_client(
            host=config.CH_HOST,
            port=config.CH_PORT,
            username=config.CH_USER,
            password=config.CH_PASSWORD
        )
        self.batch_id = batch_id

    def transform_and_load(self):
        """Executa o JOIN, limpeza e carga na camada Silver."""
        logger.info("Iniciando processamento da Camada Silver")
        
        try:
            # 1. Extração da Bronze (via Views)
            df_orders = self.client.query_df("SELECT * FROM northwind.bronze_orders")
            df_details = self.client.query_df("SELECT * FROM northwind.bronze_order_details")

            if df_orders.empty or df_details.empty:
                logger.warning("Camada Bronze vazia. Abortando Silver.")
                return 0

            # 2. Unificação (JOIN)
            logger.info("Realizando Join entre Orders e Details")
            df_silver = pd.merge(
                df_orders, 
                df_details, 
                on="order_id", 
                how="inner", 
                suffixes=('_ord', '_det')
            )

            # 3. Sanitização e Tipagem (RF-09)
            logger.info("Aplicando sanitização e regras de negócio")
            
            # Remover espaços em branco (Trim)
            df_silver['customer_id'] = df_silver['customer_id'].str.strip()
            df_silver['ship_country'] = df_silver['ship_country'].str.strip()
            df_silver['ship_city'] = df_silver['ship_city'].str.strip()

            # Conversão de Tipos
            df_silver['order_id'] = pd.to_numeric(df_silver['order_id'])
            df_silver['product_id'] = pd.to_numeric(df_silver['product_id'])
            df_silver['order_date'] = pd.to_datetime(df_silver['order_date'])
            df_silver['unit_price'] = pd.to_numeric(df_silver['unit_price'])
            df_silver['quantity'] = pd.to_numeric(df_silver['quantity'])
            df_silver['discount'] = pd.to_numeric(df_silver['discount'])

            # Cálculo de Valor Total
            df_silver['total_price'] = df_silver['unit_price'] * df_silver['quantity'] * (1 - df_silver['discount'])

            # 4. Injeção de Audit Trail (RF-10)
            df_silver['batch_id'] = self.batch_id
            # loaded_at e source_file já vêm da Bronze view ou são gerados pelo ClickHouse

            # 5. Seleção das colunas finais conforme Modelo Físico
            final_columns = [
                'order_id', 'customer_id', 'order_date', 'product_id', 
                'unit_price', 'quantity', 'discount', 'total_price',
                'ship_country', 'ship_city', 'batch_id', 'source_file'
            ]
            df_to_load = df_silver[final_columns]

            # 6. Carga na Silver (Idempotência garantida pelo ReplacingMergeTree)
            self.client.insert_df(
                'silver_orders_unified',
                df_to_load,
                database='northwind'
            )

            logger.info("Camada Silver finalizada com sucesso", count=len(df_to_load))
            return len(df_to_load)

        except Exception as e:
            logger.error(f"Erro na transformação Silver: {str(e)}")
            raise
