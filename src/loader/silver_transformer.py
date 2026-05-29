import pandas as pd
import clickhouse_connect
from common.config import config
from common.logger import logger
from common.decorators import retry_db_operation

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

    @retry_db_operation(max_retries=3)
    def transform_and_load(self):
        """Executa o JOIN, limpeza e carga na camada Silver."""
        logger.info("Iniciando processamento da Camada Silver")
        
        try:
            # 1. Extração da Bronze (As views já possuem os nomes corretos)
            orders_query = """
                SELECT order_id, customer_id, order_date, ship_country, ship_city, source_file 
                FROM northwind.bronze_orders
            """
            details_query = """
                SELECT order_id, product_id, unit_price, quantity, discount 
                FROM northwind.bronze_order_details
            """
            
            df_orders = self.client.query_df(orders_query)
            df_details = self.client.query_df(details_query)

            if df_orders.empty or df_details.empty:
                logger.warning("Camada Bronze vazia ou sem dados para as views. Verifique a carga Raw.")
                return 0

            # 2. Unificação (JOIN)
            logger.info("Realizando Join entre Orders e Details")
            # Forçamos o tipo para string antes do merge para garantir compatibilidade
            df_orders['order_id'] = df_orders['order_id'].astype(str)
            df_details['order_id'] = df_details['order_id'].astype(str)
            
            # Adicionar freight no query de extração (Bronze -> Silver)
            orders_query = """
                SELECT order_id, customer_id, order_date, ship_country, ship_city, source_file, freight 
                FROM northwind.bronze_orders
            """
            df_orders = self.client.query_df(orders_query)
            df_orders['order_id'] = df_orders['order_id'].astype(str)

            df_silver = pd.merge(df_orders, df_details, on="order_id", how="inner")

            # 3. Sanitização e Tipagem
            logger.info("Aplicando sanitização e regras de negócio")
            
            df_silver['customer_id'] = df_silver['customer_id'].str.strip()
            df_silver['ship_country'] = df_silver['ship_country'].str.strip()
            df_silver['ship_city'] = df_silver['ship_city'].str.strip()

            df_silver['order_id'] = pd.to_numeric(df_silver['order_id'])
            df_silver['product_id'] = pd.to_numeric(df_silver['product_id'])
            df_silver['order_date'] = pd.to_datetime(df_silver['order_date'])
            df_silver['unit_price'] = pd.to_numeric(df_silver['unit_price'])
            df_silver['quantity'] = pd.to_numeric(df_silver['quantity'])
            df_silver['discount'] = pd.to_numeric(df_silver['discount'])
            df_silver['freight'] = pd.to_numeric(df_silver['freight'])

            # Cálculo de Valor Total
            df_silver['total_price'] = df_silver['unit_price'] * df_silver['quantity'] * (1 - df_silver['discount'])

            # 4. Injeção de Audit Trail
            df_silver['batch_id'] = self.batch_id

            # 5. Seleção das colunas finais conforme Modelo Físico
            final_columns = [
                'order_id', 'customer_id', 'order_date', 'product_id', 
                'unit_price', 'quantity', 'discount', 'freight', 'total_price',
                'ship_country', 'ship_city', 'batch_id', 'source_file'
            ]
            
            # Verificação de segurança: garantir que todas as colunas existem
            missing = [c for c in final_columns if c not in df_silver.columns]
            if missing:
                logger.error(f"Colunas ausentes após o merge: {missing}")
                logger.debug(f"Colunas disponíveis: {df_silver.columns.tolist()}")
                raise KeyError(f"Colunas ausentes no DataFrame: {missing}")

            df_to_load = df_silver[final_columns]

            # 6. Carga na Silver
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
