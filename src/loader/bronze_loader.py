import time
import json
import pandas as pd
import clickhouse_connect
from common.config import config
from common.logger import logger

class BronzeLoader:
    """Lógica de ingestão Append-Only JSON no ClickHouse."""

    def __init__(self):
        self.client = clickhouse_connect.get_client(
            host=config.CH_HOST,
            port=config.CH_PORT,
            username=config.CH_USER,
            password=config.CH_PASSWORD
        )
        self.unixtime = int(time.time())

    def _validate_schema(self, df, tag):
        """Valida se as colunas obrigatórias estão presentes no CSV."""
        required_columns = {
            "northwind_orders.csv": [
                "order_id", "customer_id", "employee_id", "order_date", 
                "required_date", "shipped_date", "ship_via", "freight"
            ],
            "northwind_order_details.csv": [
                "order_id", "product_id", "unit_price", "quantity", "discount"
            ]
        }
        
        if tag in required_columns:
            missing = [col for col in required_columns[tag] if col not in df.columns]
            if missing:
                error_msg = f"Schema inválido para {tag}. Colunas ausentes: {missing}"
                logger.error(error_msg)
                raise ValueError(error_msg)
        
    def load_csv_to_raw(self, file_path, tag):
        """Converte CSV para JSON e insere na camada Raw em chunks."""
        logger.info(f"Iniciando carga Raw: {tag}", unixtime=self.unixtime)
        
        try:
            total_inserted = 0
            chunk_size = 10000
            
            # Lendo apenas o cabeçalho primeiro para validação rápida
            header_df = pd.read_csv(file_path, nrows=0)
            self._validate_schema(header_df, tag)

            # Lendo CSV via Pandas em Chunks para não estourar memória
            for df_chunk in pd.read_csv(file_path, chunksize=chunk_size):
                # Data Validation (Robustness): Remover linhas completamente vazias
                df_chunk = df_chunk.dropna(how='all')
                if df_chunk.empty:
                    continue

                # Convertendo cada linha para JSON string
                records_json = df_chunk.apply(lambda x: x.to_json(), axis=1).tolist()
                
                # Preparando dados para o ClickHouse
                data_to_insert = [
                    (self.unixtime, row_json, tag)
                    for row_json in records_json
                ]
                
                # Inserção em lote (Bulk Insert) do chunk
                self.client.insert(
                    'ingestion',
                    data_to_insert,
                    column_names=['unixtime', 'data', 'tag'],
                    database='northwind_raw'
                )
                total_inserted += len(data_to_insert)
            
            logger.info(f"Carga Raw finalizada: {tag}", count=total_inserted)
            return total_inserted

        except Exception as e:
            logger.error(f"Erro na carga Raw para {tag}: {str(e)}")
            raise
