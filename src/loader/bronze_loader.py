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

    def load_csv_to_raw(self, file_path, tag):
        """Converte CSV para JSON e insere na camada Raw."""
        logger.info(f"Iniciando carga Raw: {tag}", unixtime=self.unixtime)
        
        try:
            # Lendo CSV via Pandas
            df = pd.read_csv(file_path)
            
            # Convertendo cada linha para JSON string
            # record_json é uma lista de strings JSON
            records_json = df.apply(lambda x: x.to_json(), axis=1).tolist()
            
            # Preparando dados para o ClickHouse (unixtime, data, tag)
            data_to_insert = [
                (self.unixtime, row_json, tag)
                for row_json in records_json
            ]
            
            # Inserção em lote (Bulk Insert)
            self.client.insert(
                'ingestion',
                data_to_insert,
                column_names=['unixtime', 'data', 'tag'],
                database='northwind_raw'
            )
            
            logger.info(f"Carga Raw finalizada: {tag}", count=len(data_to_insert))
            return len(data_to_insert)

        except Exception as e:
            logger.error(f"Erro na carga Raw para {tag}: {str(e)}")
            raise
